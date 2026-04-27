#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
The MBOT Dashboard for displaying MBOT job status:
1. Return a clickable link for job result Passed or Failed
2. Provide a capability for moving the job to be the first in the queued if the priority changes
3. Provide all other info like tester, submitter, product and completed time.
4. CGI website displaying all data.
"""
import os
import json
import site
import time
from datetime import datetime
from collections import OrderedDict, defaultdict
from os.path import basename, dirname, realpath
from pprint import pprint, pformat
from gadget.files import File
from gadget.pylog import log
from gadget.tvpv import TvpvEnv
from gadget.strmore import curtime
from main.manager_botos import BotOS, Remote, curtime
import re
import glob


class MBotDB:
    """MBOT DashBoard Info"""
    CGINAME = 'mbot_dashboard.cgi'
    URL = f'https://tvpv.pdx.intel.com/cgi-bin/bots_dashboard/{CGINAME}'
    OPT = {}    # assigned by cgi
    darkmode = False  # Default dark mode is off
    extend = False  # Default extend view is off, show only 7 days data

    def botos_folder_input(self):
        """Return BotOS folder"""
        return f'{BotOS.root}'

    def do_move_to_top(self, botos_folder, jobId, product):
        """Move a queued job to the top when there is a request"""
        sourcename = f'{botos_folder}/pool/{product}/{jobId}.tar.gz'
        if os.path.exists(sourcename):
            all_queued_items = glob.glob(f'{botos_folder}/pool/*/*.tar.gz')
            file_names = [os.path.basename(item) for item in all_queued_items]
            smallest_file_name = min(file_names)
            assign_priority_number = int(smallest_file_name[0:4]) - 1
            newname = f'{assign_priority_number}_{jobId[5:]}.tar.gz'
            File(sourcename).rename(newname)

    def do_cancel_job(self, botos_folder, jobId, product):
        """Remove jobs from the queue when requested"""
        sourcename = f'{botos_folder}/pool/{product}/{jobId}.tar.gz'
        if os.path.exists(sourcename):
            os.remove(sourcename)
        metajobid = BotOS.get_metafname(jobId)
        metafile = f'{botos_folder}/pool/_metadata/{metajobid}.json'
        if os.path.exists(metafile):
            os.remove(metafile)

        File(f'{botos_folder}/logfiles/cancelled.log').logprint(f'{MBotDB.OPT["_user"]}: {product}/{jobId}')
        print(f'{product}/{jobId} is cancelled<br>')
        print(f'Go back to <a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi">dashboard</a>')
        exit(0)

    def process_result_file(self, result_file, job_site=''):
        """
        Docstring for process_result_file for url link
        """
        directory, file_name = os.path.split(result_file)
        _, date_part = os.path.split(directory)
        domain = TvpvEnv.site_to_domain(job_site)
        if job_site == 'BA':
            result_log_file = f"""https://tvpv1.{domain}.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./{date_part}/{file_name}"""
        else:
            result_log_file = f"""https://tvpv.{domain}.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./{date_part}/{file_name}"""
        return result_log_file

    def write_table(self, jobId, value, table):
        """Write the job data to the table"""
        # jobs_dict[job_data] = [product, status, submitter, site, tester, CompleteTime, MoveToTop]
        product = value[0]
        status = value[1]
        submitter = value[2]
        job_site = value[3]
        tester = value[4]
        completedTime = value[5]
        moveToTop = value[6]
        CancelJob = value[7]
        pr_link = value[8]
        ituff = value[9]
        init_log = value[10]
        load_log = value[11]
        comment = value[12]
        log_file_path = ""

        # Get startedTime from jobId
        startedTime = curtime(BotOS.get_timesecs(jobId))
        result_bin = ""

        botos_folder = self.botos_folder_input()
        # If the job is completed (PASSED or FAILED), set the status hyperlink to ituff file and log folder
        if status == 'PASSED' or status == 'FAILED':
            # Set the ituff file if the ituff data avaiable in the json file
            if ituff != '':
                result_file = ituff
            elif init_log != '':
                result_file = init_log
                if status == 'PASSED':
                    status = 'PASSED_INIT'
                else:
                    status = 'FAILED_INIT'
            elif load_log != '':
                result_file = load_log
                if status == 'PASSED':
                    status = 'PASSED_LOAD'
                else:
                    status = 'FAILED_LOAD'
            else:
                result_file = ""
            result_log_file = self.process_result_file(result_file, job_site)

            log_file_path = f"I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/{jobId}"
            status_row = f"""<td style='padding-right: 5px;'><a href="{result_log_file}">{status}</a></td>"""
            log_file_path_row = f"""<td style='padding-right: 5px;'>{log_file_path}</td>"""

            # Get result_bin from completed json file if exists
            if 'SoftBin' in comment:
                # Extract SoftBin value using regex - matches 'SoftBin = 100' where bin is 3-4 characters
                match = re.search(r'SoftBin\s*=\s*(\d{3,4})', comment)
                if match:
                    result_bin = match.group(1)
            elif 'passed INIT' in comment:
                result_bin = 'INIT ONLY: PASSED'
            elif 'INIT failed' in comment:
                result_bin = 'INIT FAILED'
            elif 'Polaris' in comment:
                result_bin = 'Polaris FAILED'
                status = 'POLARIS_FAILED'
                status_row = f"""<td style='padding-right: 5px;'><a href="{result_log_file}">{status}</a></td>"""
        else:
            status_row = f"""<td style='padding-right: 5px;'>{status}</td>"""
            log_file_path_row = f"""<td style='padding-right: 5px; white-space: nowrap;'>{log_file_path}</td>"""

        # Set MoveToTop and CancelJob available for queued jobs only
        if status == 'Queued':
            moveToTop_row = f"""<td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?move_to_top={jobId}&product={product}">{moveToTop}</a></td>"""
            cancelJob_row = f"""<td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?cancel_job={jobId}&product={product}">{CancelJob}</a></td>"""
        else:
            moveToTop_row = f"""<td style='padding-right: 5px;'>{moveToTop}</td>"""
            cancelJob_row = f"""<td style='padding-right: 5px;'>{CancelJob}</td>"""

        # Extract repository name and PR number from GitHub URLs
        # Format: https://github.com/intel-restricted/nvl.gcd/pull/787 -> nvl.gcd-787
        if pr_link and 'github.com' in pr_link and '/pull/' in pr_link:
            url_parts = pr_link.split('/')
            if len(url_parts) >= 5:
                repo_name = url_parts[-3]  # Repository name (e.g., nvl.gcd)
                pr_number = url_parts[-1]  # PR number (e.g., 787)
                short_pr_link = f"{repo_name}-{pr_number}"
            else:
                short_pr_link = pr_link
        else:
            short_pr_link = pr_link
        if pr_link:
            pr_link_row = f"""<td style='padding-right: 5px; white-space: nowrap;'>{f'<a href="{pr_link}" target="_blank">{short_pr_link}</a>'}</td>"""
        else:
            pr_link_row = """<td style='padding-right: 5px; white-space: nowrap;'></td>"""

        if 'FAILED' in status:
            row_bg_color = '#FF6B6B'  # LightRed for failed status
        elif 'PASSED' in status:
            row_bg_color = '#90EE90'  # LightGreen for passed status
        elif status == 'Running':
            row_bg_color = '#FFFF99'  # LightYellow for running status
        else:
            row_bg_color = '#F0F8FF'  # Default color

        # Write a table with the new data
        table += f"""<tr style='padding-right-left: 5px; text-align: left; background-color: {row_bg_color}; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>{jobId}</td>
        <td style='padding-right: 5px; white-space: nowrap;'>{product}</td>
        {status_row}
        <td style='padding-right: 5px; white-space: nowrap;'>{submitter}</td>
        <td style='padding-right: 5px; white-space: nowrap;'>{job_site}</td>
        <td style='padding-right: 5px; white-space: nowrap;'>{tester}</td>
        <td style='padding-right: 5px; white-space: nowrap;'>{startedTime}</td>
        <td style='padding-right: 5px; white-space: nowrap;'>{completedTime}</td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'>{result_bin}</td>
        {moveToTop_row}
        {cancelJob_row}
        {pr_link_row}
        {log_file_path_row}
        </tr>\n"""

        return table

    def return_today_time(self):
        """Return today time"""
        today = datetime.now()
        return today

    def read_json(self, file, kw='email'):
        """Read json and do not error if fail to read"""
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            return {kw: f'{basename(file)} error'}

    def get_json_data(self, data, timestamp):
        """read data, return empty dict if data is not within 7 days, otherwise return the data dict"""
        submitter = data.get('email', '')
        product = data.get('pkg', '')
        job_site = data.get('site', '')
        tester = data.get('tester', '')
        pr_link = data.get('url', '')
        ituff = data.get('Ituff file', '')
        init_log = data.get('INIT log', '')
        load_log = data.get('Load log', '')
        comment = data.get('comment', '')
        # Convert the timestamp to a human-readable format
        CompleteTime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        if self.extend is False:
            # check if currentTime - completeTime > 7 days, if yes, ignore the data
            current_time_epoch = int(time.time())
            if current_time_epoch - timestamp > 7 * 24 * 3600:
                return []
        MoveToTop = ''
        CancelJob = ''
        code = str(data.get('code', -1))
        if code == "0":
            status = 'PASSED'
        elif code == "-1":
            status = 'FAILED - Result is not available. return -1'
        else:
            status = 'FAILED'
        return [product, status, submitter, job_site, tester, CompleteTime, MoveToTop, CancelJob, pr_link, ituff, init_log, load_log, comment]

    def main(self):
        """Main entry point"""
        botos_folder = self.botos_folder_input()
        pool = f'{botos_folder}/pool'

        # Check if dark mode is requested
        if 'darkmode' in self.OPT and self.OPT['darkmode'].lower() == 'true':
            self.darkmode = True

        # Check if extend view is requested
        if 'extend' in self.OPT and self.OPT['extend'].lower() == 'true':
            self.extend = True

        # Take care of move_to_top command
        if 'move_to_top' in self.OPT:
            self.do_move_to_top(botos_folder, self.OPT['move_to_top'], self.OPT['product'])

        # Take care of CancelJob command
        if 'cancel_job' in self.OPT:
            self.do_cancel_job(botos_folder, self.OPT['cancel_job'], self.OPT['product'])

        queue_jobs = []
        complete_jobs = []
        metadata_jobs = []
        running_jobs_dict = {}
        queue_jobs_dict = {}
        completed_jobs_dict = {}

        # Show loading message for MBOT data retrieval
        print('<div id="loading-message" style="text-align: center; font-size: 18px; padding: 20px; color: #0000FF;">Retrieving data from botos... Please wait...</div>')
        print('<script>document.body.scrollTop = 0; document.documentElement.scrollTop = 0;</script>')

        # Get the queue jobs
        queue_jobs_raw = glob.glob(f'{pool}/*/*.tar.gz*')
        for job in queue_jobs_raw:
            temp_job = os.path.basename(job).split('.')[0]
            queue_jobs.append(temp_job)

        # Get the running jobs
        metadata_jobs_json = glob.glob(f'{pool}/_metadata/*.json')
        for job in metadata_jobs_json:
            temp_job = os.path.basename(job).split('.')[0]
            metadata_jobs.append(temp_job)

        for job_data in metadata_jobs:
            queue_job_flag = False
            for file in metadata_jobs_json:
                if job_data in file:
                    data = self.read_json(file)
                    submitter = data.get('email', '')
                    product = data.get('pkg', '')
                    job_site = data.get('site', '')
                    tester = data.get('tester', '')
                    pr_link = data.get('url', '')
                    CompleteTime = ''
                    MoveToTop = ''
                    CancelJob = ''
                    ituff = ''
                    init_log = ''
                    load_log = ''
                    comment = ''
                    for job in queue_jobs:
                        if job_data in job:
                            status = 'Queued'
                            MoveToTop = 'MoveToTop'
                            CancelJob = 'CancelJob'
                            queue_jobs_dict[job] = [product, status, submitter, job_site, tester, CompleteTime, MoveToTop, CancelJob, pr_link, ituff, init_log, load_log, comment]
                            queue_job_flag = True
                            break
                    if not (queue_job_flag):
                        status = 'Running'
                        running_jobs_dict[job_data] = [product, status, submitter, job_site, tester, CompleteTime, MoveToTop, CancelJob, pr_link, ituff, init_log, load_log, comment]
                    break
        # Sorted running_jobs by the last character, then the rest alphabetical
        sorted_running_jobs = sorted(running_jobs_dict.items(), key=lambda x: (x[0][-1], x[0][:-1]))
        # Sorted queued_jobs by the first 4 characters, last character, then the rest alphabetical
        sorted_queued_jobs = sorted(queue_jobs_dict.items(), key=lambda x: (x[0][:4], x[0][-1], x[0][5:-2]))

        # Get Completed jobs
        complete_jobs_json = glob.glob(f'{botos_folder}/completed/*.json')
        for job in complete_jobs_json:
            temp_job = os.path.basename(job).split('.')[0]
            complete_jobs.append(temp_job)
        for job_data in complete_jobs:
            for file in complete_jobs_json:
                if job_data in file:
                    data = self.read_json(file)
                    # Get the timestamp of the file
                    timestamp = os.path.getmtime(file)
                    return_data = self.get_json_data(data, timestamp)
                    if return_data:
                        completed_jobs_dict[job_data] = return_data

        # Get remote completed jobs
        completed_remote_jobs = Remote(check=True).read_completed()
        for site_itr in completed_remote_jobs:
            for file_name in completed_remote_jobs[site_itr]:
                job_data = os.path.basename(file_name).split('.')[0]
                data = completed_remote_jobs[site_itr][file_name]
                # Get the timestamp of the file by file name, workaround since we cannot stat the file
                timestamp_epoch = file_name.split('_')[0]
                timestamp_epoch_int = int(int(timestamp_epoch) / 1000)
                return_data = self.get_json_data(data, timestamp_epoch_int)
                if return_data:
                    completed_jobs_dict[job_data] = return_data

        # Sort the completed_jobs_dict by completedTime
        sorted_completed_jobs = sorted(completed_jobs_dict.items(), key=lambda x: x[1][5], reverse=True)

        # Table ==============================
        today = self.return_today_time()
        header1 = f'MBOT DASHBOARD {today}'
        headerstyle = "<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>"

        # Add dark mode CSS with conditional application
        dark_mode_styles = """
<style>
/* Default (light) styles are already present in your table */

/* Dark mode styles */
.dark-mode {
    background-color: #181818 !important;
    color: #e0e0e0 !important;
}
.dark-mode table {
    background-color: #222 !important;
    color: #e0e0e0 !important;
}
.dark-mode td, .dark-mode th {
    background-color: #222 !important;
    color: #e0e0e0 !important;
    border-color: #444 !important;
}
.dark-mode tr {
    background-color: #222 !important;
    color: #e0e0e0 !important;
}
.dark-mode a {
    color: #80bfff !important;
}
/* Add this for visited links in dark mode */
.dark-mode a:visited {
    color: #b080ff !important;
}
</style>
"""

        # Apply dark mode conditionally
        if hasattr(self, 'darkmode') and self.darkmode:
            dark_mode_styles += """
<script>
document.addEventListener('DOMContentLoaded', function() {
    document.body.classList.add('dark-mode');
});
</script>
"""

        table = dark_mode_styles
        # Add CSS to ensure single line rows for MBOT table
        table += """
<style>
#mbot-dashboard {
    table-layout: auto;
    width: 100%;
}
#mbot-dashboard td, #mbot-dashboard th {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
#mbot-dashboard tr {
    white-space: nowrap;
}
/* Filter input styling for MBot dashboard */
.dark-mode #mbot-dashboard input {
    background-color: #333 !important;
    color: #e0e0e0 !important;
    border-color: #555 !important;
}
.dark-mode #mbot-dashboard input::placeholder {
    color: #999 !important;
}
</style>
"""
        table += "<table id='mbot-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>\n"
        table += f"<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'>"
        table += f"<th colspan='13' style ='font-size:15px;'>{header1} <a href='https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?tester=True'>(Goto Tester Dashboard)</a></th></tr>"

        # Add filter row for MBOT dashboard
        filter_row = f"""{headerstyle.replace('background-color: #F0F8FF', 'background-color: #E6F3FF')}
        <th style="padding: 2px;"><input type="text" id="filter0" placeholder="Filter Job ID" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter1" placeholder="Filter Product" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter2" placeholder="Filter Status" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter3" placeholder="Filter Submitter" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter4" placeholder="Filter Site" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter5" placeholder="Filter Tester" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter6" placeholder="Filter Started" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter7" placeholder="Filter Completed" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter8" placeholder="Filter Result Bin" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter9" placeholder="Filter Move" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter10" placeholder="Filter Cancel" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter11" placeholder="Filter PR Link" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter12" placeholder="Filter Log Path" onkeyup="filterMbotTable()" style="width: 100%; font-size: 12px;"></th>
        </tr>"""
        table += filter_row

        header = f"""{headerstyle}
        <th>Job Id</th>
        <th>Product</th>
        <th>Status</th>
        <th>Submitter</th>
        <th>Site</th>
        <th>Tester</th>
        <th>Started Time</th>
        <th>Completed Time</th>
        <th>Result Bin</th>
        <th>MoveToTop</th>
        <th>CancelJob</th>
        <th>PR Link</th>
        <th>LogFilePath</th>
        </tr></thead>\n"""
        table += header
        table += "<tbody>\n"
        all_jobs = [sorted_running_jobs, sorted_queued_jobs, sorted_completed_jobs]
        for jobs in all_jobs:
            for key, value in jobs:
                jobId = key
                table = self.write_table(jobId, value, table)
        table += "</tbody>\n"
        table += "</table>\n"
        table += '<button onclick="clearAllMbotFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>\n'
        table += "<br>"
        table += 'BotOS Wiki <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage</a>'

        # Add JavaScript for MBot dashboard filtering
        mbot_script = """
<script>
function filterMbotTable() {
  const table = document.getElementById("mbot-dashboard");
  const tbody = table.tBodies[0];
  const rows = tbody.rows;

  // Get all filter values
  const filters = [];
  for (let i = 0; i < 13; i++) {
    const filterInput = document.getElementById('filter' + i);
    filters[i] = filterInput ? filterInput.value.toLowerCase() : '';
  }

  // Filter each row
  for (let i = 0; i < rows.length; i++) {
    let showRow = true;
    const row = rows[i];

    // Check each column against its filter
    for (let j = 0; j < 13 && showRow; j++) {
      if (filters[j] && row.cells[j]) {
        const cellText = row.cells[j].innerText.toLowerCase();
        if (cellText.indexOf(filters[j]) === -1) {
          showRow = false;
        }
      }
    }

    // Show/hide row based on filter results
    row.style.display = showRow ? '' : 'none';
  }

  // Update row count display
  updateMbotRowCount();
}

function updateMbotRowCount() {
  const table = document.getElementById("mbot-dashboard");
  const tbody = table.tBodies[0];
  const rows = tbody.rows;
  let visibleCount = 0;

  for (let i = 0; i < rows.length; i++) {
    if (rows[i].style.display !== 'none') {
      visibleCount++;
    }
  }

  // Update or create row count display
  let countDisplay = document.getElementById('mbot-row-count');
  if (!countDisplay) {
    countDisplay = document.createElement('div');
    countDisplay.id = 'mbot-row-count';
    countDisplay.style.cssText = 'text-align: right; padding: 5px; font-weight: bold; color: #666;';
    table.parentNode.insertBefore(countDisplay, table.nextSibling);
  }
  countDisplay.textContent = `Showing ${visibleCount} of ${rows.length} jobs`;
}

function clearAllMbotFilters() {
  for (let i = 0; i < 13; i++) {
    const filterInput = document.getElementById('filter' + i);
    if (filterInput) {
      filterInput.value = '';
    }
  }
  filterMbotTable();
}

// Initialize row count on page load for MBot dashboard
document.addEventListener('DOMContentLoaded', function() {
  // Hide loading message when page loads
  const loadingMsg = document.getElementById('loading-message');
  if (loadingMsg) {
    loadingMsg.style.display = 'none';
  }
  setTimeout(updateMbotRowCount, 100);
});
</script>
"""
        table += mbot_script

        print(table)
        return table


class TesterStatusDB:
    """Tester Status DashBoard Info"""
    CGINAME = 'mbot_dashboard.cgi'
    URL = f'https://tvpv.pdx.intel.com/cgi-bin/bots_dashboard/{CGINAME}'
    OPT = {}    # assigned by cgi
    darkmode = False  # Default dark mode is off
    site = ''  # Default site is set to JF

    def tester_folder_input(self):
        """Return tester info folder"""
        return f'{BotOS.root}/testers'

    def testers_path(self, folder_path):
        """Return the testers folder path"""
        subfolders = []
        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    folder_name = entry.name
                    if 'JF' in folder_name or 'jf' in folder_name:
                        subfolders.append(entry.path)
        return subfolders

    def get_time_since_updated(self, status_file='', timestamp=0):
        """
        Get time since the status file updated.
        :param status_file: <status>.status file
        :return: string, in hours
        """
        if timestamp != 0:
            # time in second since the date.now()
            delta_hours = timestamp / 3600
            time_since_updated = f"{delta_hours:.2f}"
            return time_since_updated
        else:
            try:
                timestamp = os.path.getmtime(status_file)
            except Exception:
                return 100000

            current_time = datetime.now()
            delta_time = current_time - datetime.fromtimestamp(timestamp)
            delta_hours = delta_time.total_seconds() / 3600
            time_since_updated = f"{delta_hours:.2f}"
            return time_since_updated

    def get_job_submitter(self, job_id):
        """Get job submitter from job_id"""
        if job_id == '':
            return ''
        job_submitter_file = f'{BotOS.root}/pool/_metadata/{job_id}.json'
        if os.path.exists(job_submitter_file):
            with open(job_submitter_file, 'r') as f:
                data = json.load(f)
                job_submitter = data.get('email', '')
                return job_submitter
        return ''

    def write_table(self, product, status, tester_name, table, expiry_time='', team_info='', tester_location='', tester_type='TPBOT/MBOT/TEAMBOT', time_since_updated='', job_id='', job_submitter='', goldlot_info='', special_notes=''):
        """Write the tester data to the table"""

        # Convert time_since_updated to float and check if > 6 for red highlighting or time_since_updated > 1 for non-TEAMBOT
        # or the status is 'noresponse' or 'reserved'.
        try:
            time_since_updated_float = float(time_since_updated) if time_since_updated else 0
            should_highlight_red = (time_since_updated_float > 1 and tester_type != 'TEAMBOT') or status == 'noresponse' or time_since_updated_float > 6
        except (ValueError, TypeError):
            time_since_updated_float = 0
            should_highlight_red = False

        if status == 'reserved':
            row_bg_color = '#FFB347'  # LightOrange for reserved status
        elif should_highlight_red:
            row_bg_color = '#FF6B6B'  # LightRed for noresponse or reserved status or time_since_updated > threshold
        elif status == 'stopped':
            row_bg_color = '#FFB6C1'  # Lightpink for stopped status
        elif status == 'down':
            row_bg_color = '#808080'  # gray for down status
        elif status == 'running':
            row_bg_color = '#90EE90'  # LightGreen for running status
        elif status == 'occupied':
            row_bg_color = '#FFFF99'  # LightYellow for occupied status
        else:
            row_bg_color = '#F0F8FF'  # Default color

        # remove @intel.com in the submitter name
        job_submitter = job_submitter.replace('@intel.com', '') if job_submitter else ''
        # Write a table with the new data
        table += f"""<tr style='padding-right-left: 5px; text-align: left; background-color: {row_bg_color}; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{product}</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{self.site}</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{tester_name}</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{status}</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>{time_since_updated}</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>{expiry_time}</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{team_info}</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{job_submitter}</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{job_id}</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>{tester_type}</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>{tester_location}</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>{goldlot_info}</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>{special_notes}</td>
        </tr>\n"""
        return table

    def return_today_time(self):
        """Return today time"""
        today = datetime.now()
        return today

    def tester_info_compare(self, current_tester_info, prev_tester_info):
        """Compare current and previous tester information"""
        if current_tester_info != prev_tester_info:
            log.info("Tester info has changed between current and previous versions")
            # Log specific differences
            for tester_name in set(current_tester_info.keys()) | set(prev_tester_info.keys()):
                if tester_name not in prev_tester_info:
                    log.info(f"New tester added: {tester_name}: {current_tester_info[tester_name]}")
                elif tester_name not in current_tester_info:
                    log.info(f"Tester removed: {tester_name}: {prev_tester_info[tester_name]}")
                elif current_tester_info[tester_name] != prev_tester_info[tester_name]:
                    if current_tester_info[tester_name] == '':
                        log.info(f"Tester location changed: {tester_name}: {prev_tester_info[tester_name]} to No-assigned-Location")
                    else:
                        log.info(f"Tester location changed: {tester_name}: {prev_tester_info[tester_name]} to {current_tester_info[tester_name]}")

    def generate_dashboard_local(self, tester_folder, tester_dir, table):
        """
        Generate the tester dashboard locally. Assuming local is JF.
        """
        tester_info_dict = {}
        tester_info_json = f'{tester_folder}/tester_info.json'
        for tester in tester_dir:
            tester_name = os.path.basename(tester)
            tester_info = [f for f in glob.glob(f'{tester}/*.info') if not f.endswith('.package.info')]
            # Get tester_type
            tester_type = 'TPBOT/MBOT/TEAMBOT'
            if len(tester_info) > 0:
                info_file = tester_info[0]
                if os.path.basename(info_file).split('.')[0] == 'type1':
                    tester_type = 'TPBOT/MBOT'
                elif os.path.basename(info_file).split('.')[0] == 'teambotonly':
                    tester_type = 'TEAMBOT'
            # Get package.info
            info_files = glob.glob(f'{tester}/*.package.info')
            if len(info_files) > 0:
                info_file = info_files[0]
            else:
                continue
            # get product
            product = (os.path.basename(info_file)).split('.')[0]
            if product.strip() == 'sim':
                tester_type = 'OFFLINE BOT'
            # Get tester status
            status_files = glob.glob(f'{tester}/*.status')
            if len(status_files) > 0:
                status_file = status_files[0]
            else:
                status_file = 'unknown.status'
            status = (os.path.basename(status_file)).split('.')[0]
            # Get the timestamp of the status file and calculate the delta_time in hours
            time_since_updated = self.get_time_since_updated(status_file)
            if float(time_since_updated) > 1.0 and status == 'idle':
                status = 'noresponse'
            # if exists tester/reserved file, then set status to reserved.
            reserved_file = f'{tester}/reserved'
            if os.path.exists(reserved_file):
                status = 'reserved'

            # Get Expiry Time
            expiry_files = glob.glob(f'{tester}/expiry.*.txt')
            if len(expiry_files) > 0:
                temp_file = os.path.basename(expiry_files[0])
                expiry_time = curtime(int(temp_file.split('.')[1]))
            else:
                expiry_time = ''
            # Get Team information
            team_file = glob.glob(f'{tester}/*.team')
            if len(team_file) > 0:
                team_info = (os.path.basename(team_file[0])).split('.')[0]
            else:
                team_info = ''
            # If team_info is empty, get the forecasted team from the team allocation pool.
            if team_info == '':
                team_allocation_file = f'{BotOS.root}/tpbot_count/_teambots_allocation.{product}.json'
                if os.path.exists(team_allocation_file) and tester_type == 'TEAMBOT':
                    with open(team_allocation_file, 'r') as f:
                        team_data = json.load(f)
                    current_tester_allocation = team_data.get('result', {})
                    for key, value in current_tester_allocation.items():
                        if tester_name in key:
                            if value == '':
                                team_info = 'Any'
                            else:
                                if value.strip() == 'analog' or value.strip() == 'digital':
                                    team_info = f'({value.strip().capitalize()})'
                                else:
                                    team_info = f'({value.strip().upper()})'
            # Get tester location.
            test_location_files = f'{tester_folder}/CurrentStatus.txt'
            if os.path.exists(test_location_files):
                with open(test_location_files, 'r') as f:
                    data_lines = f.readlines()
                for line in data_lines:
                    if tester_name in line:
                        temp_tester_location = line.split(',')[1].strip()
                        if 'X6HDMT' in temp_tester_location:
                            tester_location = f'{temp_tester_location[11:13]}-{temp_tester_location[21:23]}-{temp_tester_location[25]}'
                        else:
                            tester_location = ''
                        break
                else:
                    tester_location = ''
            else:
                tester_location = ''
            tester_info_dict[tester_name] = tester_location
            # Get jobId
            job_id_file = glob.glob(f'{tester}/*.tar.gz')
            if job_id_file:
                job_id = os.path.basename(job_id_file[0]).split('.')[0].split('_', 1)[1]
            else:
                job_id = ''
            # Get job submitter
            job_submitter = self.get_job_submitter(job_id)
            # Get goldlot info
            goldlot_file = glob.glob(f'{tester}/*.gold')
            if goldlot_file:
                sourcelot = os.path.basename(goldlot_file[0]).split('.')[0].split('_')[0]
                tray_number = os.path.basename(goldlot_file[0]).split('.')[0].split('_')[1]
                goldlot_info = f'sourcelot: {sourcelot}, tray#: {tray_number}'
            else:
                goldlot_info = ''
            # Get special_note file *.notes on the tester if any.
            special_note_files = glob.glob(f'{tester}/*.notes')
            if len(special_note_files) > 0:
                special_note_file = os.path.basename(special_note_files[0])
                special_notes = special_note_file.split('.')[0]
            else:
                special_notes = ''
            # Write the table
            table = self.write_table(product, status, tester_name, table, expiry_time, team_info, tester_location, tester_type, time_since_updated, job_id, job_submitter, goldlot_info, special_notes)
        with open(tester_info_json, 'w') as f:
            json.dump(tester_info_dict, f, indent=4, sort_keys=True)

        # Compare tester_info.json with tester_info_prev.json
        tester_info_prev_json = f'{tester_folder}/tester_info_prev.json'
        if os.path.exists(tester_info_prev_json):
            try:
                with open(tester_info_prev_json, 'r', encoding='utf-8') as f:
                    prev_tester_info = json.load(f)
                # Compare the two dictionaries
                self.tester_info_compare(tester_info_dict, prev_tester_info)
            except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
                log.error(f"Error comparing tester info files: {e}")
        else:
            log.info("Previous tester info file not found, skipping comparison")
        return table

    def sixshot(self):
        """
        Return the link to the placement xls for tester status
        Taylor request
        """
        url = 'https://intel.sharepoint.com/:x:/r/sites/nvlpdqeexecution/Shared%20Documents/General/Sixshot%20MIR-MRS%20Placement.xlsx?d=w9ee14a72869d4a0bbec4e7ecdeccaccc&csf=1&web=1&e=FTcsT2'
        return f' (<a href="{url}">Sixshot MIR-MRS Placement xls link</a>)'

    def generate_dashboard_remote(self, tester_folder, table):
        """
        For FM and PG tester site, we need to access the Remote()
        tester_data = {(site, tester): {fname: age}}
        For remote testers, we need to simulate the file paths since we only have filenames and ages
        We'll use the filename as both info_file and status_file since write_table extracts basename anyway
        """
        remote = Remote(check=True)
        tester_data = remote.get_tester_files()
        if tester_data:
            # Filter tester_data to only include testers from self.site
            filtered_tester_data = {(tester_site, tester): data for (tester_site, tester), data in tester_data.items() if tester_site == self.site}

            # Process the filtered tester data
            for (tester_site, tester_name), tester_files in filtered_tester_data.items():
                # Check if this tester has package info files
                package_info_files = [fname for fname in tester_files.keys() if fname.endswith('.package.info')]
                if not package_info_files:
                    continue
                info_file = package_info_files[0]  # Use the first package.info file

                # Determine tester type
                tester_type = 'TPBOT/MBOT/TEAMBOT'
                if 'type1.info' in tester_files:
                    tester_type = 'TPBOT/MBOT'
                elif 'teambotonly.info' in tester_files:
                    tester_type = 'TEAMBOT'
                # get product
                product = (os.path.basename(info_file)).split('.')[0]
                if product.strip() == 'sim':
                    tester_type = 'OFFLINE BOT'
                # Get status file
                status_files = [fname for fname in tester_files.keys() if fname.endswith('.status')]
                status_file = status_files[0] if status_files else 'unknown.status'
                timestamp = tester_files.get(status_file, 0)
                status = (os.path.basename(status_file)).split('.')[0]
                # Get the timestamp of the status file and calculate the delta_time in hours
                time_since_updated = self.get_time_since_updated(status_file, timestamp)
                if float(time_since_updated) > 1.0 and status == 'idle':
                    status = 'noresponse'
                # if exists tester/reserved file, then set status to reserved.
                reserved_file = [fname for fname in tester_files.keys() if fname.startswith('reserved')]
                if reserved_file:
                    status = 'reserved'
                # Get Expiry Time
                expiry_files = [fname for fname in tester_files.keys() if fname.startswith('expiry.')]
                expiry_file = expiry_files[0] if expiry_files else ''
                if expiry_file:
                    temp_file = os.path.basename(expiry_file)
                    expiry_time = curtime(int(temp_file.split('.')[1]))
                else:
                    expiry_time = ''
                # Get Team information
                team_info = ''
                team_files = [fname for fname in tester_files.keys() if fname.endswith('.team')]
                if team_files:
                    team_info = (os.path.basename(team_files[0])).split('.')[0]
                # If team_info is empty, get the forecasted team from the team allocation pool.
                if team_info == '':
                    team_allocation_file = f'{BotOS.root}/tpbot_count/_teambots_allocation.{product}.json'
                    if os.path.exists(team_allocation_file) and tester_type == 'TEAMBOT':
                        with open(team_allocation_file, 'r', encoding='utf-8') as f:
                            team_data = json.load(f)
                        current_tester_allocation = team_data.get('result', {})
                        for key, value in current_tester_allocation.items():
                            if tester_name in key:
                                if value == '':
                                    team_info = 'Any'
                                else:
                                    if value.strip() == 'analog' or value.strip() == 'digital':
                                        team_info = f'({value.strip().capitalize()})'
                                    else:
                                        team_info = f'({value.strip().upper()})'
                # Get tester location
                test_location_files = f'{tester_folder}/CurrentStatus_{tester_site}.txt'
                if os.path.exists(test_location_files):
                    with open(test_location_files, 'r') as f:
                        data_lines = f.readlines()
                    for line in data_lines:
                        if tester_name in line:
                            temp_tester_location = line.split(',')[1].strip()
                            if 'X6HDMT' in temp_tester_location:
                                tester_location = f'{temp_tester_location[11:13]}-{temp_tester_location[21:23]}-{temp_tester_location[25]}'
                            else:
                                tester_location = ''
                            break
                    else:
                        tester_location = ''
                else:
                    tester_location = ''

                # Get jobId
                job_id_file = [fname for fname in tester_files.keys() if fname.endswith('.tar.gz')]
                job_id = ''
                if job_id_file:
                    job_id = os.path.basename(job_id_file[0]).split('.')[0].split('_', 1)[1]
                else:
                    job_id = ''
                # Get job submitter
                job_submitter = self.get_job_submitter(job_id)
                # Get goldlot info
                goldlot_file = [fname for fname in tester_files.keys() if fname.endswith('.gold')]
                if goldlot_file:
                    sourcelot = os.path.basename(goldlot_file[0]).split('.')[0].split('_')[0]
                    tray_number = os.path.basename(goldlot_file[0]).split('.')[0].split('_')[1]
                    goldlot_info = f'sourcelot: {sourcelot}, tray#: {tray_number}'
                else:
                    goldlot_info = ''
                # Get special_note file *.notes on the tester if any.
                special_note_file = [fname for fname in tester_files.keys() if fname.endswith('.notes')]
                if special_note_file:
                    special_note_file = os.path.basename(special_note_file[0])
                    special_notes = special_note_file.split('.')[0]
                else:
                    special_notes = ''
                # Write table
                table = self.write_table(product, status, tester_name, table, expiry_time, team_info, tester_location, tester_type, time_since_updated, job_id, job_submitter, goldlot_info, special_notes)
        else:
            table += "<tr><td colspan='6' style='text-align: center;'>No tester data available for this site.</td></tr>"
        return table

    def main(self):
        """Main entry point"""

        # Check if site is requested
        all_sites = ['JF', 'FM', 'PG', 'IDC', 'BA']
        remote_sites = [site for site in all_sites if site != 'JF']
        if 'site' in self.OPT:
            self.site = self.OPT['site'].upper()
            if self.site not in all_sites:
                self.site = ''
                log.info(f'Invalid site specified: {self.OPT["site"]}, or site is not specified. Defaulting to all sites {format(all_sites)}')

        tester_folder = self.tester_folder_input()

        # Check if dark mode is requested
        if 'darkmode' in self.OPT and self.OPT['darkmode'].lower() == 'true':
            self.darkmode = True

        # Getting all subfolders
        tester_dir = self.testers_path(tester_folder)

        # Table ==============================
        today = self.return_today_time()
        header1 = f'TESTERS STATUS DASHBOARD {today}{self.sixshot()}'
        headerstyle = "<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>"

        # Add dark mode CSS with conditional application
        dark_mode_styles = """
<style>
/* Default (light) styles are already present in your table */

/* Dark mode styles */
.dark-mode {
    background-color: #181818 !important;
    color: #e0e0e0 !important;
}
.dark-mode table {
    background-color: #222 !important;
    color: #e0e0e0 !important;
}
.dark-mode td, .dark-mode th {
    background-color: #222 !important;
    color: #e0e0e0 !important;
    border-color: #444 !important;
}
.dark-mode tr {
    background-color: #222 !important;
    color: #e0e0e0 !important;
}
.dark-mode a {
    color: #80bfff !important;
}
/* Add this for visited links in dark mode */
.dark-mode a:visited {
    color: #b080ff !important;
}
</style>
"""

        # Apply dark mode conditionally
        if hasattr(self, 'darkmode') and self.darkmode:
            dark_mode_styles += """
<script>
document.addEventListener('DOMContentLoaded', function() {
    document.body.classList.add('dark-mode');
});
</script>
"""

        table = dark_mode_styles
        # Add CSS to ensure single line rows
        table += """
<style>
#tester-dashboard {
    table-layout: auto;
    width: 100%;
}
#tester-dashboard td, #tester-dashboard th {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
#tester-dashboard tr {
    white-space: nowrap;
}
</style>
"""
        table += "<table id='tester-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>\n"
        table += f"<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><th colspan='13' style ='font-size:15px;'><pre>{header1}</pre></th></tr>"

        # Add filter row
        filter_row = f"""{headerstyle.replace('background-color: #F0F8FF', 'background-color: #E6F3FF')}
        <th style="padding: 2px;"><input type="text" id="filter0" placeholder="Filter Product" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter1" placeholder="Filter Site" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter2" placeholder="Filter Tester" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter3" placeholder="Filter Status" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter4" placeholder="Filter Hours" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter5" placeholder="Filter Expiry" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter6" placeholder="Filter Team" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter7" placeholder="Filter Submitter" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter8" placeholder="Filter Job ID" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter9" placeholder="Filter Type" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter10" placeholder="Filter Location" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter11" placeholder="Filter Goldlot" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        <th style="padding: 2px;"><input type="text" id="filter12" placeholder="Filter Notes" onkeyup="filterTable()" style="width: 100%; font-size: 12px;"></th>
        </tr>"""
        table += filter_row

        header = f"""{headerstyle}
        <th onclick="sortTable(0)" style="padding-right: 5px; padding-left: 5px;">Product</th>
        <th onclick="sortTable(1)" style="padding-right: 5px; padding-left: 5px;">Site</th>
        <th onclick="sortTable(2)" style="padding-right: 5px; padding-left: 5px;">Tester</th>
        <th onclick="sortTable(3)" style="padding-right: 5px; padding-left: 5px;">Status</th>
        <th onclick="sortTable(4)" style="padding-right: 5px; padding-left: 5px;">LastUpdateHrs</th>
        <th onclick="sortTable(5)" style="padding-right: 5px; padding-left: 5px;">Expiry Time (hours)</th>
        <th onclick="sortTable(6)" style="padding-right: 5px; padding-left: 5px;">Team</th>
        <th onclick="sortTable(7)" style="padding-right: 5px; padding-left: 5px;">Job Submitter</th>
        <th onclick="sortTable(8)" style="padding-right: 5px; padding-left: 5px;">Job ID</th>
        <th onclick="sortTable(9)" style="padding-right: 5px; padding-left: 5px;">Tester Type</th>
        <th onclick="sortTable(10)" style="padding-right: 5px; padding-left: 5px;">Tester Location</th>
        <th onclick="sortTable(11)" style="padding-right: 5px; padding-left: 5px;">Goldlot info</th>
        <th onclick="sortTable(12)" style="padding-right: 5px; padding-left: 5px;">Special Notes</th>
        </tr></thead>\n"""
        table += header
        table += "<tbody>\n"
        if self.site == 'JF':
            table = self.generate_dashboard_local(tester_folder, tester_dir, table)

        elif self.site in remote_sites:
            # For FM and PG tester site, we need to access the Remote()
            # tester_data = {(site, tester): {fname: age}}
            # For remote testers, we need to simulate the file paths since we only have filenames and ages
            # We'll use the filename as both info_file and status_file since write_table extracts basename anyway
            print(f'<div id="loading-message" style="text-align: center; font-size: 18px; padding: 20px; color: #0000FF;">Retrieving data from {self.site}... Please wait...</div>')
            print('<script>document.body.scrollTop = 0; document.documentElement.scrollTop = 0;</script>')
            table = self.generate_dashboard_remote(tester_folder, table)
        else:
            # If no site is specified, generate for all sites
            # Show loading message
            print('<div id="loading-message" style="text-align: center; font-size: 18px; padding: 20px; color: #0000FF;">Retrieving data from all sites... Please wait...</div>')
            print('<script>document.body.scrollTop = 0; document.documentElement.scrollTop = 0;</script>')

            for bot_site in all_sites:
                self.site = bot_site
                if self.site == 'JF':
                    table = self.generate_dashboard_local(tester_folder, tester_dir, table)
                elif self.site in remote_sites:
                    table = self.generate_dashboard_remote(tester_folder, table)

        table += "</tbody>\n"
        table += "</table>\n"
        table += '<button onclick="clearAllFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>\n'
        table += "<br>\n"
        table += '<br> Goto <a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi">MBOT Dashboard</a></br>\n'
        table += '<br> Goto <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">BotOS Wiki</a></br>\n'
        table += '<br> Notes: A Teambot session is 6 hours long. Each time you renew is 2 hours long. Please pay attention to the time limit.</br>\n'
        table += '<br> *(team-name) means this tester will be allocated to the mentioned team. Ex: (Analog) means this tester will be allocated to Analog team.</br>\n'
        table += '<br> *This (team-name) is updated based on the current allocation and will be changed if the current tester allocation changes.</br>\n'

        script_body = """<script>
// Hide loading message when page loads
document.addEventListener('DOMContentLoaded', function() {
    const loadingMsg = document.getElementById('loading-message');
    if (loadingMsg) {
        loadingMsg.style.display = 'none';
    }
    // Initialize row count
    setTimeout(updateRowCount, 100);
});

let sortDirection = {};

function sortTable(colIndex) {
  const table = document.getElementById("tester-dashboard");
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.rows);
  const isAsc = !sortDirection[colIndex];
  sortDirection[colIndex] = isAsc;

  rows.sort((a, b) => {
    let valA = a.cells[colIndex].innerText.trim();
    let valB = b.cells[colIndex].innerText.trim();

    const numA = parseFloat(valA);
    const numB = parseFloat(valB);
    const isNumeric = !isNaN(numA) && !isNaN(numB);

    if (isNumeric) {
      return isAsc ? numA - numB : numB - numA;
    } else {
      return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
  });

  // Remove old rows and append sorted
  rows.forEach(row => tbody.appendChild(row));

  // Update header sort direction visuals
  Array.from(table.tHead.rows[0].cells).forEach((th, idx) => {
    th.classList.remove('sorted-asc', 'sorted-desc');
    if (idx === colIndex) {
      th.classList.add(isAsc ? 'sorted-asc' : 'sorted-desc');
    }
  });
}

function filterTable() {
  const table = document.getElementById("tester-dashboard");
  const tbody = table.tBodies[0];
  const rows = tbody.rows;

  // Get all filter values
  const filters = [];
  for (let i = 0; i < 13; i++) {
    const filterInput = document.getElementById('filter' + i);
    filters[i] = filterInput ? filterInput.value.toLowerCase() : '';
  }

  // Filter each row
  for (let i = 0; i < rows.length; i++) {
    let showRow = true;
    const row = rows[i];

    // Check each column against its filter
    for (let j = 0; j < 13 && showRow; j++) {
      if (filters[j] && row.cells[j]) {
        const cellText = row.cells[j].innerText.toLowerCase();
        if (cellText.indexOf(filters[j]) === -1) {
          showRow = false;
        }
      }
    }

    // Show/hide row based on filter results
    row.style.display = showRow ? '' : 'none';
  }

  // Update row count display
  updateRowCount();
}

function updateRowCount() {
  const table = document.getElementById("tester-dashboard");
  const tbody = table.tBodies[0];
  const rows = tbody.rows;
  let visibleCount = 0;

  for (let i = 0; i < rows.length; i++) {
    if (rows[i].style.display !== 'none') {
      visibleCount++;
    }
  }

  // Update or create row count display
  let countDisplay = document.getElementById('row-count');
  if (!countDisplay) {
    countDisplay = document.createElement('div');
    countDisplay.id = 'row-count';
    countDisplay.style.cssText = 'text-align: right; padding: 5px; font-weight: bold; color: #666;';
    table.parentNode.insertBefore(countDisplay, table.nextSibling);
  }
  countDisplay.textContent = `Showing ${visibleCount} of ${rows.length} testers`;
}

function clearAllFilters() {
  for (let i = 0; i < 13; i++) {
    const filterInput = document.getElementById('filter' + i);
    if (filterInput) {
      filterInput.value = '';
    }
  }
  filterTable();
}
</script>
"""
        table += script_body
        print(table)
        return table
