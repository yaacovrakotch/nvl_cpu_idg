#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from unittest.mock import patch
from setenv_unittest import UT_DIR, ROOT_ENV, UT_DIR_REPO    # must be first import for unittests
from gadget.errors import ErrorUser, Check
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.shell import IS_UNIX, IS_WIN
from gadget.gizmo import MockVar, with_
from gadget.ut import Mock
from gadget.helperclass import CaptureStdoutLog
from gadget.errors import Check
from main.tprobot import *
from os.path import join, dirname, abspath
import main.tprobot as tprobot
import genai.qagent_pr_gatekeeper
from pprint import pprint
import tempfile
import json


def is_lower_310():
    """Returns True if python version is lower than 3.10"""
    try:
        Check.min_python_version(3, 10)
    except Exception:
        return True

    return False


class TestTpRobot(TestCase):

    def test_no_output(self):
        out = ''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):  # assume correct sha from git
                with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with CaptureStdoutLog() as p:
                        with self.assertRaises(SystemExit):
                            TPRobot().main()

        print(p.getvalue())
        self.assertIn('PR does not have READY label', p.getvalue())

    def test_noready(self):
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN, XREADY
author: jdr
labels: ARR_ATOM_CXX, ARR_ATOM_L2CXX
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with CaptureStdoutLog() as p, MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with self.assertRaises(SystemExit):
                        TPRobot().main()

        print(p.getvalue())
        self.assertIn('PR does not have READY label', p.getvalue())

    @with_(MockVar, TPRobot, 'check_approved', Mock())
    @with_(MockVar, GitHub, 'get_branch_name', Mock(return_value='TPI/jdr'))
    def test_rc_trigger(self):
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, AAREADY, PASSED_Chk
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with TempDir(name=True, chdir=True) as tdir:
            File(f'TPConfig/RC_Testprogram.trigger').touch(mkdir=True)

            # Fail case
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
                with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                    with CaptureStdoutLog() as p, MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                        with self.assertRaises(SystemExit):
                            TPRobot().main()

            self.assertIn('TPI READY label does not exist', p.getvalue())

            # Pass case
            GitHub.clear()
            out1 = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, I_AM_TPI_READY, PASSED_Chk
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out1))):
                with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                    with CaptureStdoutLog() as p, MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                        TPRobot().main()

    @with_(MockVar, GitHub, 'get_branch_name', Mock(return_value='TPI/jdr'))
    def test_two_ready(self):
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, AAREADY, PASSED_Chk
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with CaptureStdoutLog() as p, MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with self.assertRaises(SystemExit):
                        TPRobot().main()

        self.assertIn('PR has multiple READY labels', p.getvalue())

        # unittest =========
        cmd_list = []

        def fake(slf, *kwargs):
            cmd_list.append(' '.join(slf.cmd))
            return 0, out

        with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
            with MockVar(SystemCall, "run_outtxt", fake):
                tpr = TPRobot()

                # Case1 - Two ready
                cmd_list = []
                tpr.labels = {'AAREADY', 'I_AM_TPI_READY'}
                with self.assertRaises(SystemExit):
                    tpr.check_one_ready_label_only()
                self.assertEqual(cmd_list, ['gh pr view', 'gh pr edit --remove-label AAREADY'])

                # Case2 - one ready
                cmd_list = []
                tpr.labels = {'READY'}
                tpr.check_one_ready_label_only()
                self.assertEqual(cmd_list, [])

                # Case3 - skip_bot, remove one only
                cmd_list = []
                tpr.labels = {'AAREADY', 'READY', 'I_AM_TPI_Skip_Bot'}
                with self.assertRaises(SystemExit):
                    tpr.check_one_ready_label_only()
                self.assertEqual(cmd_list, ['gh pr view', 'gh pr edit --remove-label READY'])

    @with_(MockVar, TPRobot, 'check_approved', Mock())
    @with_(MockVar, GitHub, 'get_branch_name', Mock(return_value='TPI/jdr'))
    def test_pass(self):
        # good template to use
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, ARR_ATOM_L2CXX, PASSED_Chk
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with CaptureStdoutLog() as p:
                        self.assertEqual(TPRobot().main(), 1)

        self.assertIn('tprobot is DONE', p.getvalue())
        self.assertIn('gh pr merge --auto --squash', p.getvalue())   # default

        # I_AM_TPI_READY
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: I_AM_TPI_READY, PASSED_Chk
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with CaptureStdoutLog() as p:
                        self.assertEqual(TPRobot().main(), 1)

        self.assertIn('tprobot is DONE', p.getvalue())

    @with_(MockVar, GitHub, 'get_branch_name', Mock(return_value='TPI/jdr'))
    def test_no_passchk(self):
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, ARR_ATOM_L2CXX
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with CaptureStdoutLog() as p:
                        with self.assertRaises(SystemExit):
                            TPRobot().main()
        print(p.getvalue())
        self.assertIn('PR does not have PASSED_* label', p.getvalue())

    @with_(MockVar, GitHub, 'get_branch_name', Mock(return_value='TPI/jdr'))
    def test_no_passoffline(self):
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, ARR_ATOM_L2CXX, PASSED_Chk
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))), \
                MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')), \
                MockVar(sys, "argv", 'a.py MAIN beef'.split()), \
                MockVar(os.environ, 'OFFLINE_REQUIRE', 'True'), \
                CaptureStdoutLog() as p:
            with self.assertRaises(SystemExit):
                TPRobot().main()
        print(p.getvalue())
        self.assertIn('PR does not have PASSED_OFFLINE label', p.getvalue())

    @with_(TempDir, chdir=True)
    def test_check_pr_desc(self):
        obj = TPRobot()
        with MockVar(sys, "argv", 'a.py PRDESC'.split()), \
                MockVar(GitHub, 'add_labels', Mock()), \
                MockVar(obj, 'check_pr_checkboxes', Mock()), \
                MockVar(obj, 'get_pr_view', Mock()):

            # empty pr description (or template was deleted)
            obj.prout = ''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            expect = '''
==================================================
Error:      PR description seems to be empty. This indicates something is wrong with the runner.
Suggestion: Either retrigger (try again) or ask help from Infra Channel (gh command is not giving PR description).
==================================================
'''
            self.assertTextEqual(p.getvalue(), expect)

            # empty why
            obj.prout = '''Why is this PR needed?

Who/Where is the source of the request of this PR change?
'''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            expect_none = '''
==================================================
Error:      Reason why PR is needed is not provided.
Suggestion: Pls write proper reason why this PR is needed. If you are asked in a meeting, why is this PR needed, then write down what you are about to say.
==================================================
'''
            self.assertTextEqual(p.getvalue(), expect_none)

            # too small reason
            obj.prout = '''Why is this PR needed? blah

Who/Where is the source of the request of this PR change?
'''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            expect = '''
==================================================
Error:      Reason why PR is needed is not good enough: ['blah']
Suggestion: Pls provided better reason why this PR is needed. If you are asked in a meeting, why is this PR needed, then write down what you are about to say.
==================================================
'''
            self.assertTextEqual(p.getvalue(), expect)

            # valid reason1
            File('POR_TP/BOM1/EnvironmentFile.env').touch(mkdir=True)
            obj.prout = '''Why is this PR needed? Because we wanted TP to pass
Also this one

Who/Where is the source of the request of this PR change?
'''
            with CaptureStdoutLog() as p:
                obj.main()
            expect = '''
PR Reason found:
Because we wanted TP to pass
Also this one

'''
            self.assertTextEqual(p.getvalue(), expect)

            # New format - fail
            obj.prout = '''
## Why is this PR needed?

_Provide a concise summary explaining the motivation for this change._

---

## Who/Where is the source of the request of this PR change?

_Specify HSD URL, GitHub issue number (e.g., #1234), or if coming from TPTracker, CTP, etc._
'''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            self.assertTextEqual(p.getvalue(), expect_none)

            # New format ok
            obj.prout = '''
## Why is this PR needed?

Because of blah blah

---

## Who/Where is the source of the request of this PR change?

_Specify HSD URL, GitHub issue number (e.g., #1234), or if coming from TPTracker, CTP, etc._
'''
            with CaptureStdoutLog() as p:
                obj.labels.add('BOMCNT1')
                obj.main()
            expect = '''
PR Reason found:
Because of blah blah
'''
            self.assertTextEqual(p.getvalue(), expect)

            # New format - fail
            obj.prout = '''
Some text outside the stuff blah blah

### Why is this PR needed?  Some text outside the stuff blah blah

_Provide a concise summary explaining the motivation for this change._

---

## Who/Where is the source of the request of this PR change?

_Specify HSD URL, GitHub issue number (e.g., #1234), or if coming from TPTracker, CTP, etc._
'''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            self.assertTextEqual(p.getvalue(), expect_none)

            # Instruction was not removed
            obj.prout = '''
### Why is this PR needed?
Some text outside the stuff blah blah

_Provide a concise summary explaining the motivation for this change._

---

## Who/Where is the source of the request of this PR change?

_Specify HSD URL, GitHub issue number (e.g., #1234), or if coming from TPTracker, CTP, etc._
'''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            expecti = '''
==================================================
Error:      The line '_Provide a concise summary explaining the motivation for this change._' is in the Why block of PR description.
Suggestion: Pls remove this line, this is just an instruction.
==================================================
'''
            self.assertTextEqual(p.getvalue(), expecti)

    @with_(TempDir, chdir=True)
    def test_check_pr_checkboxes2(self):
        # unknown header
        obj = TPRobot()
        with MockVar(sys, "argv", 'a.py PRDESC'.split()), \
                MockVar(GitHub, 'add_labels', Mock()), \
                MockVar(obj, 'add_bomcnt', Mock()), \
                MockVar(obj, 'get_pr_view', Mock()):

            # fail case
            obj.prout = '''
### Why is this PR needed?
This is a unittest

### blah
- [ ] yeah filled
- [ X] yeah filled

### What type of PR is this?
- [X] New Planned Feature     (First PR to a planned item)
- [ ] New Unplanned Feature   (First PR to an unplanned item)

---
**Instructions
'''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            self.assertIn('PR description has errors', p.getvalue())

    @with_(TempDir, chdir=True)
    def test_check_pr_checkboxes(self):
        obj = TPRobot()
        with MockVar(sys, "argv", 'a.py PRDESC'.split()), \
                MockVar(GitHub, 'add_labels', Mock()), \
                MockVar(obj, 'add_bomcnt', Mock()), \
                MockVar(obj, 'get_pr_view', Mock()):

            # fail case
            obj.prout = '''
### Why is this PR needed?
This is a unittest

### Who/Where is the source of this PR change
- [X] yeah filled

# first error, unfilled
### What type of PR is this?
- [ ] New Planned Feature     (First PR to a planned item)
- [ ] New Unplanned Feature   (First PR to an unplanned item)

# 2nd error, incorrect checkbox
### Does this PR come with a common PR?
- [ x] No
- [ ] Yes. Pls specify common PR url: _____

# 3rd error, unfilled
### Which Bins are affected?
- [ ] Many bins (Can't tell specific since this change affect many downstream bins)
- [X] Specific bins, Pls specify: _____

# 4th error, missing header (### Which package(s) are affected)

### Socket(s) affected by this PR (HOT/COLD/PHM)?
- [x] HOT
- [ ] COLD

### VALIDATION INFO:
- [x] No validation performed
- [ ] Load and init only or offline

### VALIDATION Temperature:
- [ ] VPO CLASS HOT
- [X] Other, please specify Temp: Filled up
- [ ] Not applicable (no validation performed or load/init only or offline)

---
**Instructions
'''
            with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
                obj.main()
            expect = '''
PR Reason found:
This is a unittest
==================================================
Error:      PR description has errors. See below:
   1. Line "- [ x] No" is not valid checkbox syntax. It must start with "- [x]" or "- [ ]"
   2. Pls fill in the blank for line "- [X] Specific bins, Pls specify: _____"
   3. Section "### What type of PR is this" is not filled. Pls answer this section.
   4. "### Which package(s) are affected" Section is not found. Pls copy template from goto.intel.com/nvl.pr.template
Suggestion: Pls update PR description and fix above errors and re-trigger the checkers.
==================================================
'''
            self.assertTextEqual(p.getvalue(), expect)

            # pass case
            obj.prout = '''
### Why is this PR needed?
This is a unittest

### Who/Where is the source of this PR change
- [X] yeah filled

### What type of PR is this?
- [X] New Planned Feature     (First PR to a planned item)
- [ ] New Unplanned Feature   (First PR to an unplanned item)

### Does this PR come with a common PR?
- [x] No
- [ ] Yes. Pls specify common PR url: _____

### Which Bins are affected?
- [ ] Many bins (Can't tell specific since this change affect many downstream bins)
- [X] Specific bins, Pls specify: yeah___

### Which package(s) are affected
- [X] none

### Socket(s) affected by this PR (HOT/COLD/PHM)?
- [x] HOT
- [ ] COLD

### VALIDATION INFO:
- [x] No validation performed
- [ ] Load and init only or offline

### VALIDATION Temperature:
- [ ] VPO CLASS HOT
- [X] Other, please specify Temp: Filled up
- [ ] Not applicable (no validation performed or load/init only or offline)

---
**Instructions
'''
            obj.main()

    @with_(MockVar, TPRobot, 'check_approved', Mock())
    @with_(MockVar, GitHub, 'get_branch_name', Mock(return_value='TPI/jdr'))
    def test_noapproval(self):
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, ARR_ATOM_L2CXX
reviewers:      iceylu (Requested), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with CaptureStdoutLog() as p:
                        with self.assertRaises(SystemExit):
                            TPRobot().main()

        print(p.getvalue())
        self.assertIn('PR has no approvers yet', p.getvalue())
        self.assertIn('Removing Ready label', p.getvalue())

        # pass case special
        print("NEW CASE=========================")
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, ARR_ATOM_L2CXX, I_AM_TPD_NR, PASSED_Chk
reviewers:      iceylu (Requested), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                    with CaptureStdoutLog() as p:
                        self.assertEqual(TPRobot().main(), 1)

    def test_repo_init_main(self):
        with TempDir(name=True, chdir=True), \
                MockVar(sys, "argv", 'a.py REPO_INIT main_branch'.split()), \
                MockVar(GitCheckout, 'main', Mock(return_value=True)), \
                MockVar(tprobot, 'confirm', Mock()):

            File('UserCode/a.txt').touch(mkdir=True)

            # pass case - no .git
            with CaptureStdoutLog() as p:
                self.assertEqual(TPRobot().main(), 3)
            self.assertFalse('CMD: git checkout main_branch' in p.getvalue())
            self.assertFalse(exists('UserCode'))    # it got deleted

            # pass case - with .git
            File('.git/something').touch(mkdir=True)
            with MockVar(GitCheckout, 'main', Mock(return_value=True)), \
                    CaptureStdoutLog() as p:
                self.assertEqual(TPRobot().main(), 3)
            self.assertFalse('CMD: git checkout main_branch' in p.getvalue())

    def test_repo_init(self):
        obj = TPRobot()
        obj.arg1 = 'main_branch'

        # case1 - wrong trigger label
        with TempDir(name=True, chdir=True), \
                MockVar(sys, "argv", 'a.py REPO_INIT main_branch'.split()), \
                MockVar(tprobot, 'confirm', Mock()):

            with CaptureStdoutLog() as p:
                res = obj.repo_init_check()
                # self.assertEqual(TPRobot().main(), 3)

            self.assertTrue('CMD: git checkout main_branch' in p.getvalue())

            # check the outputs - this is used by other tools
            self.assertEqual(len(res), 3)

        # case2 - UserCode deleted
        with TempDir(name=True, chdir=True):
            File('UserCode/a.txt').touch(mkdir=True)
            with MockVar(sys, "argv", 'a.py REPO_INIT main_branch'.split()):
                with CaptureStdoutLog() as p:
                    with self.assertRaisesRegex(ErrorUser, 'seems to be not clean'):
                        obj.repo_init_check()
            self.assertFalse(exists('UserCode'))    # it got deleted

        # case3 - submodules deleted
        with TempDir(name=True, chdir=True):
            File('Shared/a.txt').touch(mkdir=True)
            with MockVar(sys, "argv", 'a.py REPO_INIT main_branch'.split()), \
                    MockVar(GitHub, 'get_submodules', Mock(return_value=['Shared'])):
                with self.assertRaisesRegex(ErrorUser, 'seems to be not clean'):
                    obj.repo_init_check()
            self.assertFalse(exists('Shared'))    # it got deleted

    def test_check_approved(self):
        with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    obj = TPRobot()
                    obj.check_approved()
        self.assertIn('disabled PR merging', p.getvalue())

        obj.labels.add('MAROON_APPROVED')
        self.assertEqual(obj.check_approved(), 1)

    @with_(MockVar, TPRobot, 'check_approved', Mock())
    def test_wrong_trigger(self):
        # case1 - wrong trigger label
        with MockVar(sys, "argv", 'a.py PRE_CHECK SOMETHING'.split()):
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    TPRobot().main()

        print(p.getvalue())
        self.assertIn('is not a READY trigger. Trigger is: SOMETHING', p.getvalue())

        # case2 - no args
        with MockVar(sys, "argv", 'a.py'.split()):
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    TPRobot().main()

        print(p.getvalue())
        self.assertIn('Incorrect usage', p.getvalue())

        # case3 - no args
        with MockVar(sys, "argv", 'a.py a b'.split()):
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    TPRobot().main()

        print(p.getvalue())
        self.assertIn('Unknown command', p.getvalue())

        # case4 - pass case
        with MockVar(sys, "argv", 'a.py PRE_CHECK READY'.split()):
            with CaptureStdoutLog() as p:
                self.assertEqual(TPRobot().main(), 2)

    def test_unused(self):
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/torch_mvtp') as tdir:
            with MockVar(sys, "argv", f'a.py UNUSED {tdir}'.split()):
                with CaptureStdoutLog() as p:
                    TPRobot().main()
                self.assertIn('UnusedContentFinder', p.getvalue())

        # No env found - in cases of I:\ drive only
        with TempDir(name=True, chdir=True) as tdir:
            with MockVar(sys, "argv", f'a.py UNUSED {tdir}'.split()):
                with CaptureStdoutLog() as p:
                    TPRobot().main()
                self.assertIn('nothing to do', p.getvalue())

    @with_(TempDir, chdir=True)
    @unittest.skipIf(IS_WIN, 'unix only')
    def test_msbuild(self):
        # fail case case, for unix run
        with MockVar(sys, "argv", f'a.py MSBUILD a.sln'.split()):
            with self.assertRaises(SystemExit):
                TPRobot().main()

        # coverage on main, that it go to msbuild
        with MockVar(sys, "argv", f'a.py MSBUILD a.sln'.split()):
            with MockVar(TPRobot, 'msbuild', Mock()):
                self.assertEqual(TPRobot().main(), 5)

        # pass case
        with MockVar(sys, "argv", f'a.py MSBUILD a.sln'.split()):
            with CaptureStdoutLog() as p:
                obj = TPRobot()
                obj.arg1 = 'b.sln'
                obj.msbuild(['/usr/bin/ls'])
        self.assertIn('/usr/bin/ls b.sln -m', p.getvalue())

    @with_(MockVar, TPRobot, 'check_approved', Mock())
    @with_(MockVar, GitHub, 'get_branch_name', Mock(return_value='TPI/jdr'))
    def test_checksha(self):
        GitHub.clear()
        # fail
        out = 'deadbeef\n'
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                with CaptureStdoutLog() as p:
                    with self.assertRaises(SystemExit):
                        TPRobot().main()

        print(p.getvalue())
        self.assertIn('Only latest will be checked', p.getvalue())

        # pass case - READY label is forced
        out = 'deadbeef\n'
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(sys, "argv", 'a.py MAIN deadbeef'.split()):
                # pass case - default
                with CaptureStdoutLog() as p:
                    with MockVar(GitHub, 'get_labels', Mock(return_value={'READY', 'PASSED_Chk'})):
                        tpr = TPRobot()
                        result = tpr.main()

                print("NEW CASE=======================")
                print(p.getvalue())
                self.assertEqual(result, 1)
                self.assertIn('tprobot is DONE', p.getvalue())

    @with_(MockVar, TPRobot, 'check_approved', Mock())
    def test_automerge(self):
        # bundle
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, ARR_ATOM_L2CXX, PASSED_Chk, BUNDLE
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with MockVar(GitHub, 'get_branch_name', Mock(return_value='TPI/jdr')):
                    with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                        with CaptureStdoutLog() as p:
                            self.assertEqual(TPRobot().main(), 1)

        print("CASE ==========================")
        print(p.getvalue())
        self.assertIn('gh pr merge --auto --merge', p.getvalue())
        self.assertIn('tprobot is DONE', p.getvalue())

        # RC branch
        GitHub.clear()
        out = '''
title:  ARRATOM/21B0B_WW49 to TP/21B Merge:Added POWERMUX switch for all VMAX tests
state:  OPEN
author: jdr
labels: ARR_ATOM_CXX, READY, ARR_ATOM_L2CXX, PASSED_Chk
reviewers:      iceylu (Approved), chen3-chen-intel (Requested)
assignees:
'''
        with MockVar(SystemCall, "run_outtxt", Mock(return_value=(1, out))):
            with MockVar(TPRobot, 'get_checkout_sha', Mock(return_value='beef')):
                with MockVar(GitHub, 'get_branch_name', Mock(return_value='TP/RC_37B')):
                    with MockVar(sys, "argv", 'a.py MAIN beef'.split()):
                        with CaptureStdoutLog() as p:
                            self.assertEqual(TPRobot().main(), 1)

        print("CASE ==========================")
        print(p.getvalue())
        self.assertIn('gh pr merge --auto --merge', p.getvalue())
        self.assertIn('tprobot is DONE', p.getvalue())

    @with_(TempDir, chdir=True)
    def test_check_items(self):
        # pass case
        text = '''
- [X] checklist1

### What type of PR is this
- [ ] not a problem

- [ ] 2nd line

### Why is this PR needed?
- [x] AR1

---
- [X] AR2
'''
        self.assertEqual(CheckedMarks().main(text), 1)

        # fail case
        text = '''
- [ ] checklist1

### What type of PR is this
- [ ] not a problem

### Why is this PR needed?
- [ ] AR1

---
- [ ] AR2
'''

        with self.assertRaises(SystemExit), CaptureStdoutLog() as p:
            CheckedMarks().main(text)

        expect = '''
==================================================
Error:      Required checklist items (3) below is not yet completed:
   - [ ] checklist1
   - [ ] AR1
   - [ ] AR2
Suggestion: TPBot cannot proceed because of above.
==================================================
'''
        self.assertTextEqual(p.getvalue(), expect)

        # empty case
        self.assertEqual(CheckedMarks().main(''), -1)

    def test_old_pr(self):
        # old PR
        text = '''
### Why is this PR needed?
_Provide a concise summary explaining the motivation for this change._

### Who/Where is the source of the request of this PR change?
_Specify HSD URL, GitHub issue number (e.g., #1234), or if coming from TPTracker, CTP, etc._

### Does this PR come with a common PR?
_Yes/No. If yes, please specify the linked common PR._

### What Bin(s) are affected (e.g., B60)?
_List all affected bins:_
e.g., B60

### Socket(s) affected by this PR (HOT/COLD/PHM)?
- [ ] HOT
- [ ] COLD
- [ ] PHM

### Which package is affected?
- [ ] All packages
- [ ] Novalake S 28C
- [ ] Novalake S 52C
- [ ] Novalake S 28C BLLC
- [ ] Novalake S 16C
- [ ] Novalake UL
- [ ] Novalake U
- [ ] Novalake H
- [ ] Novalake P
- [ ] Novalake HX
- [ ] Novalake AX 28C
- [ ] Novalake AX 16C

### Other detail worth mentioning?
_Include any extra notes, context, or special considerations here._

### VALIDATION INFO:
- [ ] No validation performed
- [ ] Load and init only offline
- [ ] Standing die check. If MBOT, please provide URL log: [Paste log link]
- [ ] VPO: Please specify #: [VPO number]

### VALIDATION Temperature:
- [ ] VPO CLASSHOT
- [ ] VPO COLD (CSM/PHMCOLD/PHMROOM)
- [ ] MBOT default temp
- [ ] Other, please specify: [Describe]

---
**Instructions above: Put 'X' inside the square brackets if you have performed that validation. No space between brackets.**

'''
        # must not fail
        self.assertEqual(CheckedMarks().main(text), 2)

    def test_check_passed_label(self):
        obj = TPRobot()

        # normal check
        obj.labels = {'PASSED_Chk'}
        self.assertEqual(obj.check_passed_label(), 1)

        # bom labels - fail
        with TempDir(chdir=True):
            File('POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
            File('POR_TP/Class_NVL_S68C/EnvironmentFile.env').touch(mkdir=True)
            obj.labels = {'PASSED_S68C'}
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    obj.check_passed_label()
            self.assertIn('PASSED_S28C', p.getvalue())

        # bom labels - pass
        with TempDir(chdir=True):
            File('POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
            File('POR_TP/Class_NVL_S68C/EnvironmentFile.env').touch(mkdir=True)
            obj.labels = {'PASSED_S28C', 'PASSED_S68C'}
            self.assertEqual(obj.check_passed_label(), 2)

    def test_check_passed_label_perbom(self):
        obj = TPRobot()

        with MockVar(os.environ, 'TARGETBOM', 'Class_NVL_S28C'):
            # bom labels - fail
            with TempDir(chdir=True):
                obj.labels = {'PASSED_S68C'}
                with CaptureStdoutLog() as p:
                    with self.assertRaises(SystemExit):
                        obj.check_passed_label()
                self.assertIn('PASSED_S28C', p.getvalue())

            # bom labels - pass
            with TempDir(chdir=True):
                obj.labels = {'PASSED_S28C', 'PASSED_S68C'}
                self.assertEqual(obj.check_passed_label(), 2)

    def test_get_pr_view_closed(self):
        # Test get_pr_view_closed method with PR number
        obj = TPRobot()

        # Case 1: Successfully get closed PR info with PR number
        json_output = '{"number": 1234, "body": "Test PR description\\nnvl.hub BRANCH: test_branch"}'
        with MockVar(SystemCall, 'run_outonly', Mock(return_value=json_output)):
            with CaptureStdoutLog() as p:
                pr_body, pr_number = obj.get_pr_view_closed(1234)

            self.assertEqual(pr_number, '1234')
            self.assertEqual(pr_body, 'Test PR description\nnvl.hub BRANCH: test_branch')
            self.assertIn('Found PR #1234', p.getvalue())

        # Case 2: No PR found (empty output)
        with MockVar(SystemCall, 'run_outonly', Mock(return_value='')):
            with CaptureStdoutLog() as p:
                pr_body, pr_number = obj.get_pr_view_closed(9999)

            self.assertIsNone(pr_body)
            self.assertIsNone(pr_number)
            self.assertIn('No PR found for number: 9999', p.getvalue())

        # Case 3: Exception handling (invalid JSON)
        with MockVar(SystemCall, 'run_outonly', Mock(return_value='invalid json')):
            with CaptureStdoutLog() as p:
                pr_body, pr_number = obj.get_pr_view_closed(1234)

            self.assertIsNone(pr_body)
            self.assertIsNone(pr_number)
            self.assertIn('Error getting closed PR info', p.getvalue())

    @with_(MockVar, Check, 'min_python_version', Mock())
    @with_(MockVar, TPRobot, 'get_pr_view', Mock())
    def test_PR_Gatekeeper_success(self):
        # Test successful PR gatekeeper validation
        obj = TPRobot()

        # Mock the PR description
        valid_description = "This PR fixes a critical bug in the test flow that causes failures in B60 bin testing."

        # Mock check_pr_why to return valid description
        with MockVar(obj, 'check_pr_why', Mock(return_value=valid_description)):
            # Mock PR_Gatekeeper class and its main method
            mock_gatekeeper_instance = Mock()
            mock_gatekeeper_instance.main.return_value = 1, "YES"  # Success
            mock_gatekeeper_class = Mock(return_value=mock_gatekeeper_instance)

            # Mock the imported PR_Gatekeeper class from genai module
            with MockVar(genai.qagent_pr_gatekeeper, 'PR_Gatekeeper', mock_gatekeeper_class), \
                    MockVar(sys, "argv", 'a.py PR_GATEKEEPER'.split()):

                # Should not raise exception
                obj.main()

                # Verify PR_Gatekeeper was instantiated and main was called
                mock_gatekeeper_class.assert_called_once_with(valid_description)
                mock_gatekeeper_instance.main.assert_called_once()

    @with_(MockVar, Check, 'min_python_version', Mock())
    @with_(MockVar, TPRobot, 'get_pr_view', Mock())
    @unittest.skip('Skip for now')
    def test_PR_Gatekeeper_failure(self):
        # Test PR gatekeeper validation failure
        obj = TPRobot()
        obj.prout = 'blah'
        test_description = "Fixes minor typo."

        with MockVar(obj, "check_pr_why", Mock(return_value=test_description)):
            mock_pr_gatekeeper = Mock()
            mock_pr_gatekeeper.main.return_value = 0, "Ignore"  # Indicate failure
            mock_pr_gatekeeper_class = Mock(return_value=mock_pr_gatekeeper)

            with MockVar(genai.qagent_pr_gatekeeper, 'PR_Gatekeeper', mock_pr_gatekeeper_class):
                with self.assertRaises(SystemExit):
                    obj.PR_Gatekeeper()

                # Verify PR_Gatekeeper was instantiated and main was called
                mock_pr_gatekeeper_class.assert_called_once_with(test_description)
                mock_pr_gatekeeper.main.assert_called_once()

    def test_PR_Gatekeeper_python_version_check(self):
        # Test that Python version check is performed
        obj = TPRobot()

        # Mock min_python_version to raise exception for old Python
        mock_check = Mock(side_effect=Exception("Python 3.10 or higher is required"))

        with MockVar(Check, 'min_python_version', mock_check):
            with MockVar(obj, 'check_pr_why', Mock(return_value="test description")):

                # Should raise exception due to version check
                with self.assertRaisesRegex(Exception, 'Python 3.10'):
                    obj.PR_Gatekeeper()

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="on development only", neg=False))
    @unittest.skipIf(is_lower_310(), "Need python3.10 or newer")
    def test_PR_Gatekeeper_real_detailed_bug_fix(self):
        # Test PR_Gatekeeper with real DataHost - detailed bug fix description
        obj = TPRobot()

        obj.prout = '''
    ### Why is this PR needed?
    This PR addresses HSD #98765 where the test program crashes when encountering invalid
    bin configurations. The root cause was improper error handling in the bin parser module
    that did not validate input parameters. This fix adds comprehensive validation and
    error messages to prevent crashes and provide actionable feedback to users.

    The issue manifests when:
    1. Bin configuration files contain non-numeric bin IDs
    2. Missing required fields in the configuration
    3. Duplicate bin definitions exist

    Without this fix, production tests fail silently, causing significant delays in
    manufacturing validation cycles.

    ### What type of PR is this?
    - [x] New Planned Feature     (First PR to a planned item)
    - [ ] New Unplanned Feature   (First PR to an unplanned item)
    - [ ] Response to a Sighting  (First PR to a sighting/QE event/bug)
    - [ ] Fix to a previous PR
    - [ ] Other, pls specify: _____

    ### Who/Where is the source of the request of this PR change?
    HSD #98765, requested by manufacturing team

    ### Does this PR come with a common PR?
    No

    ### What Bin(s) are affected (e.g., B60)?
    B60, B70, B80

    ### Socket(s) affected by this PR (HOT/COLD/PHM)?
    - [X] HOT
    - [X] COLD
    - [X] PHM

    ### Which package is affected?
    - [X] All packages

    ### Other detail worth mentioning?
    Tested with 500+ configuration files from production

    ### VALIDATION INFO:
    - [ ] No validation performed
    - [ ] Load and init only offline
    - [X] Standing die check. If MBOT, please provide URL log: http://mbot.example.com/log/12345
    - [ ] VPO: Please specify #:

    ### VALIDATION Temperature:
    - [X] VPO CLASSHOT
    - [X] VPO COLD (CSM/PHMCOLD/PHMROOM)
    - [ ] MBOT default temp
    - [ ] Other, please specify:
    '''

        # Mock get_pr_view to set prout
        with MockVar(obj, 'get_pr_view', Mock(return_value=None)):
            obj.PR_Gatekeeper()

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="on development only", neg=False))
    @unittest.skipIf(is_lower_310(), "Need python3.10 or newer")
    def test_PR_Gatekeeper_real_failing_case(self):
        # Test PR_Gatekeeper with real DataHost
        # /usr/intel/pkgs/python3/3.12.3/bin/python3 main/test/test_tprobot.py TestTpRobot.test_PR_Gatekeeper_real_failing_case
        obj = TPRobot()

        # edit below for testing purpose
        reason = 'lessten'

        obj.prout = f'''
    ### Why is this PR needed?
    {reason}

    ### Who/Where is the source of the request of this PR change?
    HSD #98765, requested by manufacturing team

    ### Does this PR come with a common PR?
    No

    ### What Bin(s) are affected (e.g., B60)?
    B60, B70, B80

    ### Socket(s) affected by this PR (HOT/COLD/PHM)?
    - [X] HOT
    - [X] COLD
    - [X] PHM

    ### Which package is affected?
    - [X] All packages

    ### Other detail worth mentioning?
    Tested with 500+ configuration files from production

    ### VALIDATION INFO:
    - [ ] No validation performed
    - [ ] Load and init only offline
    - [X] Standing die check. If MBOT, please provide URL log: http://mbot.example.com/log/12345
    - [ ] VPO: Please specify #:

    ### VALIDATION Temperature:
    - [X] VPO CLASSHOT
    - [X] VPO COLD (CSM/PHMCOLD/PHMROOM)
    - [ ] MBOT default temp
    - [ ] Other, please specify:
    '''
        with MockVar(TPRobot, 'get_pr_view', Mock()):
            with self.assertRaises(SystemExit):
                obj.PR_Gatekeeper()


class TestAtomic(TestCase):

    @with_(TempDir, chdir=True)
    def test_integration(self):
        obj = TPRobot()

        prdesc = """
NOTE:
nvl.hub BRANCH: hub_flow_wrap_3
nvl.gcd BRANCH: gcd_flow_wrap_2

Why is this PR needed?
flow wrap for HX and S52. Reverts #854 and reinstates #808
"""
        with MockVar(obj, 'get_pr_view_closed', Mock(return_value=(prdesc, '1234'))), \
                MockVar(sys, "argv", 'a.py CHECK_ATOMIC'.split()), \
                MockVar(SystemCall, 'run_outonly', Mock(return_value='1133\n')), \
                MockVar(SystemCall, 'run', Mock(return_value=0)), \
                CaptureStdoutLog() as p:

            self.assertEqual(obj.main(), 6)
            self.assertIn('nvl.gcd: PR number = 1133', p.getvalue())
            self.assertIn('nvl.hub: PR number = 1133', p.getvalue())
            self.assertIn('Marked PR #1133 in nvl.gcd as ready for review', p.getvalue())

        # Test NON-atomic PR (no branch specifications)
        obj = TPRobot()

        prdesc = """
### Why is this PR needed?
This is a regular PR without atomic changes

### What type of PR is this?
- [X] New Planned Feature

### Who/Where is the source of this PR change?
- [X] Planned item
"""
        with MockVar(obj, 'get_pr_view_closed', Mock(return_value=(prdesc, '1234'))), \
                MockVar(sys, "argv", 'a.py CHECK_ATOMIC'.split()), \
                CaptureStdoutLog() as p:

            self.assertEqual(obj.main(), 6)
            self.assertIn('No atomic changes detected', p.getvalue())
            self.assertIn('Skipping version update', p.getvalue())

    def test_get_all_pr_numbers(self):
        # basic case
        prlist = {'nvl.cpu': 'cpu_flow_wrap_2',
                  'nvl.gcd': 'gcd_flow_wrap_2'}
        with MockVar(SystemCall, 'run_outonly', Mock(return_value='1133\n')):
            result = AtomicChange.get_all_pr_numbers(prlist)
        self.assertEqual(result, {'nvl.cpu': '1133',
                                  'nvl.gcd': '1133'})

        # no output
        with MockVar(SystemCall, 'run_outonly', Mock(return_value='')):
            result = AtomicChange.get_all_pr_numbers(prlist)
        self.assertEqual(result, {'nvl.cpu': None,
                                  'nvl.gcd': None})

        # some error on gh
        with MockVar(SystemCall, 'run_outonly', Mock(return_value='no pull requests found for branch "add_ahmt_qgate_waiver_ww44p5x"')):
            result = AtomicChange.get_all_pr_numbers(prlist)
        self.assertEqual(result, {'nvl.cpu': None,
                                  'nvl.gcd': None})

    def test_mark_prs_ready(self):
        # both are passing
        data = {'nvl.cpu': '1133',
                'nvl.gcd': '1133',
                'nvl.hub': None}

        system_arg_input = []

        def fake_run(slf, disp=None):
            system_arg_input.append(' '.join(slf.cmd))
            return 0    # passing case

        with MockVar(SystemCall, 'run', fake_run):
            result = AtomicChange.mark_prs_ready(data)

        self.assertEqual(result, 0)   # there are no fails
        pprint(system_arg_input)
        self.assertEqual(system_arg_input, ['gh pr ready 1133 --repo intel-restricted/nvl.cpu',
                                            'gh pr ready 1133 --repo intel-restricted/nvl.gcd'])

        # let's say both of them failed
        system_arg_input = []

        def fake_run2(slf, disp=None):
            system_arg_input.append(' '.join(slf.cmd))
            return 1    # fail case

        with MockVar(SystemCall, 'run', fake_run2):
            result = AtomicChange.mark_prs_ready(data)

        self.assertEqual(result, 2)   # there are no fails

    def test_check_atomic_and_get_branch(self):
        # basic case
        prdesc = """
NOTE:
nvl.hub BRANCH: hub_flow_wrap_3
nvl.gcd BRANCH: gcd_flow_wrap_2
nvl.pcd BRANCH: pcd_flow_wrap_2
nvl.cpu BRANCH: cpu_flow_wrap_2

Why is this PR needed?
flow wrap for HX and S52. Reverts #854 and reinstates #808
"""
        AtomicChange.prout = prdesc
        result = AtomicChange.check_atomic_and_get_branch()
        pprint(result)
        self.assertEqual(result, {'nvl.cpu': 'cpu_flow_wrap_2',
                                  'nvl.gcd': 'gcd_flow_wrap_2',
                                  'nvl.hub': 'hub_flow_wrap_3',
                                  'nvl.pcd': 'pcd_flow_wrap_2'})

        # no atomic change / keyword not complete
        prdesc = """
Why is this PR needed?
flow wrap for HX and S52. Reverts #854 and reinstates #808
This PR is needed for nvl.hub BRANCH
"""
        AtomicChange.prout = prdesc
        result = AtomicChange.check_atomic_and_get_branch()
        pprint(result)
        self.assertEqual(result, {})

        # partial two only
        prdesc = """
nvl.hub BRANCH: hub_flow_wrap_3
nvl.gcd BRANCH: gcd_flow_wrap_2

Why is this PR needed?
flow wrap for HX and S52. Reverts #854 and reinstates #808
This PR is needed for nvl.hub BRANCH
"""
        AtomicChange.prout = prdesc
        result = AtomicChange.check_atomic_and_get_branch()
        pprint(result)
        self.assertEqual(result, {'nvl.gcd': 'gcd_flow_wrap_2',
                                  'nvl.hub': 'hub_flow_wrap_3'})

        # incorrect keyword - should just ignore invalid repos
        prdesc = """
nvl.hub BRANCH: hub_flow_wrap_3
arl.gcd BRANCH: gcd_flow_wrap_2

Why is this PR needed?
flow wrap for HX and S52. Reverts #854 and reinstates #808
This PR is needed for nvl.hub BRANCH
"""
        AtomicChange.prout = prdesc
        result = AtomicChange.check_atomic_and_get_branch()
        # Should only return nvl.hub, arl.gcd is filtered out
        self.assertEqual(result, {'nvl.hub': 'hub_flow_wrap_3'})

    @with_(TempDir, chdir=True)
    def test_load_json_file(self):
        # Test load_json_file method
        # Case 1: File doesn't exist - should create default data
        with TempDir(name=True) as tdir:
            json_path = join(tdir, 'atomic_version_db')
            existing_data, current_version, file_path = AtomicChange.load_json_file(json_path)

            self.assertEqual(current_version, '1.0')
            self.assertTrue(file_path.endswith('main.json'))
            self.assertEqual(existing_data, {
                'latest': '1.0',
                'nvl.hub': {"1": ["1.0"]},
                'nvl.cpu': {"1": ["1.0"]},
                'nvl.pcd': {"1": ["1.0"]},
                'nvl.gcd': {"1": ["1.0"]},
                'nvl.common': {"1": ["1.0"]},
            })

        # Case 2: File exists - should load existing data
        with TempDir(name=True) as tdir:
            json_path = join(tdir, 'atomic_version_db')
            os.makedirs(json_path, exist_ok=True)
            test_file = join(json_path, 'main.json')

            test_data = {
                'latest': '2.5.11000000001',
                'nvl.hub': {'1234': ['2.5.11000000001']},
                'nvl.cpu': {'5678': ['2.5.11000000001']},
                'nvl.pcd': {'9012': ['2.5.11000000001']},
                'nvl.gcd': {'3456': ['2.5.11000000001']},
                'nvl.common': {'120': ['2.5.11000000001']}
            }

            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            existing_data, current_version, file_path = AtomicChange.load_json_file(json_path)

            self.assertEqual(current_version, '2.5.11000000001')
            self.assertEqual(existing_data, {
                'latest': '2.5.11000000001',
                'nvl.hub': {'1234': ['2.5.11000000001']},
                'nvl.cpu': {'5678': ['2.5.11000000001']},
                'nvl.pcd': {'9012': ['2.5.11000000001']},
                'nvl.gcd': {'3456': ['2.5.11000000001']},
                'nvl.common': {'120': ['2.5.11000000001']}
            })

        # Case 3: Branch-specific filename (with BASE_REF env var)
        with TempDir(name=True) as tdir:
            json_path = join(tdir, 'atomic_version_db')
            os.makedirs(json_path, exist_ok=True)

            with MockVar(os.environ, 'BASE_REF', 'main_nvl'):
                existing_data, current_version, file_path = AtomicChange.load_json_file(json_path)
                self.assertTrue(file_path.endswith('main_nvl.json'))
                self.assertEqual(current_version, '1.0')
                self.assertEqual(existing_data, {
                    'latest': '1.0',
                    'nvl.hub': {"1": ["1.0"]},
                    'nvl.cpu': {"1": ["1.0"]},
                    'nvl.pcd': {"1": ["1.0"]},
                    'nvl.gcd': {"1": ["1.0"]},
                    'nvl.common': {"1": ["1.0"]},
                })

        # Case 4: BASE_REF='main' should create main.json (not main_main.json)
        with TempDir(name=True) as tdir:
            json_path = join(tdir, 'atomic_version_db')
            os.makedirs(json_path, exist_ok=True)

            with MockVar(os.environ, 'BASE_REF', 'main'):
                existing_data, current_version, file_path = AtomicChange.load_json_file(json_path)
                self.assertTrue(file_path.endswith('main.json'))
                self.assertFalse('main_main.json' in file_path)
                self.assertEqual(current_version, '1.0')
                self.assertEqual(existing_data, {
                    'latest': '1.0',
                    'nvl.hub': {"1": ["1.0"]},
                    'nvl.cpu': {"1": ["1.0"]},
                    'nvl.pcd': {"1": ["1.0"]},
                    'nvl.gcd': {"1": ["1.0"]},
                    'nvl.common': {"1": ["1.0"]},
                })

    def test_check_affected_bom(self):
        # Test check_affected_bom method
        n = len(AtomicChange.BOM_MAPPING)
        all_names = [full for full, _ in AtomicChange.BOM_MAPPING]

        # Case 1: All packages checked via "All packages" checkbox
        pr_desc_all = """
### Which package is affected?
- [X] All packages
- [ ] Novalake S 28C
"""
        AtomicChange.prout = pr_desc_all
        bom_flags, is_all_packages = AtomicChange.check_affected_bom()
        self.assertEqual(bom_flags, '1' * n)
        self.assertTrue(is_all_packages)

        # Case 2: Specific individual packages checked — select first, third, and seventh by position
        # Build both the PR description and expected flags from BOM_MAPPING dynamically
        checked_indices = {0, 2, 6}
        pr_lines = ['### Which package is affected?', '- [ ] All packages']
        for i, name in enumerate(all_names):
            mark = 'X' if i in checked_indices else ' '
            pr_lines.append(f'- [{mark}] {name}')
        AtomicChange.prout = '\n'.join(pr_lines)
        expected_flags = ''.join('1' if i in checked_indices else '0' for i in range(n))
        bom_flags, is_all_packages = AtomicChange.check_affected_bom()
        self.assertEqual(bom_flags, expected_flags)
        self.assertFalse(is_all_packages)

        # Case 3: All individual packages checked — build PR desc from BOM_MAPPING so it always
        # covers every BOM regardless of how many are in the mapping
        pr_lines = ['### Which package is affected?', '- [ ] All packages']
        for name in all_names:
            pr_lines.append(f'- [X] {name}')
        AtomicChange.prout = '\n'.join(pr_lines)
        bom_flags, is_all_packages = AtomicChange.check_affected_bom()
        self.assertEqual(bom_flags, '1' * n)
        self.assertTrue(is_all_packages)  # All individually marked → treated as all packages

        # Case 4: No packages checked
        pr_desc_none = """
### Which package is affected?
- [ ] All packages
- [ ] Novalake S 28C
"""
        AtomicChange.prout = pr_desc_none
        bom_flags, is_all_packages = AtomicChange.check_affected_bom()
        self.assertEqual(bom_flags, '0' * n)
        self.assertFalse(is_all_packages)

    def test_uprev_atomic_rev(self):
        """Test uprev_atomic_rev method"""
        # Case 1: Increment minor version (string with BOM flags)
        with CaptureStdoutLog() as p:
            result = AtomicChange.uprev_atomic_rev('1.4.11000000001', is_all_packages=False)
        self.assertEqual(result, '1.5')
        self.assertIn('1.5', p.getvalue())

        # Case 2: Increment major version (string with BOM flags)
        with CaptureStdoutLog() as p:
            result = AtomicChange.uprev_atomic_rev('1.22.11000000001', is_all_packages=True)
        self.assertEqual(result, '2.0')
        self.assertIn('2.0', p.getvalue())

        # Case 3: Increment major version (string with BOM flags)
        with CaptureStdoutLog() as p:
            result = AtomicChange.uprev_atomic_rev('1.9.11000000001', is_all_packages=False)
        self.assertEqual(result, '1.10')
        self.assertIn('1.10', p.getvalue())

    def test_update_atomic_dict(self):
        """Test update_atomic_dict method"""
        # Case 1: Basic update with new PR numbers
        pr_numbers = {'nvl.hub': '1234', 'nvl.cpu': '5678'}
        new_version = '1.5'
        bom_flags = '11000000001'
        existing_data = {
            'latest': '1.4.10000000000',
            'nvl.hub': {'1000': ['1.4.10000000000']},
            'nvl.cpu': {'2000': ['1.4.10000000000']},
            'nvl.pcd': {'3000': ['1.4.10000000000']},
            'nvl.gcd': {'4000': ['1.4.10000000000']},
            'nvl.common': {'100': ['1.4.10000000000']}
        }

        AtomicChange.prno = '120'
        result = AtomicChange.update_atomic_dict(pr_numbers, new_version, bom_flags, existing_data)

        self.assertEqual(result, {
            'latest': '1.5.11000000001',
            'nvl.hub': {'1000': ['1.4.10000000000'], '1234': ['1.5.11000000001']},
            'nvl.cpu': {'2000': ['1.4.10000000000'], '5678': ['1.5.11000000001']},
            'nvl.pcd': {'3000': ['1.4.10000000000', '1.5.11000000001']},
            'nvl.gcd': {'4000': ['1.4.10000000000', '1.5.11000000001']},
            'nvl.common': {'100': ['1.4.10000000000'], '120': ['1.5.11000000001']}
        })

    def test_atomic_revision_final_workflow(self):
        """Test atomic_revision_final_workflow method"""
        # Case 1: All packages affected (major version increment)
        pr_numbers = {'nvl.hub': '1234', 'nvl.cpu': '5678'}
        current_version = '1.22.10000000000'
        existing_data = {
            'latest': '1.22.10000000000',
            'nvl.hub': {'1000': ['1.22.10000000000']},
            'nvl.cpu': {'2000': ['1.22.10000000000']},
            'nvl.pcd': {'3000': ['1.22.10000000000']},
            'nvl.gcd': {'4000': ['1.22.10000000000']},
            'nvl.common': {'100': ['1.22.10000000000']}
        }

        AtomicChange.prno = '120'
        with MockVar(AtomicChange, 'check_affected_bom', Mock(return_value=('11111111111', True))), \
                CaptureStdoutLog() as p:
            result = AtomicChange.atomic_revision_final_workflow(pr_numbers, current_version, existing_data)

        self.assertIn('2.0', p.getvalue())
        self.assertEqual(result, {
            'latest': '2.0.11111111111',
            'nvl.hub': {'1000': ['1.22.10000000000'], '1234': ['2.0.11111111111']},
            'nvl.cpu': {'2000': ['1.22.10000000000'], '5678': ['2.0.11111111111']},
            'nvl.pcd': {'3000': ['1.22.10000000000', '2.0.11111111111']},
            'nvl.gcd': {'4000': ['1.22.10000000000', '2.0.11111111111']},
            'nvl.common': {'100': ['1.22.10000000000'], '120': ['2.0.11111111111']}
        })

        # Case 2: Individual packages affected (minor version increment)
        current_version = '1.4.10000000000'
        existing_data = {
            'latest': '1.4.10000000000',
            'nvl.hub': {'1000': ['1.4.10000000000']},
            'nvl.cpu': {'2000': ['1.4.10000000000']},
            'nvl.pcd': {'3000': ['1.4.10000000000']},
            'nvl.gcd': {'4000': ['1.4.10000000000']},
            'nvl.common': {'100': ['1.4.10000000000']}
        }

        AtomicChange.prno = '121'
        with MockVar(AtomicChange, 'check_affected_bom', Mock(return_value=('10100000000', False))), \
                CaptureStdoutLog() as p:
            result = AtomicChange.atomic_revision_final_workflow(pr_numbers, current_version, existing_data)

        self.assertIn('1.5', p.getvalue())
        self.assertEqual(result, {
            'latest': '1.5.10100000000',
            'nvl.hub': {'1000': ['1.4.10000000000'], '1234': ['1.5.10100000000']},
            'nvl.cpu': {'2000': ['1.4.10000000000'], '5678': ['1.5.10100000000']},
            'nvl.pcd': {'3000': ['1.4.10000000000', '1.5.10100000000']},
            'nvl.gcd': {'4000': ['1.4.10000000000', '1.5.10100000000']},
            'nvl.common': {'100': ['1.4.10000000000'], '121': ['1.5.10100000000']}
        })

    @with_(TempDir, chdir=True)
    def test_save_json_file(self):
        # Test save_json_file method
        # Case 1: Save to new file
        with TempDir(name=True) as tdir:
            json_path = join(tdir, 'atomic_version_db')
            os.makedirs(json_path, exist_ok=True)
            file_path = join(json_path, 'main.json')

            test_data = {
                'latest': '1.5.11000000001',
                'nvl.hub': {'1234': ['1.5.11000000001']},
                'nvl.cpu': {'5678': ['1.5.11000000001']},
                'nvl.pcd': {'9012': ['1.5.11000000001']},
                'nvl.gcd': {'3456': ['1.5.11000000001']},
                'nvl.common': {'120': ['1.5.11000000001']}
            }

            with CaptureStdoutLog() as p:
                AtomicChange.save_json_file(file_path, test_data)

            self.assertTrue(os.path.exists(file_path))
            self.assertIn('Version data saved', p.getvalue())

            # Verify the saved content
            with open(file_path, 'r') as f:
                saved_data = json.load(f)

            self.assertEqual(saved_data, {
                'latest': '1.5.11000000001',
                'nvl.hub': {'1234': ['1.5.11000000001']},
                'nvl.cpu': {'5678': ['1.5.11000000001']},
                'nvl.pcd': {'9012': ['1.5.11000000001']},
                'nvl.gcd': {'3456': ['1.5.11000000001']},
                'nvl.common': {'120': ['1.5.11000000001']}
            })

        # Case 2: Save with existing file (should create backup)
        with TempDir(name=True) as tdir:
            json_path = join(tdir, 'atomic_version_db')
            os.makedirs(json_path, exist_ok=True)
            file_path = join(json_path, 'main.json')

            # Create initial file
            initial_data = {'latest': '1.0', 'nvl.hub': {}}
            with open(file_path, 'w') as f:
                json.dump(initial_data, f)

            # Save new data (should backup old file)
            new_data = {'latest': '2.0', 'nvl.hub': {'9999': ['2.0']}}
            with CaptureStdoutLog() as p:
                AtomicChange.save_json_file(file_path, new_data)

            # Check backup was created
            backup_path = f'{file_path}.previous'
            self.assertTrue(os.path.exists(backup_path))
            self.assertIn('Backup created', p.getvalue())

            # Verify backup contains old data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            self.assertEqual(backup_data, {'latest': '1.0', 'nvl.hub': {}})

            # Verify new file contains new data
            with open(file_path, 'r') as f:
                saved_data = json.load(f)
            self.assertEqual(saved_data, {'latest': '2.0', 'nvl.hub': {'9999': ['2.0']}})

        # Case 3: Error handling (invalid path)
        with CaptureStdoutLog() as p:
            # Try to save to invalid path
            AtomicChange.save_json_file('/invalid/path/that/does/not/exist/file.json', {})
        self.assertIn('Error saving JSON file', p.getvalue())

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/SimpleNVL')
    def test_do_sendemail(self):
        obj = TPRobot()

        # Case 1 - Coverage on main, test sendemails command.
        with MockVar(sys, "argv", f'a.py SENDEMAILS'.split()):
            with MockVar(TPRobot, 'sendemails', Mock()):
                self.assertEqual(TPRobot().main(), 6)

        # Case 2 - Email sending is disabled when TO_LIST env var is not set.
        with MockVar(os.environ, 'TO_LIST', MockVar.delete):
            result = obj.sendemails()
            self.assertEqual(result, None)

        # Mock DataHost.central to capture the call.
        def _setup_mock_central_and_capture():
            """Helper to setup DataHost.central mock and return captured_args list."""
            captured_args = []

            def mock_central(self, method, args, check=False, site=None):
                captured_args.append((method, args, check))
                return None

            DataHost.central = mock_central
            return captured_args

        # Case 3 - Successful email sending for passed workflow.
        with MockVar(os.environ, 'TO_LIST', 'pass_blahblah@intel.com'), \
                MockVar(os.environ, 'WORKFLOW_RESULT', 'Pass'), \
                TempDir():
            captured_args = _setup_mock_central_and_capture()
            obj.sendemails()

            # Verify that sendmail was called
            self.assertEqual(len(captured_args), 1)
            self.assertTextEqual(captured_args[0][0], 'sendmail')

            # Verify email arguments
            to_list, subject, body = captured_args[0][1][:3]
            self.assertTextEqual(to_list, 'pass_blahblah@intel.com')
            self.assertIn('Pass', subject)
            self.assertIn('passed NVL automation workflow checks', body)

        # Case 4 - Successful email sending for failed workflow.
        with MockVar(os.environ, 'TO_LIST', 'fail_blah@intel.com,fail_blahblah@intel.com'), \
                MockVar(os.environ, 'WORKFLOW_RESULT', 'Fail'), \
                TempDir():
            captured_args = _setup_mock_central_and_capture()
            obj.sendemails()

            # Verify that sendmail was called
            self.assertEqual(len(captured_args), 1)
            self.assertTextEqual(captured_args[0][0], 'sendmail')

            # Verify email arguments
            to_list, subject, body = captured_args[0][1]
            self.assertTextEqual(to_list, 'fail_blah@intel.com,fail_blahblah@intel.com')
            self.assertIn('Fail', subject)
            self.assertIn('FAILED with NVL automation workflow', body)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
