"""
Configurable wrapper for flow comparison tools.
Usage:
    python run_flow_compare.py --config config_arr_ccf_cxx.py [compare|generate|validate|all]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

def load_config(config_file):
    """Dynamically load configuration from a Python file."""
    spec = importlib.util.spec_from_file_location("config", config_file)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def apply_config_to_scripts(config):
    """Apply configuration to compare_flows_v3 and symbolize_mtpl modules."""
    import compare_flows_v3 as v3
    import symbolize_mtpl as sm
    
    # Apply to compare_flows_v3
    v3.ROOT = config.ROOT
    v3._MODULE_DIR = config.ROOT / config.MODULE_PATH
    v3._MODULE_NAME = config.MODULE_NAME
    v3._BP_PATH = v3._MODULE_DIR / f"{config.MODULE_NAME}_bp.mtpl"
    v3._ORIG_PATH = v3._MODULE_DIR / f"{config.MODULE_NAME}_orig.mtpl"
    v3._SRC_MTPL = v3._MODULE_DIR / f"{config.MODULE_NAME}.mtpl"
    
    # Ensure orig snapshot with updated paths
    v3.ensure_orig_snapshot()
    
    v3.MTPL_PRIMARY = v3._ORIG_PATH
    v3.MTPL_TEST_SOURCES = [v3.MTPL_PRIMARY]
    v3.OUT_CSV = v3._MODULE_DIR / f"{config.MODULE_NAME}_bp.flows_compare.csv"
    v3.FLOW_DEFS = config.FLOW_DEFS
    v3.FLOWS = list(config.FLOW_DEFS.keys())
    
    # Apply to symbolize_mtpl
    sm.KEEP_FLOW = config.KEEP_FLOW
    sm.REMOVE_FLOWS = config.REMOVE_FLOWS
    sm.ALL_FLOWS = config.ALL_FLOWS
    sm._MODULE_DIR = v3._MODULE_DIR
    sm._MODULE_NAME = config.MODULE_NAME
    sm.OUT_MTPL = v3._MODULE_DIR / f"{config.MODULE_NAME}_bp.mtpl"
    sm.OUT_SYMBOLS = v3._MODULE_DIR / f"{config.MODULE_NAME}_bp.mtpl_symbols.csv"
    sm.OUT_EXPANDED = v3._MODULE_DIR / f"{config.MODULE_NAME}_bp.mtpl_expanded"
    
    # Update v3 reference in symbolize_mtpl
    sm.v3 = v3

def main():
    parser = argparse.ArgumentParser(description="Run flow comparison with configuration")
    parser.add_argument("--config", required=True, help="Path to configuration Python file")
    parser.add_argument("mode", nargs="?", default="all", 
                       choices=["compare", "generate", "validate", "all"],
                       help="Operation mode (default: all)")
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    
    config = load_config(config_path)
    print(f"Loaded configuration from: {config_path}")
    print(f"  ROOT: {config.ROOT}")
    print(f"  MODULE: {config.MODULE_NAME}")
    print(f"  KEEP_FLOW: {config.KEEP_FLOW}")
    print(f"  REMOVE_FLOWS: {', '.join(config.REMOVE_FLOWS)}")
    print()
    
    # Apply configuration to modules
    apply_config_to_scripts(config)
    
    # Import main execution module
    import symbolize_mtpl as sm
    
    # Execute requested mode
    if args.mode == "all":
        print("Running ALL phases: compare -> generate -> validate")
        sm.main_compare()
        sm.main_generate()
        sm.main_validate()
    elif args.mode == "compare":
        print("Running COMPARE phase only")
        sm.main_compare()
    elif args.mode == "generate":
        print("Running GENERATE phase only")
        sm.main_generate()
    elif args.mode == "validate":
        print("Running VALIDATE phase only")
        sm.main_validate()

if __name__ == "__main__":
    main()
