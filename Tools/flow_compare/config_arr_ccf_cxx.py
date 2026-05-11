"""
Configuration file for ARR_CCF_CXX flow comparison.
Import this before running compare_flows_v3.py or symbolize_mtpl.py
"""
from pathlib import Path
from collections import OrderedDict

# Repository root
ROOT = Path(r"C:\Users\okayyal\source\repos\nvl_cpu_idgww20")

# Module configuration
MODULE_PATH = "Modules/ARR/ARR_CCF_CXX"
MODULE_NAME = "ARR_CCF_CXX"

# Flow configuration
KEEP_FLOW = "ARR_CCF_CXX_F1XCCF"
REMOVE_FLOWS = [
    "ARR_CCF_CXX_F2XCCF",
    "ARR_CCF_CXX_F3XCCF",
    "ARR_CCF_CXX_F4XCCF",
    "ARR_CCF_CXX_F5XCCF"
]
ALL_FLOWS = [KEEP_FLOW, *REMOVE_FLOWS]

# Flow definitions (flow_name -> prefix/identifier)
# These are used for normalization - adjust as needed
FLOW_DEFS = OrderedDict([
    ("ARR_CCF_CXX_F1XCCF", "F1XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F2XCCF", "F2XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F3XCCF", "F3XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F4XCCF", "F4XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F5XCCF", "F5XCCF_SubFlow::"),
])
