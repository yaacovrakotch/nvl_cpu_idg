#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Automatic PR Counter
Will be run daily.
"""

import setenv        # must be first in the imports
from gadget.strmore import day_code
import urllib.request
import re
import time
import sys
import csv

try:
    import win32com.client
except ImportError:
    pass


class PRCounter:

    def url_repo(self, repo, pr_cnt, br):
        url = f'https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?repo={repo}&PR_CNT={pr_cnt}&br={br}&code={day_code()}'
        with urllib.request.urlopen(url) as response:
            data = response.read().decode()
            pattern = re.compile(r'<pre>(.*?)</pre>', re.DOTALL)
            data_good = pattern.findall(data)
        pr_count = data_good[-1]
        tp = pr_count.split('\n')
        return tp

    def get_report_file(self, repo):
        report_file = f'//amr.corp.intel.com/ec/proj/mdl/jf/intel/engineering/dev/team_classtp/dashboard/PR_counter/{repo[0]}-{repo[1]}.html'
        return report_file

    def get_csv_file(self, repo):
        csv_file = f'//amr.corp.intel.com/ec/proj/mdl/jf/intel/engineering/dev/team_classtp/dashboard/PR_counter/{repo[0]}-{repo[1]}.csv'
        return csv_file

    def get_csv_file_team(self, repo):
        csv_file = f'//amr.corp.intel.com/ec/proj/mdl/jf/intel/engineering/dev/team_classtp/dashboard/PR_counter/{repo[0]}-{repo[1]}_team.csv'
        return csv_file

    def current_repo(self):
        # Repo data:
        arlu28 = ['arlu28', 75]
        arls68_20A_old = ['arls68', 65]
        arls68_20A = ['arls68', 66]

        # Repo_list = [arlu28, arls68_20A_old, arls68_20A]
        repo_list = [arlu28, arls68_20A]
        return repo_list

    def generate_pr_sum_table(self, repo, tp):
        total_pr = 0
        tp = sorted(tp, reverse=True)
        # Table
        table = "<table border='1' cellspacing='0' style='font-family: Calibri;'>\n"
        table += f"""<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:18px;'><pre>Repo: {repo[0]}; Branch: TP/{repo[1]}</pre></td></tr>"""
        table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right:15px; font-size:16px;'>Test Program</td>
        <td style='padding-right:5px; font-size:16px;'>Released Date</td>
        <td style='padding-right:5px; font-size:16px;'>Number of PRs</td>
        <td style='padding-right:5px; font-size:16px;'>PR List</td>
        </tr>\n"""
        csv_file = self.get_csv_file(repo)
        with open(csv_file, 'w') as f:
            f.write('Test Program,Released Date,Number of PRs,PR List\n')
            for item in tp:
                # print(item)
                if item.strip().startswith('TP_'):
                    # print(item.strip())
                    tp_data = item.strip().split(',')
                    tp_name = tp_data[0].split('_')[1]
                    table += f"""  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                    <td style='padding-right:15px; font-size:16px;'>{tp_data[0]}</td>
                    <td style='text-align: right; font-size:16px;'>{tp_data[1]}</td>
                    <td style='text-align: right; font-size:16px;'>{tp_data[2]}</td>
                    <td style='text-align: right; font-size:16px;'><a href = "https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog=../../infra/torch/PR_reports/{tp_name}.txt"> PR List {tp_name}</a></td>
                    </tr>\n"""
                    f.write(f'{tp_data[0]},{tp_data[1]},{tp_data[2]},https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog=../../infra/torch/PR_reports/{tp_name}.txt')
                    f.write('\n')
                    total_pr += int(tp_data[2])
        table += "</table>\n"
        return table, total_pr

    def pr_sum(self, repo):
        tp = self.url_repo(repo[0], 'SUM', repo[1])
        pr_flag = False
        # Check if the tp data is valid
        for item in tp:
            if item.strip().startswith('TP_'):
                pr_flag = True
                print(item)
                break
        if pr_flag:
            sum_data = self.generate_pr_sum_table(repo, tp)
            table = sum_data[0]
            total_pr = sum_data[1]
            report_file = self.get_report_file(repo)
            print(f'Start writing: {report_file}')
            f = open(report_file, "w")
            f.write("<html style=\"font-family: Calibri; font-size: 16px;\">\n")
            f.write("<head>\n")
            f.write(f"<title>PR Counter Summary</title>\n")
            f.write("</head>")
            f.write("<body>\n")
            f.write(f"<h1>{table}</h1>\n \
                <h2 style = 'font-size: 16px;'>Total number of PRs: {str(total_pr)}</h2>\n</body></html>")
            print(f'Done processing file {report_file}')
            f.close()
        else:
            print(f'ERROR! Can NOT pull the latest data from the repo.')
            print(tp)

    def pr_team(self, repo):
        tp = self.url_repo(repo[0], 'TEAM', repo[1])
        pr_flag = False
        # Check if the tp data is valid
        for item in tp:
            if item.strip().startswith('TP_'):
                pr_flag = True
                print(item)
                break
        if pr_flag:
            csv_file = self.get_csv_file_team(repo)
            with open(csv_file, 'w') as f:
                print(f'Start writing: {csv_file}')
                f.write('Test Program,PR Number,Team,Module\n')
                team_list = ['ARR', 'BinDefinitions', 'EnvFile', 'PORTP', 'TPConfig', 'PSCN', 'Uservar', 'SSIO', 'MIO', 'FUS', 'Shared', 'SCLK', 'UserCode', 'DRV', 'ProgramFlows', 'Misc', 'YBS', 'CLK', 'FUN', 'PTH', 'TPI', 'NSIO', 'revert', 'EnvironmentFile', 'SCN', 'YML', 'SFUN', 'BinMatrix', 'PPR', 'SIO', 'IOEP']
                PR_number_list = []
                team_report = []
                for item in tp:
                    if item.strip().startswith('TP_'):
                        item_temp = item.strip().split(',')
                        TP = item_temp[0].strip()
                        PR_number = item_temp[1].strip()
                        team = item_temp[2].strip()
                        mod = item_temp[3].strip()
                        if PR_number not in PR_number_list:
                            PR_number_list.append(PR_number)
                        if team in team_list:
                            temp = f'{TP}:{PR_number}:{team}:{mod}'
                            team_report.append(temp)
                PR_number_list = list(map(str, sorted(map(int, PR_number_list))))
                team_report.sort()

                for PR in PR_number_list:
                    final_team = []
                    final_mod = []
                    for item in team_report:
                        temp_PR = item.split(':')[1]
                        if temp_PR == PR:
                            TestProgram = item.split(':')[0]
                            team = item.split(':')[2]
                            mod = item.split(':')[3]
                            if not final_team:
                                final_team.append(team)
                            else:
                                if team not in final_team:
                                    final_team.append(team)
                            if not final_mod:
                                final_mod.append(mod)
                            else:
                                if mod not in final_mod:
                                    final_mod.append(mod)
                    mods = '-'.join(final_mod)
                    teams = '-'.join(final_team)
                    if teams != '':
                        f.write(f'{TestProgram},{PR},{teams},{mods}\n')
                print(f'Done processing file {csv_file}')
                f.close()

            # Create a PR summary for easy ordering and display on PowerBI
            tp_series_list = []
            tp_team_dict = {}
            with open(csv_file, 'r') as f:
                next(f)
                csv_reader = f.readlines()
            for line in csv_reader:
                row = line.split(',')
                if row[0][0:6] not in tp_series_list:
                    tp_series_list.append(row[0][0:6])
            tp_series_list.sort()
            for tpName in tp_series_list:
                team_dict = {}
                for line in csv_reader:
                    row = line.split(',')
                    if tpName == row[0][0:6]:
                        team = row[2].split('-')
                        for item in team:
                            if item in team_dict.keys():
                                team_dict[item] = team_dict[item] + 1
                            else:
                                team_dict[item] = 1
                # Set the default value for Team to 0 if the team does not exist in the TP_series
                for temp_team in team_list:
                    if temp_team not in team_dict.keys():
                        team_dict[temp_team] = 0
                tp_team_dict[tpName] = team_dict

            # Write summary data to csv file
            csv_name = csv_file.rsplit('.', 1)[0]
            team_csv_summary = f'{csv_name}_summary.csv'
            with open(team_csv_summary, 'w') as f:
                f.write('TP_Series,Team,NumberOfPRs\n')
                for key, value in tp_team_dict.items():
                    for key1, value1 in value.items():
                        f.write(f'{key},{key1},{value1}\n')
        else:
            print(f'ERROR! Can NOT pull the latest data from the repo.')
            print(tp)

    def main(self):
        repo_list = self.current_repo()
        for repo in repo_list:
            self.pr_sum(repo)
            self.pr_team(repo)


if __name__ == '__main__':  # pragma: no cover
    obj = PRCounter()
    obj.main()
