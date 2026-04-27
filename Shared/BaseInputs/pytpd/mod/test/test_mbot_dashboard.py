#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston

import sys
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE  # must be first import for unittests
from mod.mbot_dashboard import MBotDB, TesterStatusDB
from main.manager_botos import Remote
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import shutil
import os
import time


class MbotDB(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mbot_db(self):
        obj = MBotDB()
        botos_folder = f'{UT_DIR}/mbot_dashboard'
        today_time = '2025-02-03 11:32:05.929017'
        gold_result = """
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
<table id='mbot-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>
<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><th colspan='13' style ='font-size:15px;'>MBOT DASHBOARD 2025-02-03 11:32:05.929017 <a href='https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?tester=True'>(Goto Tester Dashboard)</a></th></tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #E6F3FF; color: #000000;'>
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
        </tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>
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
        </tr></thead>
<tbody>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FFFF99; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1738357931825_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Running</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT61919A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_13:12:11</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'><a href="https://github.com/intel-restricted/nvl.hub/pull/908" target="_blank">nvl.hub-908</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FFFF99; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1738347801867_D</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Running</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.abfg@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT64287A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_10:23:21</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>8000_1738347801824_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Queued</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_10:23:21</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?move_to_top=8000_1738347801824_B&product=arls68">MoveToTop</a></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?cancel_job=8000_1738347801824_B&product=arls68">CancelJob</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'><a href="https://github.com/intel-restricted/nvl.hub/pull/907" target="_blank">nvl.hub-907</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>8000_1738347801823_E</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Queued</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_10:23:21</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?move_to_top=8000_1738347801823_E&product=arls68">MoveToTop</a></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?cancel_job=8000_1738347801823_E&product=arls68">CancelJob</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #90EE90; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1731905940140_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68poc</td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./2024-11-17/ituff_CLASSHOT_TestUnitLog_2024-11-17-21-00-44.txt">PASSED</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT61919A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2024-11-17_20:59:00</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-02-03 10:17:20</td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'>100</td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px;'>I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/1731905940140_B</td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FF6B6B; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1733218861920_E</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'><a href="https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./2024-12-03/loadLog_2024-12-03-17-50-36.txt">FAILED_LOAD</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>PG</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT64287A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2024-12-03_01:41:01</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-02-03 10:16:57</td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px;'>I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/1733218861920_E</td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #90EE90; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1732299273894_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./2024-11-22/ituff_CLASSHOT_TestUnitLog_2024-11-22-10-18-54.txt">PASSED</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT64287A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2024-11-22_10:14:33</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-02-03 10:16:39</td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'>100</td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px;'>I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/1732299273894_B</td>
        </tr>
</tbody>
</table>
<button onclick="clearAllMbotFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>
<br>BotOS Wiki <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage</a>
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
        with MockVar(MBotDB, 'botos_folder_input', Mock(return_value=botos_folder)), \
                MockVar(MBotDB, 'return_today_time', Mock(return_value=today_time)), \
                MockVar(MBotDB, 'extend', True), \
                MockVar(Remote, 'read_completed', Mock(return_value={})):
            result = obj.main()
        self.assertTextEqual(result, gold_result)

    def test_mbot_db_no_extend(self):
        obj = MBotDB()
        botos_folder = f'{UT_DIR}/mbot_dashboard'
        today_time = '2025-02-03 11:32:05.929017'
        gold_result = """
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
<table id='mbot-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>
<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><th colspan='13' style ='font-size:15px;'>MBOT DASHBOARD 2025-02-03 11:32:05.929017 <a href='https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?tester=True'>(Goto Tester Dashboard)</a></th></tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #E6F3FF; color: #000000;'>
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
        </tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>
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
        </tr></thead>
<tbody>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FFFF99; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1738357931825_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Running</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT61919A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_13:12:11</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'><a href="https://github.com/intel-restricted/nvl.hub/pull/908" target="_blank">nvl.hub-908</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FFFF99; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1738347801867_D</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Running</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.abfg@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT64287A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_10:23:21</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>8000_1738347801824_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Queued</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_10:23:21</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?move_to_top=8000_1738347801824_B&product=arls68">MoveToTop</a></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?cancel_job=8000_1738347801824_B&product=arls68">CancelJob</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'><a href="https://github.com/intel-restricted/nvl.hub/pull/907" target="_blank">nvl.hub-907</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>8000_1738347801823_E</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'>Queued</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-01-31_10:23:21</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?move_to_top=8000_1738347801823_E&product=arls68">MoveToTop</a></td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?cancel_job=8000_1738347801823_E&product=arls68">CancelJob</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #90EE90; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1731905940140_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68poc</td>
        <td style='padding-right: 5px;'><a href="https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./2024-11-17/ituff_CLASSHOT_TestUnitLog_2024-11-17-21-00-44.txt">PASSED</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT61919A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2024-11-17_20:59:00</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-02-03 10:17:20</td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'>100</td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px;'>I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/1731905940140_B</td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FF6B6B; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1733218861920_E</td>
        <td style='padding-right: 5px; white-space: nowrap;'>arls68</td>
        <td style='padding-right: 5px;'><a href="https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./2024-12-03/loadLog_2024-12-03-17-50-36.txt">FAILED_LOAD</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'>tai.pham1234@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>PG</td>
        <td style='padding-right: 5px; white-space: nowrap;'>JF04TXBT64287A</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2024-12-03_01:41:01</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-02-03 10:16:57</td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px;'></td>
        <td style='padding-right: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px;'>I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/1733218861920_E</td>
        </tr>
</tbody>
</table>
<button onclick="clearAllMbotFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>
<br>BotOS Wiki <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage</a>
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
        with MockVar(MBotDB, 'botos_folder_input', Mock(return_value=botos_folder)), \
                MockVar(MBotDB, 'return_today_time', Mock(return_value=today_time)), \
                MockVar(MBotDB, 'extend', False), \
                MockVar(time, 'time', Mock(return_value=1739211405)), \
                MockVar(Remote, 'read_completed', Mock(return_value={})):
            result = obj.main()
        self.assertTextEqual(result, gold_result)

    def test_write_table(self):
        obj = MBotDB()
        gold_result = """<tr style='padding-right-left: 5px; text-align: left; background-color: #90EE90; color: #000000;'>
        <td style='padding-right: 5px; white-space: nowrap;'>1731905940140_B</td>
        <td style='padding-right: 5px; white-space: nowrap;'>nvls</td>
        <td style='padding-right: 5px;'><a href="https://tvpv.png.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=.//ituff_path">PASSED</a></td>
        <td style='padding-right: 5px; white-space: nowrap;'>gustavo.a.zumbado@intel.com</td>
        <td style='padding-right: 5px; white-space: nowrap;'>PG</td>
        <td style='padding-right: 5px; white-space: nowrap;'>tester1</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2024-11-17_20:59:00</td>
        <td style='padding-right: 5px; white-space: nowrap;'>2025-02-25 12:58:22</td>
        <td style='padding-left: 5px; white-space: nowrap; text-align: right;'></td>
        <td style='padding-right: 5px;'>MoveToTop</td>
        <td style='padding-right: 5px;'>CancelJob</td>
        <td style='padding-right: 5px; white-space: nowrap;'><a href="https://github.com/intel-restricted/nvl.gcd/pull/787" target="_blank">nvl.gcd-787</a></td>
        <td style='padding-right: 5px;'>I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/1731905940140_B</td>
        </tr>
"""
        botos_folder = f'{UT_DIR}/mbot_dashboard'
        today_time = '2025-02-03 11:32:05.929017'
        jobId = '1731905940140_B'
        value = ['nvls', 'PASSED', 'gustavo.a.zumbado@intel.com', 'PG', 'tester1', '2025-02-25 12:58:22', 'MoveToTop', 'CancelJob',
                 'https://github.com/intel-restricted/nvl.gcd/pull/787', 'ituff_path', 'init_path', 'log_path', 'comment']
        with TempDir() as tdir:
            with MockVar(MBotDB, 'botos_folder_input', Mock(return_value=botos_folder)), \
                    MockVar(MBotDB, 'curtime', Mock(return_value=today_time)), \
                    MockVar(Remote, 'read_completed', Mock(return_value={})):
                result = obj.write_table(jobId, value, "")
        self.assertTextEqual(result, gold_result)

    def test_get_json_data(self):
        obj = MBotDB()
        botos_folder = f'{UT_DIR}/mbot_dashboard'
        today_time = '2025-02-03 11:32:05.929017'
        timestamp = 1738409525.929017
        data = {"INIT log": "I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/6248_CLASSHOT_AF_initLog_2026-03-19-11-05-39.txt",
                "Ituff file": "I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/ituff_CLASSHOT_1_TestUnitLog_2026-03-19-11-05-39.txt",
                "Load log": "I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/loadLog_2026-03-19-11-05-39.txt",
                "Test Unit log": "I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/CLASSHOT_1_TestUnitLog_2026-03-19-11-05-39.txt",
                "code": 1,
                "tprolling": "I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos/tp_rolling_botos/1773939350804_B",
                "logfile": "I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/7000_1773939350804_B_JF04TXBT64169A.txt",
                "site": "JF",
                "command": "done",
                "comment": "[2026-03-19T12:07:58.014533-07:00][A][TAL][DUT: 11] DUT 11: DataBin = 60282001, SoftBin = 6028, HardBin = 60, PassFailBin = 1, ExitPort = 1",
                "tracelot": "",
                "pkg": "nvls52c",
                "email": "",
                "tester": "JF: JF04TXBT64169A",
                "url": "https://github.com/intel-restricted/nvl.common/pull/2396"}
        gold_result = ['nvls52c', 'FAILED', '', 'JF', 'JF: JF04TXBT64169A', '2025-02-01 03:32:05', '', '', 'https://github.com/intel-restricted/nvl.common/pull/2396',
                       'I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/ituff_CLASSHOT_1_TestUnitLog_2026-03-19-11-05-39.txt',
                       'I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/6248_CLASSHOT_AF_initLog_2026-03-19-11-05-39.txt',
                       'I:/tpvalidation/engtools/tptools/mtl/infra/torch/testerload/2026-03-19/loadLog_2026-03-19-11-05-39.txt',
                       '[2026-03-19T12:07:58.014533-07:00][A][TAL][DUT: 11] DUT 11: DataBin = 60282001, SoftBin = 6028, HardBin = 60, PassFailBin = 1, ExitPort = 1']
        with MockVar(time, 'time', Mock(return_value=1738400000.929017)):
            result = obj.get_json_data(data, timestamp)
        self.assertEqual(result, gold_result)


class TesterDB(TestCase):

    def test_mbot_db(self):
        obj = TesterStatusDB()
        tester_folder = f'{UT_DIR_REPO}/tester_status'
        today_time = '2025-02-25 12:58:22.612101'
        time_since_updated = "1"
        job_submitter = 'gustavo.a.zumbado@intel.com'
        OPT = {'site': 'JF'}
        obj.OPT = OPT
        obj.site = 'JF'
        gold_result = """
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
<table id='tester-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>
<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><th colspan='13' style ='font-size:15px;'><pre>TESTERS STATUS DASHBOARD 2025-02-25 12:58:22.612101</pre></th></tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #E6F3FF; color: #000000;'>
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
        </tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>
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
        </tr></thead>
<tbody>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FFB347; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>arls68jf</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF04TXBT61919A</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>reserved</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>2025-08-19_17:16:13</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPI</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TEAMBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>X6-06-1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>sourcelot: NS28A0GL11, tray#: 3</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>test special notes</td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #90EE90; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>arls68jf</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF04TXBT64278A</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>running</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>1757614297066_D</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPBOT/MBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>X6-06-2</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>sim</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>jf4github01</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>OFFLINE BOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>sim</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>jf4github04</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>OFFLINE BOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
</tbody>
</table>
<button onclick="clearAllFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>
<br>
<br> Goto <a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi">MBOT Dashboard</a></br>
<br> Goto <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">BotOS Wiki</a></br>
<br> Notes: A Teambot session is 6 hours long. Each time you renew is 2 hours long. Please pay attention to the time limit.</br>
<br> *(team-name) means this tester will be allocated to the mentioned team. Ex: (Analog) means this tester will be allocated to Analog team.</br>
<br> *This (team-name) is updated based on the current allocation and will be changed if the current tester allocation changes.</br>
<script>
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
        with MockVar(TesterStatusDB, 'tester_folder_input', Mock(return_value=tester_folder)), \
                MockVar(TesterStatusDB, 'return_today_time', Mock(return_value=today_time)), \
                MockVar(TesterStatusDB, 'sixshot', Mock(return_value="")), \
                MockVar(TesterStatusDB, 'get_job_submitter', Mock(return_value=job_submitter)), \
                MockVar(TesterStatusDB, 'get_time_since_updated', Mock(return_value=time_since_updated)):
            result = obj.main()
        self.assertTextEqual(result, gold_result)

    def test_tester_info_compare(self):
        obj = TesterStatusDB()
        golden_result = """Tester info has changed between current and previous versions
Tester location changed: JF04TXBT64278A: X6-06-2 to No-assigned-Location
"""
        with CaptureStdoutLog() as p:
            obj.tester_info_compare({'JF04TXBT61919A': 'X6-06-1', 'JF04TXBT64278A': ''}, {'JF04TXBT61919A': 'X6-06-1', 'JF04TXBT64278A': 'X6-06-2'})
        self.assertTextEqual(p.getvalue(), golden_result)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mbot_db_FM_empty(self):
        obj = TesterStatusDB()
        tester_folder = f'{UT_DIR}/tester_status'
        today_time = '2025-02-25 12:58:22.612101'
        time_since_updated = "1"
        OPT = {'site': 'FM'}
        obj.OPT = OPT
        obj.site = 'FM'
        gold_result = """
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
<table id='tester-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>
<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><th colspan='13' style ='font-size:15px;'><pre>TESTERS STATUS DASHBOARD 2025-02-25 12:58:22.612101</pre></th></tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #E6F3FF; color: #000000;'>
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
        </tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>
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
        </tr></thead>
<tbody>
<tr><td colspan='6' style='text-align: center;'>No tester data available for this site.</td></tr></tbody>
</table>
<button onclick="clearAllFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>
<br>
<br> Goto <a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi">MBOT Dashboard</a></br>
<br> Goto <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">BotOS Wiki</a></br>
<br> Notes: A Teambot session is 6 hours long. Each time you renew is 2 hours long. Please pay attention to the time limit.</br>
<br> *(team-name) means this tester will be allocated to the mentioned team. Ex: (Analog) means this tester will be allocated to Analog team.</br>
<br> *This (team-name) is updated based on the current allocation and will be changed if the current tester allocation changes.</br>
<script>
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
        with MockVar(TesterStatusDB, 'tester_folder_input', Mock(return_value=tester_folder)), \
                MockVar(TesterStatusDB, 'return_today_time', Mock(return_value=today_time)), \
                MockVar(TesterStatusDB, 'sixshot', Mock(return_value="")), \
                MockVar(TesterStatusDB, 'get_time_since_updated', Mock(return_value=time_since_updated)), \
                MockVar(Remote, 'get_tester_files', Mock(return_value={})):
            result = obj.main()
        self.assertTextEqual(result, gold_result)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mbot_db_FM(self):
        obj = TesterStatusDB()
        tester_folder = f'{UT_DIR}/tester_status'
        today_time = '2025-02-25 12:58:22.612101'
        time_since_updated = "1"
        job_submitter = 'abcde@intel.com'
        OPT = {'site': 'FM'}
        obj.OPT = OPT
        obj.site = 'FM'

        # Mock tester data for FM site: {(site, tester): {fname: age}}
        tester_data = {
            ('FM', 'FM04TXBT12345A'): {
                'I:/FM04TXBT12345A/nvls28c.package.info': 0.5,
                'I:/FM04TXBT12345A/GLXXGOLD34_4.gold': 0.5,
                'I:/FM04TXBT12345A/8000_1757634432654_D.tar.gz': 0.5,
                'I:/FM04TXBT12345A/idle.status': 0.3,
                'I:/FM04TXBT12345A/type1.info': 0.1,
                'I:/FM04TXBT12345A/reserved for testing.notes': 0.1
            },
            ('FM', 'FM04TXBT67890B'): {
                'I:/FM04TXBT67890B/arls68fm.package.info': 0.7,
                'I:/FM04TXBT67890B/running.status': 0.2,
                'I:/FM04TXBT12345A/8000_1757634432654_B.tar.gz': 0.5,
                'I:/FM04TXBT67890B/teambotonly.info': 0.1
            },
            ('FM', 'fm4sim01'): {
                'I:/fm4sim01/sim.package.info': 1.2,
                'I:/fm4sim01/idle.status': 0.4
            },
            # This should be filtered out since it's not FM site
            ('PG', 'PG04TXBT11111C'): {
                'I:/PG04TXBT11111C/arls68pg.package.info': 0.6,
                'I:/PG04TXBT11111C/status': 0.3
            }
        }

        gold_result = """
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
<table id='tester-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>
<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><th colspan='13' style ='font-size:15px;'><pre>TESTERS STATUS DASHBOARD 2025-02-25 12:58:22.612101</pre></th></tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #E6F3FF; color: #000000;'>
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
        </tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>
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
        </tr></thead>
<tbody>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>nvls28c</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM04TXBT12345A</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>abcde</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>1757634432654_D</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPBOT/MBOT/TEAMBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>sourcelot: GLXXGOLD34, tray#: 4</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>reserved for testing</td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #90EE90; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>arls68fm</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM04TXBT67890B</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>running</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>abcde</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>1757634432654_B</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPBOT/MBOT/TEAMBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>sim</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>fm4sim01</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>abcde</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>OFFLINE BOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
</tbody>
</table>
<button onclick="clearAllFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>
<br>
<br> Goto <a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi">MBOT Dashboard</a></br>
<br> Goto <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">BotOS Wiki</a></br>
<br> Notes: A Teambot session is 6 hours long. Each time you renew is 2 hours long. Please pay attention to the time limit.</br>
<br> *(team-name) means this tester will be allocated to the mentioned team. Ex: (Analog) means this tester will be allocated to Analog team.</br>
<br> *This (team-name) is updated based on the current allocation and will be changed if the current tester allocation changes.</br>
<script>
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
        with MockVar(TesterStatusDB, 'tester_folder_input', Mock(return_value=tester_folder)), \
                MockVar(TesterStatusDB, 'return_today_time', Mock(return_value=today_time)), \
                MockVar(TesterStatusDB, 'sixshot', Mock(return_value="")), \
                MockVar(TesterStatusDB, 'get_time_since_updated', Mock(return_value=time_since_updated)), \
                MockVar(TesterStatusDB, 'get_job_submitter', Mock(return_value=job_submitter)), \
                MockVar(Remote, 'get_tester_files', Mock(return_value=tester_data)):
            result = obj.main()
        self.assertTextEqual(result, gold_result)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tester_db_all_sites(self):
        obj = TesterStatusDB()
        tester_folder = f'{UT_DIR}/tester_status'
        today_time = '2025-02-25 12:58:22.612101'
        time_since_updated = "1"
        job_submitter = 'gustavo.a.zumbado@intel.com'
        # Mock tester data for FM site: {(site, tester): {fname: age}}
        tester_data = {
            ('FM', 'FM04TXBT12345A'): {
                'I:/FM04TXBT12345A/nvls28c.package.info': 0.5,
                'I:/FM04TXBT12345A/GLXXGOLD34_4.gold': 0.5,
                'I:/FM04TXBT12345A/8000_1757634432654_D.tar.gz': 0.5,
                'I:/FM04TXBT12345A/idle.status': 0.3,
                'I:/FM04TXBT12345A/type1.info': 0.1,
                'I:/FM04TXBT12345A/reserved for testing.notes': 0.1
            },
            ('FM', 'FM04TXBT67890B'): {
                'I:/FM04TXBT67890B/arls68fm.package.info': 0.7,
                'I:/FM04TXBT67890B/down.status': 0.2,
                'I:/FM04TXBT12345A/8000_1757634432654_B.tar.gz': 0.5,
                'I:/FM04TXBT67890B/teambotonly.info': 0.1
            },
            ('FM', 'fm4sim01'): {
                'I:/fm4sim01/sim.package.info': 1.2,
                'I:/fm4sim01/idle.status': 0.4
            },
            # This should be filtered out since it's not FM site
            ('PG', 'PG04TXBT11111C'): {
                'I:/PG04TXBT11111C/arls68pg.package.info': 0.6,
                'I:/PG04TXBT11111C/status': 0.3
            }
        }
        gold_result = """
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
<table id='tester-dashboard' border='1' cellspacing='0' style='font-family: Calibri;'>
<thead><tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><th colspan='13' style ='font-size:15px;'><pre>TESTERS STATUS DASHBOARD 2025-02-25 12:58:22.612101</pre></th></tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #E6F3FF; color: #000000;'>
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
        </tr><tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>
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
        </tr></thead>
<tbody>
<tr style='padding-right-left: 5px; text-align: left; background-color: #FFB347; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>arls68jf</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF04TXBT61919A</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>reserved</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>2025-08-19_17:16:13</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPI</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TEAMBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>X6-06-1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>sourcelot: NS28A0GL11, tray#: 3</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>test special notes</td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #90EE90; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>arls68jf</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF04TXBT64278A</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>running</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>1757614297066_D</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPBOT/MBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>X6-06-2</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>sim</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>jf4github01</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>OFFLINE BOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>sim</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>JF</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>jf4github04</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>OFFLINE BOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>nvls28c</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM04TXBT12345A</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>1757634432654_D</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPBOT/MBOT/TEAMBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>sourcelot: GLXXGOLD34, tray#: 4</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>reserved for testing</td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #808080; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>arls68fm</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM04TXBT67890B</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>down</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>1757634432654_B</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPBOT/MBOT/TEAMBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>sim</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>FM</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>fm4sim01</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>idle</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>OFFLINE BOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
<tr style='padding-right-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000; white-space: nowrap;'>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>arls68pg</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>PG</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>PG04TXBT11111C</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>unknown</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'>1</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>gustavo.a.zumbado</td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; white-space: nowrap;'>TPBOT/MBOT/TEAMBOT</td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        <td style='padding-right: 5px; padding-left: 5px; text-align: right; white-space: nowrap;'></td>
        </tr>
</tbody>
</table>
<button onclick="clearAllFilters()" style="margin: 10px 0; padding: 8px 16px; font-size: 14px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear All Filters</button><br>
<br>
<br> Goto <a href="https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi">MBOT Dashboard</a></br>
<br> Goto <a href="https://wiki.ith.intel.com/display/ITSpdxtp/TPBot%2C+MBot+and+TeamBot+usage">BotOS Wiki</a></br>
<br> Notes: A Teambot session is 6 hours long. Each time you renew is 2 hours long. Please pay attention to the time limit.</br>
<br> *(team-name) means this tester will be allocated to the mentioned team. Ex: (Analog) means this tester will be allocated to Analog team.</br>
<br> *This (team-name) is updated based on the current allocation and will be changed if the current tester allocation changes.</br>
<script>
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
        with MockVar(TesterStatusDB, 'tester_folder_input', Mock(return_value=tester_folder)), \
                MockVar(TesterStatusDB, 'return_today_time', Mock(return_value=today_time)), \
                MockVar(TesterStatusDB, 'sixshot', Mock(return_value="")), \
                MockVar(TesterStatusDB, 'get_time_since_updated', Mock(return_value=time_since_updated)), \
                MockVar(TesterStatusDB, 'get_job_submitter', Mock(return_value=job_submitter)), \
                MockVar(Remote, 'get_tester_files', Mock(return_value=tester_data)):
            result = obj.main()
        self.assertTextEqual(result, gold_result)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
