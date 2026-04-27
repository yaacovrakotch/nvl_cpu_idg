#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
import os
import json
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
from gadget.shell import SystemCall
from gadget.getgit import GitHub
from main.nvl_pr_counter import *
from os.path import join, dirname, abspath
import sys
from unittest.mock import patch


class TestBasic(TestCase):

    def test_get_changed_files(self):
        pr_count = PRCounter()
        expect = ['file1.py', 'file2.py', 'dir/file3.py']
        data_out = 'file1.py\nfile2.py\ndir/file3.py'
        # Ensure we're passing a string/number, not a list
        pr_number = '123'  # or 123
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, data_out))):
            data = pr_count.get_changed_files(pr_number)
        self.assertEqual(data, expect)

    def test_pr_sum(self):
        pr_count = PRCounter()
        repo = 'nvl.cpu'
        milestone = {'202546': 'A0'}
        save_output = []
        pr_list = '''[
            {
                "branch": "main",
                "event": "S28C A0 ES1",
                "mergedAt": "2025-10-30T00:00:00Z",
                "number": 1993,
                "title": "[S28C|HX28C|P16C][FUN_CCF_CX816][Update S28C and HX28C plist format to bomgroup|Included CLASS_NVL_P16C in mconfig]",
                "url": "https://github.com/intel-restricted/nvl.cpu/pull/1993"
            },
            {
                "branch": "main",
                "event": "S28C A0 ES1",
                "mergedAt": "2025-10-29T00:00:00Z",
                "number": 1991,
                "title": "[S28C|HX28C|P16C][FUN_CORE|FUN_ATOM|FUN_CCF][ApexTC, IS TorchRule and FUN CORE P16C BomGroup] ",
                "url": "https://github.com/intel-restricted/nvl.cpu/pull/1991"
            }
        ]'''

        expect = [
            {
                'branch': 'main',
                'event': 'S28C A0 ES1',
                'mergedAt': 202544,
                'number': 1993,
                'title': '[S28C|HX28C|P16C][FUN_CCF_CX816][Update S28C and HX28C '
                'plist format to bomgroup|Included CLASS_NVL_P16C in mconfig]',
                'url': 'https://github.com/intel-restricted/nvl.cpu/pull/1993',
                'repo': 'nvl.cpu',
                'teams': ['SCN']
            },
            {
                'branch': 'main',
                'event': 'S28C A0 ES1',
                'mergedAt': 202544,
                'number': 1991,
                'title': '[S28C|HX28C|P16C][FUN_CORE|FUN_ATOM|FUN_CCF][ApexTC, IS '
                'TorchRule and FUN CORE P16C BomGroup] ',
                'url': 'https://github.com/intel-restricted/nvl.cpu/pull/1991',
                'repo': 'nvl.cpu',
                'teams': ['SCN']
            }
        ]
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            os.mkdir(f'{tdir}/nvl.cpu')
            with MockVar(GitHub, 'get_all_branches', Mock(return_value=['main'])), \
                    MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, pr_list))), \
                    MockVar(pr_count, 'get_changed_files', Mock(return_value=['SCN/sdfd.mtpl', 'another_file.py'])), \
                    MockVar(pr_count, 'main_repo_folder', tdir):
                all_prs = pr_count.pr_sum(repo, milestone, save_output)
        print(all_prs)
        self.assertEqual(all_prs, expect)

    def test_main(self):
        pr_count = PRCounter()
        repo = 'nvl.cpu'
        milestone = {'202546': 'A0'}
        read_output = [
            {
                'branch': 'main',
                'event': 'S28C A0 ES1',
                'mergedAt': 202544,
                'number': 1993,
                'title': '[S28C|HX28C|P16C][FUN_CCF_CX816][Update S28C and HX28C '
                'plist format to bomgroup|Included CLASS_NVL_P16C in mconfig]',
                'url': 'https://github.com/intel-restricted/nvl.cpu/pull/1993',
                'repo': 'nvl.cpu',
                'teams': ['SCN']
            }
        ]
        mock_pr_sum = [
            {
                'branch': 'main',
                'event': 'S28C A0 ES1',
                'mergedAt': 202544,
                'number': 1991,
                'title': '[S28C|HX28C|P16C][FUN_CORE|FUN_ATOM|FUN_CCF][ApexTC, IS '
                'TorchRule and FUN CORE P16C BomGroup] ',
                'url': 'https://github.com/intel-restricted/nvl.cpu/pull/1991',
                'repo': 'nvl.cpu',
                'teams': ['SCN']
            }
        ]
        expect = [
            {
                'branch': 'main',
                'event': 'S28C A0 ES1',
                'mergedAt': 202544,
                'number': 1991,
                'repo': 'nvl.cpu',
                'teams': ['SCN'],
                'title': '[S28C|HX28C|P16C][FUN_CORE|FUN_ATOM|FUN_CCF][ApexTC, IS '
                'TorchRule and FUN CORE P16C BomGroup] ',
                'url': 'https://github.com/intel-restricted/nvl.cpu/pull/1991'
            },
            {
                'branch': 'main',
                'event': 'S28C A0 ES1',
                'mergedAt': 202544,
                'number': 1993,
                'repo': 'nvl.cpu',
                'teams': ['SCN'],
                'title': '[S28C|HX28C|P16C][FUN_CCF_CX816][Update S28C and HX28C '
                'plist format to bomgroup|Included CLASS_NVL_P16C in mconfig]',
                'url': 'https://github.com/intel-restricted/nvl.cpu/pull/1993'
            }
        ]
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            mock_milestone_file = join(tdir, 'milestone.json')
            mock_output_file = join(tdir, 'all_prs_data.json')
            mock_milestone_file_data = '''{
                "202527": "S28C A0 PO",
                "202544": "S28C A0 ES1"
            }'''
            File(mock_milestone_file).touch(mock_milestone_file_data, newfile=True)

            os.mkdir(f'{tdir}/nvl.cpu')
            with MockVar(GitHub, 'get_all_branches', Mock(return_value=['main'])), \
                    MockVar(pr_count, 'pr_sum', Mock(return_value=mock_pr_sum)), \
                    MockVar(pr_count, 'read_output_file', Mock(return_value=read_output)), \
                    MockVar(pr_count, 'milestone_file', mock_milestone_file), \
                    MockVar(pr_count, 'repos', ['nvl.cpu']), \
                    MockVar(pr_count, 'output_file', mock_output_file), \
                    MockVar(pr_count, 'main_repo_folder', tdir):
                pr_count.main()
            # Verify the output file was created and contains expected data
            actual_data = json.loads(File(mock_output_file).read())
            self.assertEqual(actual_data, expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
