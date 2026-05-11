"""
Standalone script to run flow comparison for ARR_CCF_CXX.
This script patches the configuration in compare_flows_v3.py and symbolize_mtpl.py
and then runs the comparison.

Usage:
    python run_ccf_compare.py [compare|generate|validate|all]
    
Default: all (runs all three phases)
"""
import sys
from pathlib import Path
from collections import OrderedDict

# ============================================================================
# CONFIGURATION FOR ARR_CCF_CXX
# ============================================================================

ROOT = Path(r"C:\Users\okayyal\source\repos\nvl_cpu_idgww20")
MODULE_PATH = "Modules/ARR/ARR_CCF_CXX"
MODULE_NAME = "ARR_CCF_CXX"

KEEP_FLOW = "ARR_CCF_CXX_F1XCCF"
REMOVE_FLOWS = [
    "ARR_CCF_CXX_F2XCCF",
    "ARR_CCF_CXX_F3XCCF",
    "ARR_CCF_CXX_F4XCCF",
    "ARR_CCF_CXX_F5XCCF"
]
ALL_FLOWS = [KEEP_FLOW, *REMOVE_FLOWS]

FLOW_DEFS = OrderedDict([
    ("ARR_CCF_CXX_F1XCCF", "F1XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F2XCCF", "F2XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F3XCCF", "F3XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F4XCCF", "F4XCCF_SubFlow::"),
    ("ARR_CCF_CXX_F5XCCF", "F5XCCF_SubFlow::"),
])

# ============================================================================
# APPLY CONFIGURATION
# ============================================================================

def apply_configuration():
    """Patch compare_flows_v3 and symbolize_mtpl with ARR_CCF_CXX configuration."""
    import compare_flows_v3 as v3
    import symbolize_mtpl as sm
    
    # Patch compare_flows_v3
    v3.ROOT = ROOT
    v3.SKILL_CSV = ROOT / "Tools" / "flow_compare" / "ARR_CCF_CXX_skill.csv"
    v3._MODULE_DIR = ROOT / MODULE_PATH
    v3._MODULE_NAME = MODULE_NAME
    v3._BP_PATH = v3._MODULE_DIR / f"{MODULE_NAME}_bp.mtpl"
    v3._ORIG_PATH = v3._MODULE_DIR / f"{MODULE_NAME}_orig.mtpl"
    v3._SRC_MTPL = v3._MODULE_DIR / f"{MODULE_NAME}.mtpl"
    
    # Recreate ensure_orig_snapshot with updated paths
    def ensure_orig_snapshot():
        if v3._ORIG_PATH.exists():
            return
        legacy = v3._MODULE_DIR / f"{MODULE_NAME}.mtpl_orig"
        if legacy.exists():
            legacy.rename(v3._ORIG_PATH)
            print(f"[orig] migrated legacy snapshot -> {v3._ORIG_PATH.name}")
            return
        if not v3._SRC_MTPL.exists():
            raise FileNotFoundError(
                f"Cannot create orig snapshot: source mtpl missing: {v3._SRC_MTPL}")
        import shutil
        shutil.copy2(v3._SRC_MTPL, v3._ORIG_PATH)
        print(f"[orig] created snapshot {v3._ORIG_PATH.name} from {v3._SRC_MTPL.name}")
    
    ensure_orig_snapshot()
    
    v3.MTPL_PRIMARY = v3._ORIG_PATH
    v3.MTPL_TEST_SOURCES = [v3.MTPL_PRIMARY]
    v3.OUT_CSV = v3._MODULE_DIR / f"{MODULE_NAME}_bp.flows_compare.csv"
    v3.FLOW_DEFS = FLOW_DEFS
    v3.FLOWS = list(FLOW_DEFS.keys())
    
    # Patch symbolize_mtpl
    sm.KEEP_FLOW = KEEP_FLOW
    sm.REMOVE_FLOWS = REMOVE_FLOWS
    sm.ALL_FLOWS = ALL_FLOWS
    sm._MODULE_DIR = v3._MODULE_DIR
    sm._MODULE_NAME = MODULE_NAME
    sm.OUT_MTPL = v3._MODULE_DIR / f"{MODULE_NAME}_bp.mtpl"
    sm.OUT_SYMBOLS = v3._MODULE_DIR / f"{MODULE_NAME}_bp.mtpl_symbols.csv"
    sm.OUT_EXPANDED = v3._MODULE_DIR / f"{MODULE_NAME}_bp.mtpl_expanded"
    
    # Update v3 reference
    sm.v3.ROOT = v3.ROOT
    sm.v3._MODULE_DIR = v3._MODULE_DIR
    sm.v3._MODULE_NAME = v3._MODULE_NAME
    sm.v3.MTPL_PRIMARY = v3.MTPL_PRIMARY
    sm.v3.MTPL_TEST_SOURCES = v3.MTPL_TEST_SOURCES
    sm.v3.OUT_CSV = v3.OUT_CSV
    sm.v3.FLOW_DEFS = v3.FLOW_DEFS
    sm.v3.FLOWS = v3.FLOWS

    print(f"[OK] Configuration applied:")
    print(f"  Module: {MODULE_NAME}")
    print(f"  Root: {ROOT}")
    print(f"  Keep flow: {KEEP_FLOW}")
    print(f"  Remove flows: {', '.join(REMOVE_FLOWS)}")
    print()

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if mode not in ["compare", "generate", "validate", "all"]:
        print(f"ERROR: Invalid mode '{mode}'")
        print("Usage: python run_ccf_compare.py [compare|generate|validate|all]")
        sys.exit(1)
    
    apply_configuration()
    
    import symbolize_mtpl as sm

    if mode == "all":
        print("=" * 70)
        print("RUNNING ALL PHASES")
        print("=" * 70)
        # The main() function handles all phases based on command-line args
        # We need to set sys.argv for it
        sys.argv = ["symbolize_mtpl.py", "all"]
        sm.main()
    elif mode == "compare":
        sys.argv = ["symbolize_mtpl.py", "compare"]
        sm.main()
    elif mode == "generate":
        sys.argv = ["symbolize_mtpl.py", "generate"]
        sm.main()
    elif mode == "validate":
        sys.argv = ["symbolize_mtpl.py", "validate"]
        sm.main()

if __name__ == "__main__":
    main()
