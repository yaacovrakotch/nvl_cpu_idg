#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Do pre-checks during tprobot run

Usage:
tprobot.py PRE_CHECK ${{ github.event.label.name }}
tprobot.py MAIN ${{ github.event.pull_request.head.sha }}
tprobot.py REPO_INIT TP/23
tprobot.py UNUSED ${{ github.event.inputs.destination }}
tprobot.py MSBUILD ArrowLake_H68.sln
tprobot.py CHECK_ATOMIC
"""
import json
from setenv import ROOT_ENV      # must be first in the imports
from gadget.gizmo import Elapsed
from gadget.shell import SystemCall
from gadget.errors import exit1, ErrorCockpit, confirm, Check
from gadget.getgit import GitHub, GetCmd, GitCheckout
from gadget.files import File, check_and_del
from gadget.disk import Chdir
from gadget.pylog import log
from gadget.helperclass import IS_UT
from os.path import exists, dirname
from gadget.data_host import DataHost
from datetime import datetime
import subprocess
import os
import sys
import shutil
import re
import glob

# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class TPRobot:

    def __init__(self):
        self.prout = None     # assigned in get_pr_view()
        self.arg1 = None
        self.labels = set()   # assigned in get_pr_view()

    def main(self):
        """
        Main Entry point
        """
        sw = Elapsed()

        if len(sys.argv) == 1:
            exit1("Incorrect usage. Usage: tprobot.py MAIN ${{ github.event.label.name }}",
                  "Pls fix yml file")

        cmd = sys.argv[1]
        if cmd == "PRE_CHECK":
            self.arg1 = sys.argv[2]
            self.check_trig_label()
            print(f"PRE_CHECK is DONE in {sw}.")
            return 2

        elif cmd == "PRDESC":
            self.check_pr_desc()
            return 6

        elif cmd == "REPO_INIT":
            self.arg1 = sys.argv[2]
            # self.repo_init_check()
            self.repo_init_check2()
            print(f"REPO_INIT is DONE in {sw}.")
            return 3

        elif cmd == "MAIN":
            self.arg1 = sys.argv[2]
            self.main_bot()
            print(f"tprobot is DONE in {sw}.")
            return 1

        elif cmd == "UNUSED":
            self.arg1 = sys.argv[2]
            self.unused()
            print(f"UNUSED is DONE in {sw}.")
            return 4

        elif cmd == "MSBUILD":
            self.arg1 = sys.argv[2]
            self.msbuild()
            print(f"MSBUILD is DONE in {sw}.")
            return 5

        elif cmd == "SENDEMAILS":
            self.sendemails()
            print(f"SENDEMAILS is DONE in {sw}.")
            return 6

        elif cmd == "CHECK_ATOMIC":

            # ======= The first part is for dielet READY add

            # step1: Get the pr description and prno
            # Get PR number from command line argument if provided
            pr_number = sys.argv[2] if len(sys.argv) > 2 else None
            AtomicChange.prout, AtomicChange.prno = self.get_pr_view_closed(pr_number)
            if not AtomicChange.prout:
                print("Error: Could not retrieve closed PR information")
                return 1

            # step2: get the branch names of the dielets
            pr_list = AtomicChange.check_atomic_and_get_branch()
            if not pr_list:
                print("No atomic changes detected (no branch specifications found). Skipping version update.")
                return 6

            # step3: get the pr number of the dielets
            pr_numbers = AtomicChange.get_all_pr_numbers(pr_list)

            # step4: mark those ready
            AtomicChange.mark_prs_ready(pr_numbers)
            for repo, pr_number in pr_numbers.items():
                print(f"{repo}: PR number = {pr_number}")

            # ======= The second part is revision increment and saving
            json_base_path = r'I:\tpvalidation\engtools\tptools\mtl\infra\torch\atomic_version_db'

            # step1: load
            existing_data, current_version, file_path = AtomicChange.load_json_file(json_base_path)
            print(f"Current version: {current_version}")

            # step2: process revision
            data = AtomicChange.atomic_revision_final_workflow(pr_numbers, current_version, existing_data)

            # step3: load
            AtomicChange.save_json_file(file_path, data)

            return 6

        elif cmd == "PR_GATEKEEPER":
            self.PR_Gatekeeper()
            print(f"PR_Gatekeeper is done in {sw}.")
            return 7

        else:
            exit1(f'Unknown command: {cmd}', 'Run tprobot.py without any args for help. Pls fix yml file.')

    def main_bot(self):
        """Main routine for bot checkers"""
        self.check_sha()      # must be first bec of unittests

        self.get_pr_view()    # This needs checkout to be correct

        self.check_ready_label()

        self.set_automerge()

        self.check_reviewers()

        self.check_passed_label()

        self.check_one_ready_label_only()

        # self.check_approved()

        CheckedMarks().main(self.prout)

    def repo_init_check2(self):
        """
        Make sure repo checkout is good
        Second generation

        :return: exit_code, stdout, stderr
        """
        # delete these folders - they cause issues
        print('-i- Deleting UserCode folder...')
        check_and_del('UserCode', error=False)
        check_and_del('ctp-mtl')

        if exists('.git'):
            GitCheckout().main(self.arg1)

    def repo_init_check(self):
        """
        Make sure repo checkout is good
        Something for future if below sequence still does not work
        See how fast is it to do a "delete _work and copy _work"?
        If this is fast enough, say less than 30 secs, then do a "delete _work, git pull on _work_copy, cp _work_copy"
        :return: exit_code, stdout, stderr
        """
        # Show current status
        SystemCall(f'git status', disp=True).run_sout_serr()
        # Abort any merge
        SystemCall(f'git merge --abort', disp=True).run_sout_serr()
        # reset
        SystemCall(f'git reset --hard', disp=True).run_sout_serr()

        # delete these folders - they cause issues
        print('-i- Deleting UserCode folder...')
        check_and_del('UserCode', error=False)

        # delete all submodules
        for submodule in GitHub.get_submodules():
            print(f'-i- Deleting submodule {submodule}')
            check_and_del(submodule, error=False)

        # Remove extra files
        SystemCall(f'git restore .', disp=True).run_sout_serr()
        check_and_del('ctp-mtl')

        # Goto the main line
        _, sout, serr = SystemCall(f'git checkout {self.arg1}', disp=True).run_sout_serr()

        if 'error:' in serr:     # pragma: no cover   - for later, confirmed working
            print("CMD: Delete Modules/")
            check_and_del('Modules')
            check_and_del('Shared')
            SystemCall(f'git restore .', disp=True).run_sout_serr()

            # Goto the main line
            _, sout, serr = SystemCall(f'git checkout {self.arg1}', disp=False).run_sout_serr()    # too many lines

            print(f"CMD: git checkout {self.arg1}")
            print(f"==== Stdout: <intentionally not displayed - too long")
            print(f"==== Stderr:\n{serr}")
            confirm('error:' not in serr, 'There are still error in git checkout.', 'See log above')

            # Remove extra files
            SystemCall(f'git restore .', disp=True).run_sout_serr()
            SystemCall(f'git status', disp=True).run_sout_serr()

        # Git pull
        SystemCall(f'git pull', disp=True).run_sout_serr()
        # Shared submodule
        SystemCall(f'git submodule update --init --recursive --force', disp=True).run_sout_serr()
        # remove extra files
        SystemCall(f'git clean -f -d', disp=True).run_sout_serr()
        # Final status
        result = SystemCall(f'git status', disp=True).run_sout_serr()

        # do the check - error out
        ecode, sout, serr = result
        confirm('nothing to commit, working tree clean' in sout,
                '[git status] seems to be not clean',
                'Check above output. Expecting [working tree clean]')
        confirm(('Your branch is up to date with' in sout) or
                ('HEAD detached at' in sout),
                '[git status] shows that git pull did not work.',
                f'Check git pull above. (Expecting branch is up to date|HEAD detached at).')

        return result

    def set_automerge(self):
        """
        Set automerge and merge vs squash depending on PR type
        The systemcall will fail if DRAFT, but we need it for main-line check,
        thus, code is not checking whether pass or fail
        Let's see first if this will be abused (aka, module owner will use draft on integration tester)
        Assume folks will not abuse, as of Dec 10
        """
        if 'BUNDLE' in self.labels:
            cmd = "gh pr merge --auto --merge"
        elif GitHub.get_branch_name().startswith('TP/RC_'):    # RC branches
            cmd = "gh pr merge --auto --merge"
        else:
            cmd = "gh pr merge --auto --squash"

        _, out = SystemCall(GetCmd.exe(cmd)).run_outtxt()
        print(f"output of {cmd} ===============:")
        print(out)

    def check_sha(self):
        """Make sure sha is the same as the checkout sha"""
        pr_sha = self.arg1
        co_sha = self.get_checkout_sha()
        if pr_sha != co_sha:
            exit1(f'Only latest will be checked! This action/run is {pr_sha}, latest is {co_sha}',
                  'Just ignore this failure and look for the newest action/runner')

    def get_checkout_sha(self):
        """Return latest"""
        cmd = "git log -1 --format='%H'"
        _, out = SystemCall(cmd).run_outtxt()
        print(f"output of {cmd} ===============:")
        print(out)
        return out.strip()

    def get_pr_view(self):
        """Run gh pr view"""
        self.labels = GitHub.get_labels()
        self.prout = GitHub.get_pr_view_output()

    def get_pr_view_closed(self, pr_number):
        """
        Get PR information for a closed/merged PR using the PR number.

        Args:
            pr_number: PR number to query

        Returns:
            tuple: (prout, prno) - PR description/body and PR number
        """
        try:
            # Use provided PR number directly
            cmd = ['gh', 'pr', 'view', str(pr_number), '--json', 'number,body', '--jq', '.']
            output = SystemCall(cmd, disp=True).run_outonly()

            if not output.strip():
                print(f"No PR found for number: {pr_number}")
                return None, None

            # Parse JSON output
            pr_data = json.loads(output)
            pr_body = pr_data.get('body', '')
            print(f"Found PR #{pr_number}")
            return pr_body, str(pr_number)

        except Exception as e:
            print(f"Error getting closed PR info: {e}")
            return None, None

    def check_trig_label(self):
        """
        Make sure checker is triggered by READY label only
        Everytime someone adds a label, the trigger is set
        This assumes READY label is the last one
        Automatic label are not triggers - This is expected
        This does not need checkout
        """
        if self.arg1 in ('BUNDLE', 'READY', 'AAREADY', 'I_AM_TPI_READY', 'I_AM_TPI_Skip_Bot'):
            return    # success
        exit1(f"This github action/run is not a READY trigger. Trigger is: {self.arg1}",
              'Just ignore this failure and look for the newest action/runner with READY')

    def check_approved(self):
        """
        Fail right away, unless MAROON_APPROVED label exist
        """
        if 'MAROON_APPROVED' in self.labels:
            return 1

        exit1("We have disabled PR merging to mainline for now (8am Jul 9 meeting direction). "
              "Why? We want tpbot to get to true Bin1 first. Once we have Bin1 in our mainlines then "
              "We enable normal tpbot operation.",
              "For the meantime, continue to confirm your branch is clean using latest main line thru your "
              "engg validations.")

    def check_ready_label(self):
        """Make sure READY label exist in PR"""
        if exists('TPConfig/RC_Testprogram.trigger'):
            log.info(f'-i- check_rc: labels: {self.labels}')
            if 'I_AM_TPI_READY' not in self.labels:
                exit1("TPI READY label does not exist.",
                      'This TP is a Release Candidate (TPConfig/RC_Testprogram.trigger). '
                      'Only TPI can add ready label for RC program.')

        if {'BUNDLE', 'READY', 'AAREADY', 'I_AM_TPI_READY', 'I_AM_TPI_Skip_Bot', 'PASSED_Si'} & self.labels:
            return     # success
        exit1("PR does not have READY label.",
              "Need READY label for tprobot to run")

    def check_one_ready_label_only(self):
        """
        Make sure there is only one ready label.
        Reason: If there are two ready labels, then there are two tpbot jobs, one of them pass, and the 2nd fail and PR
        will not be merged. This will trigger a fail condition right away.
        """
        ordered_ready_labels = ['READY', 'AAREADY', 'I_AM_TPI_READY']
        result = set(ordered_ready_labels) & self.labels
        if len(result) > 1:

            # remove one label only, assuming one label per job
            for label in ordered_ready_labels:
                if label in self.labels:
                    GitHub.remove_labels([label])
                    break
            else:     # pragma: no cover
                raise ErrorCockpit("Unreachable code")

            exit1("PR has multiple READY labels, each label added will trigger a run. Now removing extra READY label.",
                  "Just ignore this failure and look for the newest action/runner. ")

    def check_passed_label(self):
        """
        Make sure PASSED_Chk label exist in PR
        For Bundle, we don't need PASSED_Chk, it's needed for the PR to be merged automatically anyway.
        This way, TPI does not have to add additional label.
        """
        # offline check
        if os.environ.get('OFFLINE_REQUIRE') and 'PASSED_OFFLINE' not in self.labels:
            exit1("PR does not have PASSED_OFFLINE label. Offline must pass first before TPBot can run.",
                  ("Wait for offline to pass, then click on 'Re-run Jobs' button. "
                   "Ideally, add READY label only when offline pass. "
                   "If you see this error and Offline already passed, then "
                   "remove READY label -> add PASSED_OFFLINE label first -> add READY label next"))

        # traditional check
        if 'PASSED_Chk' in self.labels or 'BUNDLE' in self.labels:
            return 1    # success

        passed_labels = []
        if os.environ.get('TARGETBOM'):       # specific BOM
            # NEW Mode check, one bom at a time
            bom = os.environ['TARGETBOM']
            bom = bom.split('_')[-1]
            label = f'PASSED_{bom}'
            passed_labels.append(label)

        else:
            # sequential single tpbot check
            cwd = os.getcwd()
            log.info(f'-i- cwd: {cwd}')
            env_files = glob.glob('POR_TP/*/EnvironmentFile.env')
            for env_file in env_files:
                bom = os.path.basename(os.path.dirname(env_file))
                bom = bom.split('_')[-1]
                label = f'PASSED_{bom}'
                passed_labels.append(label)

        if passed_labels:
            if set(passed_labels).issubset(self.labels):
                return 2
            exit1(f"PR does not have {passed_labels} label. Checkers must pass first before TPBot can run.",
                  ("Wait for checkers to pass, then click on 'Re-run Jobs' button. "
                   "Ideally, add READY label only when checkers pass. "
                   "If you see this error and Checkers already passed, click on 'Re-run Jobs' button in "
                   "Checkers so label is created."))

        self.remove_ready()
        exit1("PR does not have PASSED_* label. Checkers must pass first before TPBot can run.",
              ("Wait for checkers to pass, then click on 'Re-run Jobs' button. "
               "Ideally, add READY label only when checkers pass. "
               "If you see this error and Checkers already passed, click on 'Re-run Jobs' button in "
               "Checkers so label is created."))

    def check_pr_desc(self):
        """Wrapper for checker's checks"""
        self.get_pr_view()

        # PR description checks
        self.check_pr_why()
        self.check_pr_checkboxes()

        self.add_bomcnt()

    def check_pr_why(self):
        """Error if Reason for PR description was not filled up"""
        found = False
        foundlines = []
        valid_template = False
        rheader = re.compile(r'^#+\s+(.*)$')
        instruction = None
        for line in self.prout.split('\n'):
            # remove header chars
            oline = line
            res = rheader.search(line)
            if res:
                line = res.group(1)

            if line == '---':
                continue

            if line.startswith('_Provide a'):
                instruction = line
                continue   # Ignore this line - comment only

            # start marker
            if '### Why is this PR needed?' in oline:
                found = True
                valid_template = True
                continue

            if 'Why is this PR needed?' in line:
                found = True
                valid_template = True
                line = line.replace('Why is this PR needed?', '')

            # end marker
            if ('Who/Where is the source' in line) or oline.strip().startswith('###'):
                found = False

            if found and line.strip():
                foundlines.append(line.strip())

        if not valid_template:
            exit1("PR description seems to be empty. This indicates something is wrong with the runner.",
                  "Either retrigger (try again) or ask help from Infra Channel (gh command is not giving PR description).")

        # count the total length
        not_empty = 0
        for line in foundlines:
            not_empty += len(line)

        if not_empty == 0:
            exit1("Reason why PR is needed is not provided.",
                  "Pls write proper reason why this PR is needed. "
                  "If you are asked in a meeting, why is this PR needed, "
                  "then write down what you are about to say.")

        if not_empty < 10:
            exit1(f"Reason why PR is needed is not good enough: {foundlines}",
                  "Pls provided better reason why this PR is needed. "
                  "If you are asked in a meeting, why is this PR needed, "
                  "then write down what you are about to say.")

        if instruction:
            exit1(f"The line '{instruction}' is in the Why block of PR description.",
                  "Pls remove this line, this is just an instruction.")

        print('PR Reason found:')
        for line in foundlines:
            print(line)

        # Return the found lines joined as a single string
        return '\n'.join(foundlines)

    @classmethod
    def sections(cls):
        """Returns dictionary of sections required for checkboxes"""
        sections = '''
### What type of PR is this
### Who/Where is the source of this PR change
### Does this PR come with a common PR
### Which Bins are affected
### Socket(s) affected by this PR
### Which package(s) are affected
### VALIDATION INFO
### VALIDATION Temperature
'''
        return {x: None for x in sections.split('\n') if x}

    def check_pr_checkboxes(self):
        """
        Checks each section that at least one checkbox is checked
        """

        # {section: 'first choice string'|None|<emptystring>}
        secmap = self.sections()
        head = None
        rcheckbox = re.compile(r'^\s*-\s*\[')
        rvalidcheckbox = re.compile(r'^-\s+\[([ xX])\]\s+(.*)$')
        error = []

        for line in self.prout.split('\n'):

            # new section line
            if line.startswith(('###', '---')):

                for head in secmap:
                    if line.startswith(head):
                        secmap[head] = ''      # found
                        break
                else:
                    head = None

            # checkbox
            if head and rcheckbox.search(line):
                res = rvalidcheckbox.search(line)
                if res:
                    if res.group(1).strip():     # x or X value
                        secmap[head] = res.group(2)
                        if line.replace('_', '').strip().endswith(':'):
                            error.append(f'Pls fill in the blank for line "{line}"')
                else:
                    secmap[head] = 'assume filled'
                    error.append(f'Line "{line}" is not valid checkbox syntax. It must start with "- [x]" or "- [ ]"')

        # check that each section has at least one checkbox (and that it exist)
        for head in secmap:
            if secmap[head] == '':
                error.append(f'Section "{head}" is not filled. Pls answer this section.')
            if secmap[head] is None:
                error.append(f'"{head}" Section is not found. Pls copy template from goto.intel.com/nvl.pr.template')

        if error:
            final = [f'   {idx + 1}. {line}' for idx, line in enumerate(error)]
            exit1('PR description has errors. See below:\n%s' % '\n'.join(final),
                  'Pls update PR description and fix above errors and re-trigger the checkers.')

    def add_bomcnt(self):
        """Add BOMCNT<n> label. This is needed for auto-ready-add cron"""
        # get the count
        files = glob.glob(f'POR_TP/*/EnvironmentFile.env')
        confirm(files, f'No POR_TP/*/EnvironmentFile.env found in folder: {os.getcwd()}', 'Is checkout successful?')
        label = f'BOMCNT{len(files)}'

        # Add the label if it does not exist
        if label not in self.labels:
            GitHub.add_labels({label}, check=True)

    def check_reviewers(self):
        """Error if no reviewers"""
        # special option for developer & testing - no review needed
        if 'I_AM_TPD_NR' in self.labels:
            return

        # 2nd pass, look for reviewers
        for line in self.prout.split('\n'):
            if line.startswith('reviewers:'):
                if 'Approved' not in line:
                    self.remove_ready()
                    exit1("PR has no approvers yet!",
                          "Need at least one approver for the PR")

    def remove_ready(self):
        """Remove ready label"""
        print("-i- Removing Ready label")
        GitHub.remove_labels('READY AAREADY I_AM_TPI_READY'.split())

    def unused(self):
        """Independent routine: Call unused script from MIT"""
        with Chdir(self.arg1):
            env = glob.glob('*_TP/*/EnvironmentFile.env')
            if not env:
                print(f"No Env found in {self.arg1}: nothing to do")
                return
            confirm(len(env) == 1, f'Found: {env}', 'Expecting one EnvironmentFile.env only.')
            plist = glob.glob('*_TP/*/PLIST_ALL*.plist.xml')
            confirm(len(plist) == 1, f'Found: {plist}', 'Expecting one .plist.xml only.')

            cmd = (f'{sys.executable} '
                   'I:/tpvalidation/engtools/tptools/mtl/tools/github-actions/Actions/UnusedContentFinder/main.py '
                   'unused-content '
                   f'--plistXmlFile {plist[0]} '
                   f'--environmentalFile {env[0]} '
                   '--environmentPlistVariableName HDST_PLIST_PATH '
                   f'--tplDirectory ./ '
                   '--environmentPatVariableName HDST_PAT_PATH '
                   '--alephFilesVariable ALEPH_FILES '
                   f'--outputDirectory {dirname(env[0])}/Reports/unused-content')
            SystemCall(cmd, disp=True).run_sout_serr()

    def msbuild(self, choices=(r'C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\amd64\MSBuild.exe',
                               r'C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\amd64\MSBuild.exe')):
        """Independent routine: Call msbuild"""
        # Determine msbuild executable first
        for msbuild_exe in choices:
            if exists(msbuild_exe):
                break
        else:
            exit1(f'[{choices[0]}] does not exist', 'Where is MSBuild.exe?')

        # run it
        slnfile = self.arg1
        cmd = ([msbuild_exe, slnfile] +
               "-m -verbosity:normal -nologo -restore -p:Configuration=Release".split() +
               ["-p:Platform=Any CPU"])
        SystemCall(cmd, disp=True).run_sout_serr()

    def PR_Gatekeeper(self):
        """Independent routine: Call PR_Gatekeeper script from GenAI"""
        from genai.qagent_pr_gatekeeper import PR_Gatekeeper

        Check.min_python_version(3, 10)
        # Convert to single string for LLM
        # Call Gate Keeper
        self.get_pr_view()
        pr_description = self.check_pr_why()
        gatekeeper = PR_Gatekeeper(pr_description)
        result, llm_response = gatekeeper.main()
        if result == 1:
            log_result = "Yes"
        else:
            log_result = "No"

        # Log the data to an output file
        path = 'I:/tpvalidation/engtools/tptools/mtl/logs/checkers/why.log'
        if exists(path) and not IS_UT:        # pragma: no cover
            text = f'{log_result}: {pr_description}'
            File(path).logprint(text)

        # if result != 1:
        #     exit1(f"PR_Gatekeeper: PR description is invalid: {pr_description}",
        #           f"Pls update the Why is this PR needed section as per suggestion from the agent - {llm_response}")

    def sendemails(self):
        """
        This function is for sending out email to the recipient list defined in environment variable TO_LIST.
        Rely on the user inputs from yml file to determine the subject and body of the email.
        The email is sent out using DataHost central sendmail function.
        Usage:: py tprobot.py SENDEMAILS
        """
        if 'TO_LIST' not in os.environ:          # this is only defined for torch workflow checkout yml
            log.info('-i- Workflow auto-notification email function is disabled TO_LIST is undefined.')
            return

        # Get the recipient list from environment variable. It should be a comma-separated string of email addresses.
        to_list = os.environ['TO_LIST']

        # Get workflow result from environment variable
        workflow_result = os.environ.get('WORKFLOW_RESULT', 'Unknown')

        # Build GitHub Actions workflow URL
        github_server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
        github_repo = os.environ.get('GITHUB_REPOSITORY', '')
        run_id = os.environ.get('GITHUB_RUN_ID', '')
        workflow_url = f"{github_server}/{github_repo}/actions/runs/{run_id}"

        # Set current time and workflow pass or fail result in subject.
        current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        subject = f'[NVL] Torch Pre Prod Workflow Check - {workflow_result} {current_time}'

        if workflow_result == 'Fail':
            sentence = 'This email is to inform that Torch Pre-Prod version FAILED with NVL automation workflow.\n'
            sentence += '\nPlease help address the failure before Torch Pre-Prod version release to production.\n'
        else:
            sentence = 'This email is to inform that Torch Pre-Prod version passed NVL automation workflow checks.\n'

        body = f'''
Hello NVL Repo Owners and Torch Team,

{sentence}
Workflow Run Details: {workflow_url}

Thanks!

***This is an auto-generated email***
***Please Do Not Reply***
'''
        # Send email using DataHost central sendmail function.
        DataHost().central('sendmail', (to_list, subject, body), check=True)
        log.info(f'-i- Email sent to {to_list}')


class CheckedMarks:

    def __init__(self):
        self.secmap = TPRobot.sections()

    def main(self, pr_desc):
        """
        Make sure all requirements (aka, check boxes) are checked.
        See https://hsdes.intel.com/appstore/article/#/22018448928
        on usage.

        Note: the checkbox has to be in the main description of PR

        This will raise exception if check box is not checked

        :return:
        """
        if not pr_desc:
            return -1    # Do nothing

        gatelist = []
        cnt = 0
        for item in self.check_items(pr_desc):
            if item.strip() in ('Novalake U', 'Novalake UL'):     # indicator of old PR template (Nov 2 or earlier)
                cnt += 1
            gatelist.append(f'   - [ ] {item}')

        if cnt == 2:
            return 2      # special case: old PR, do not error out

        if gatelist:
            item = '\n'.join(gatelist)
            exit1(f"Required checklist items ({len(gatelist)}) below is not yet completed:\n{item}",
                  "TPBot cannot proceed because of above.")
        return 1

    def check_items(self, pr_desc):
        """
        Iterator: Return item(s) that are unchecked

        PR description sections that are part of template are ignored.
        Unchecked boxes should only come from sections that are not part of template.

        :param pr_desc: PR description text
        :return: item
        """
        robj = re.compile(r'[\-\*]\s+\[ \]\s+(.*)')     # unchecked box
        found = True
        for line in pr_desc.split('\n'):

            # new section line
            if line.startswith(('###', '---')):

                for head in self.secmap:
                    if line.startswith(head):
                        found = False
                        break
                else:
                    found = True

            if found:
                line = line.strip()
                res = robj.search(line)
                if res:
                    yield res.group(1)


class AtomicChange:
    """
    Atomic version management system for multi-repository PR tracking.

    This class manages atomic version numbers across multiple Novalake repositories (dielet repos:
    nvl.hub, nvl.pcd, nvl.cpu, nvl.gcd and common repo: nvl.common). It tracks versions with BOM
    (Bill of Materials) flags, increments versions based on affected packages, and maintains
    version history in branch-specific JSON files.

    Key Features:
    - Retrieves PR numbers from multiple repositories using GitHub CLI
    - Parses PR descriptions to identify affected BOM packages (11 Novalake packages)
    - Increments version numbers (minor: 1.9→1.10, or major: 1.22→2.0 when all packages affected)
    - Generates version strings with BOM flags (e.g., "1.4.11000000001")
    - Stores version history in branch-specific JSON files with automatic backup
    - Supports environment-based branching via BASE_REF (main.json, main_nvl.json, etc.)
    - PR state management (marking PRs as ready/draft)

    Version Format: "major.minor.BOMflags"
    - major.minor: Numeric version (e.g., 1.4)
    - BOMflags: 11-character string of 1s/0s indicating which packages are affected

    JSON Structure:
    {
        "latest": "1.4.11000000001",
        "nvl.common": {"120": ["1.4.11000000001"]},
        "nvl.pcd": {"1239": ["1.4.11000000001"]},
        "nvl.hub": {"1129": ["1.4.11000000001"]},
        "nvl.cpu": {"0000": ["1.4.11000000001"]},
        "nvl.gcd": {"2139": ["1.4.11000000001"]}
    }

    Usage:
        See main(CHECK_ATOMIC) for "ATOMIC USAGE"
    """

    # BOM sequence and display name mapping - SINGLE SOURCE OF TRUTH
    # Order matters! This corresponds to the bit positions in BOM flags
    # Only add new BOMs at the bottom, do not add new BOM in middle or front
    # The first element is the exact-name in the PR description check boxes under 'Which package(s) are affected?'
    # The second element is the short BOM name that will show up in the cci webpage

    BOM_MAPPING = [
        ("Novalake S 28C", "NVL_S28C"),
        ("Novalake S 52C", "NVL_S52C"),
        ("Novalake S 28C BLLC", "NVL_S28C_BLLC"),
        ("Novalake S 16C", "NVL_S16C"),
        ("Novalake UL 6C", "NVL_UL6C"),
        ("Novalake U 8C", "NVL_U8C"),
        ("Novalake H 16C", "NVL_H16C"),
        ("Novalake P 16C", "NVL_P16C"),
        ("Novalake HX 28C", "NVL_HX28C"),
        ("Novalake AX 28C", "NVL_AX28C"),
        ("Novalake AX 16C", "NVL_AX16C"),
        ("Dunlow S 28C", "DNL_S28C")
    ]

    # Class variables to store closed PR information
    prout = None
    prno = None

    @classmethod
    def check_atomic_and_get_branch(cls):
        """
        iterate to all repos, get the dielet branch names, if exist in PR desc
        Uses cls.prout (stored PR description) for closed PRs
        :return: dict {repo: branch}
        """
        from main.nvl_buildtp import BuildCommon

        # Parse PR description for branch patterns like "nvl.cpu BRANCH: mybranch"
        pr_list = {repo: branch for repo, branch in re.findall(r'^\s*(\S+)\s+BRANCH:\s+(\S+)', cls.prout, re.MULTILINE)
                   if repo in BuildCommon.repomap}

        for repo, branch in pr_list.items():  # print repo and branch
            print(f"{repo}: {branch}")

        return pr_list

    @classmethod
    def get_all_pr_numbers(cls, pr_list: dict):
        """
        get PR numbers from branch names
        :param pr_list: dict {repo: branch}
        :return: {repo: prnumber_string}
        """
        pr_numbers = {}
        for repo, branch in pr_list.items():
            cmd = ['gh', 'pr', 'view', '--repo', f'intel-restricted/{repo}', '--json', 'number', '--jq', '.number', branch]
            pr_number = SystemCall(cmd, disp=True).run_outonly()
            if pr_number.strip().isdigit():
                pr_numbers[repo] = pr_number.strip()
            else:
                pr_numbers[repo] = None
        return pr_numbers

    @classmethod
    def mark_prs_ready(cls, pr_numbers: dict):
        """
        Sends the gh command to mark the PR's ready given dict
        :param pr_numbers: {branch: prnumber}
        :return: unittest hook count of fails
        """
        ctr = 0
        for repo, pr_number in pr_numbers.items():
            if pr_number:  # Only proceed if a PR number was found
                cmd = ['gh', 'pr', 'ready', pr_number, '--repo', f'intel-restricted/{repo}']
                exitcode = SystemCall(cmd).run(disp=True)
                if exitcode:   # any non-zero value
                    print(f"Failed to mark PR #{pr_number} in {repo} as ready")
                    ctr += 1
                else:
                    print(f"Marked PR #{pr_number} in {repo} as ready for review.")

        return ctr

    @classmethod
    def load_json_file(cls, file_path):
        """
        Load existing version data from JSON file and extract current version.

        Args:
            file_path (str): Directory path to construct branch-specific JSON filename

        Returns:
            tuple: (existing_data dict, current_version string, file_path string)
        """
        # Construct branch-specific filename
        branch_name = os.environ.get('BASE_REF', 'main')
        file_path = f'{file_path}/{branch_name}.json'

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
            print(f"Loaded data from {file_path}")
            current_version = existing_data['latest']
        else:
            print(f"JSON file not found: {file_path}. Creating default data.")
            existing_data = {
                'latest': '1.0',
                'nvl.hub': {"1": ["1.0"]},
                'nvl.cpu': {"1": ["1.0"]},
                'nvl.pcd': {"1": ["1.0"]},
                'nvl.gcd': {"1": ["1.0"]},
                'nvl.common': {"1": ["1.0"]},
            }
            current_version = '1.0'

        return existing_data, current_version, file_path

    @classmethod
    def check_affected_bom(cls):
        """
        Check which BOMs are affected in the PR description from the current repo.

        Returns:
            tuple: (bom_flags_string, is_all_packages)
                - bom_flags_string: String of '1's and '0's indicating affected BOMs
                - is_all_packages: Boolean indicating if "All packages" is checked
        """
        # Get BOM sequence from class-level mapping
        bom_sequence = [full_name for full_name, _ in cls.BOM_MAPPING]

        # Get PR description using GitHub CLI for the current branch
        pr_description = cls.prout

        # Check if "All packages" is marked
        is_all_packages = bool(re.search(r'\[[xX]\]\s*All packages', pr_description))

        # If "All packages" is checked, return all 1's
        if is_all_packages:
            return ('1' * len(bom_sequence), True)

        # Initialize result string
        bom_flags = []

        # Check each BOM in sequence
        for bom in bom_sequence:
            # Look for the pattern [x] or [X] followed by the BOM name
            if re.search(r'\[[xX]\]\s*' + re.escape(bom), pr_description):
                bom_flags.append('1')
            else:
                bom_flags.append('0')

        # Check if all individual BOMs are marked (all flags are '1')
        bom_flags_str = ''.join(bom_flags)
        all_individually_marked = (bom_flags_str == '1' * len(bom_sequence))

        return (bom_flags_str, all_individually_marked)

    @classmethod
    def uprev_atomic_rev(cls, current_version, is_all_packages=False):
        """
        Increment the version number.

        Args:
            current_version: Can be float (e.g., 1.3) or string with BOM flags (e.g., "1.3.11000000001")
            is_all_packages: If True, increment major version; otherwise increment minor version

        Returns:
            str: New version number as string (e.g., "1.4" or "2.0")
        """
        # If it's a string with BOM flags, extract just the version number
        if isinstance(current_version, str):
            # Split by '.' and take first two parts (major.minor)
            parts = current_version.split('.')
        else:
            # It's a float or int
            version_str = str(current_version)
            parts = version_str.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0

        # Increment major or minor version based on is_all_packages
        if is_all_packages:
            major += 1
            minor = 0  # Reset minor version when major is incremented
        else:
            minor += 1

        new_version = f"{major}.{minor}"

        print(f'generated version: {new_version}')
        return new_version

    @classmethod
    def update_atomic_dict(cls, pr_numbers: dict, new_version, bom_flags: str, existing_data: dict = None, common_repo='nvl.common'):
        """
        Store version against each PR in a dictionary format (no file I/O).
        Uses the provided version directly without incrementing.

        Args:
            pr_numbers (dict): Dictionary of dielet repositories and their PR numbers.
            new_version: The new version to use (float like 1.4).
            bom_flags (str): String of '1's and '0's indicating affected BOMs.
            existing_data (dict): Optional existing version data dictionary. If None, starts fresh.
            common_repo (str): The common repository name (default: 'nvl.common')

        Returns:
            dict: Updated dictionary with version data.
        """

        # Create version string: "major.minor.BOMflags" (e.g., "1.4.11000000001")
        # new_version is already a string from uprev_atomic_rev with correct major/minor increment
        version_with_bom = f"{new_version}.{bom_flags}"

        # Initialize the version data structure
        version_data = {
            "latest": version_with_bom
        }

        # Get current PR number for the common repo
        current_pr = cls.prno
        version_data[common_repo] = {current_pr: [version_with_bom]}

        # Update the version data with PR numbers and versions for dielet repos
        for repo, pr_number in pr_numbers.items():
            if repo not in version_data:
                version_data[repo] = {}

            if pr_number not in version_data[repo]:
                version_data[repo][pr_number] = []

            version_data[repo][pr_number].append(version_with_bom)

        # Update the latest version
        version_data["latest"] = version_with_bom

        # Merge the new version data with the existing data
        for repo, pr_data in version_data.items():
            if repo == "latest":
                existing_data["latest"] = version_data["latest"]
                continue

            if repo not in existing_data:
                existing_data[repo] = {}

            for pr_number, versions in pr_data.items():
                if pr_number not in existing_data[repo]:
                    existing_data[repo][pr_number] = []

                # Append new versions, avoiding duplicates
                for version in versions:
                    if version not in existing_data[repo][pr_number]:
                        existing_data[repo][pr_number].append(version)

        # Handle missing repositories (not in current pr_numbers input)
        # Append new version to their latest existing PR
        for repo in existing_data:
            if repo != "latest" and repo not in pr_numbers:
                # Get the latest (last) PR number for this repo
                latest_pr = list(existing_data[repo].keys())[-1]
                # Append the new version to this PR number
                if version_with_bom not in existing_data[repo][latest_pr]:
                    existing_data[repo][latest_pr].append(version_with_bom)

        return existing_data

    @classmethod
    def atomic_revision_final_workflow(cls, pr_numbers: dict, current_version, existing_data: dict = None):
        """
        Complete workflow: Check BOM flags, increment version appropriately, and update PR data.

        Args:
            pr_numbers (dict): Dictionary of repositories and their PR numbers.
            current_version: Current version (float or string with BOM flags).
            existing_data (dict): Optional existing version data dictionary.

        Returns:
            dict: Updated dictionary with version data.
        """
        # Check BOM flags first to determine if "All packages" is selected
        bom_flags, is_all_packages = cls.check_affected_bom()

        # Increment version based on whether all packages are affected
        new_version = cls.uprev_atomic_rev(current_version, is_all_packages)

        # Update PR data with new version
        return cls.update_atomic_dict(pr_numbers, new_version, bom_flags, existing_data)

    @classmethod
    def save_json_file(cls, file_path, data):
        """
        Save version data to JSON file with proper formatting.
        Creates a backup of existing file as .json.previous before saving.

        Args:
            file_path (str): Full path to the JSON file (branch-specific filename already constructed)
            data (dict): Version data to save
        """
        try:
            # Backup existing file if it exists
            if os.path.exists(file_path):
                backup_path = f'{file_path}.previous'
                shutil.copy2(file_path, backup_path)
                print(f"Backup created: {backup_path}")

            # Save JSON with proper formatting
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

            print(f"Version data saved to {file_path}")
        except Exception as e:
            print(f"Error saving JSON file: {e}")


if __name__ == '__main__':  # pragma: no cover
    TPRobot().main()
