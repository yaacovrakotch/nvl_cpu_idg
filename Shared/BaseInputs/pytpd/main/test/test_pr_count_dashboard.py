#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
from main.pr_count_dashboard import *
import main.pr_count_dashboard as PRCount
from os.path import join, dirname, abspath
import sys
from unittest.mock import patch


class FakeDate:

    @classmethod
    def today(cls):
        return '2024-01-09'


class TestBasic(TestCase):

    def test_generate_pr_sum_table(self):
        repo = ['arlu28', 75]
        report_file = f'{UT_DIR_REPO}/pr_counter/arlu28-75.html'
        csv_file = f'{UT_DIR_REPO}/pr_counter/arlu28-75.csv'
        golden_report_file = f'{UT_DIR_REPO}/pr_counter/arlu28-75-gold1.html'
        golden_csv_file = f'{UT_DIR_REPO}/pr_counter/arlu28-75-gold1.csv'
        pr_count = PRCounter()
        # check_and_del(actual_file)
        tp = ['TP_75A0B,2024-04-17,209', 'TP_75B0A,2024-04-18,52', 'TP_75B0C,2024-04-19,9']
        with MockVar(pr_count, 'url_repo', Mock(return_value=tp)), \
                MockVar(pr_count, 'get_report_file', Mock(return_value=report_file)), \
                MockVar(pr_count, 'get_csv_file', Mock(return_value=csv_file)):
            pr_count.pr_sum(repo)
        self.assertGoldEqual(report_file, golden_report_file)
        self.assertGoldEqual(csv_file, golden_csv_file)

    def test_generate_pr_team(self):
        repo = ['arlu28', 75]
        csv_file = f'{UT_DIR_REPO}/pr_counter/arlu28-75-team.csv'
        csv_file_summary = f'{UT_DIR_REPO}/pr_counter/arlu28-75-team_summary.csv'
        golden_csv_file = f'{UT_DIR_REPO}/pr_counter/arlu28-75-team-gold1.csv'
        golden_csv_file_summary = f'{UT_DIR_REPO}/pr_counter/arlu28-75-team_summary-gold.csv'
        tp = ['TP_75A0B,100,ARR,ARR', 'TP_75A0B,100,EnvFile,EnvFile', 'TP_75A0B,104,SSIO,SSIO_MPPHY_SXS', 'TP_75H0A,568,TPI,TPI_BASE_XXX']
        pr_count = PRCounter()
        with MockVar(pr_count, 'url_repo', Mock(return_value=tp)), \
                MockVar(pr_count, 'get_csv_file_team', Mock(return_value=csv_file)):
            pr_count.pr_team(repo)
        self.assertGoldEqual(csv_file, golden_csv_file)
        self.assertGoldEqual(csv_file_summary, golden_csv_file_summary)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
