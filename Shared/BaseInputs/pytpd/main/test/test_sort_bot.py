#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for sort_bot.py (labeler)
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.files import TempDir, File
from gadget.disk import Chdir
from main.sort_bot import *
from gadget.gizmo import MockVar, with_
from os.path import join, dirname, abspath


class TestSortBot(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        cmd_list = []

        out_pr = '''
labels: tpi_label, ARR_CORE
'''
        out_diff = '''

  shell: /usr/intel/bin/bash -e {0}
  env:
    GITHUB_TOKEN: ***
diff --git a/.github/workflows/checkers.yml b/.github/workflows/checkers.yml
index 65f3ccb3..e35a758c 100644
--- a/.github/workflows/checkers.yml
+++ b/.github/workflows/checkers.yml
@@ -26,6 +26,11 @@ jobs:
         git fetch
         git merge origin/master
        '''
        out_all_labels = '''
showstopper             #EE32EB
blah
SCN_CCF_C68             #0000ff
'''

        def fake(slf, *kwargs):
            cmd = ' '.join(slf.cmd)
            cmd_list.append(cmd)
            if 'gh pr diff' in cmd:
                return 0, out_diff
            if 'gh label list' in cmd:
                return 0, out_all_labels
            if 'gh label create' in cmd:
                return 0, ''
            if '--add-label' in cmd:
                return 0, ''
            if '--remove-label' in cmd:
                return 0, ''
            if 'gh pr view' in cmd:
                return 0, out_pr
            raise Exception(f'fake(): Dont know how to handle: {cmd}')

        # no args
        with MockVar(sys, 'argv', ['a.py']):
            self.assertEqual(SortBot().main(), 1)

        File('Modules/ARR_CORE/a.mtpl').touch(mkdir=True)

        # basic run
        with MockVar(sys, 'argv', ['a.py', 'MAIN', 'some_branch']):
            with MockVar(SystemCall, "run_outtxt", fake):
                SortBot().main()

        self.assertEqual(cmd_list, ['gh pr diff some_branch',
                                    'gh label list -L 3000',
                                    'gh label create YML -c 0000ff',
                                    'gh pr edit some_branch --add-label YML',
                                    'gh pr view',
                                    'gh pr edit --remove-label ARR_CORE'])

    @with_(TempDir, chdir=True)
    def test_basic_qualdoc(self):
        cmd_list = []

        out_pr = '''
- [X] TPDB QualDoc
'''

        def fake(slf, *kwargs):
            cmd = ' '.join(slf.cmd)
            cmd_list.append(cmd)
            if 'gh pr view' in cmd:
                return 0, out_pr
            raise Exception(f'fake(): Dont know how to handle: {cmd}')

        # basic run - pass
        with MockVar(sys, 'argv', ['a.py', '-qualdoc']):
            with MockVar(SystemCall, "run_outtxt", fake):
                with self.assertRaises(SystemExit):
                    SortBot().main()

        self.assertEqual(cmd_list, ['gh pr view'])    # should be no other command

        # invalid PR with space
        out_pr = '''
- [X ] TPDB QualDoc
'''
        with MockVar(sys, 'argv', ['a.py', '-qualdoc']):
            with MockVar(SystemCall, "run_outtxt", fake):
                with self.assertRaisesRegex(ErrorUser, 'is an invalid line'):
                    SortBot().main()

        # fail any line
        out_pr = '''
- [ X] blah
- [X] blah2
'''
        with MockVar(sys, 'argv', ['a.py', '-qualdoc']):
            with MockVar(SystemCall, "run_outtxt", fake):
                with self.assertRaisesRegex(ErrorUser, 'is an invalid line'):
                    SortBot().main()

        # fail qualdoc
        out_pr = '''
- [X] blah
- [X] blah2
'''
        with MockVar(sys, 'argv', ['a.py', '-qualdoc']):
            with MockVar(SystemCall, "run_outtxt", fake):
                with self.assertRaisesRegex(ErrorUser, 'is not specified for this PR'):
                    SortBot().main()

    def test_qualdoc(self):
        # non-qualdoc run
        with MockVar(sys, 'argv', ['a.py', 'blah']):
            self.assertEqual(SortBot.qualdoc_check(), 1)

        # qualdoc run
        with MockVar(sys, 'argv', ['a.py', '-qualdoc']):

            # fail case
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, 'yay'))):
                with self.assertRaisesRegex(ErrorUser, 'TPDB Qualdoc'):
                    SortBot.qualdoc_check()

            # pass case
            with MockVar(SystemCall, "run_outtxt", Mock(return_value=(0, '\n[X] TPDB QualDoc\n'))):
                with self.assertRaises(SystemExit):
                    SortBot.qualdoc_check()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
