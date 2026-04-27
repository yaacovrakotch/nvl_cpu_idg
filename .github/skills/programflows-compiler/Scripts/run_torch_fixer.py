"""
run_torch_fixer.py — Torch fix-tp wrapper for NVL test program BOMs.

Runs the Torch fixer for a given BOM and automatically discards all
side-effect file changes introduced by the fixer (e.g. .env, .plist,
.slimplist). Only files that were already dirty before the fixer ran are
preserved. NOTE: .stpl files are intentionally kept — they are NOT discarded.

Usage:
    python run_torch_fixer.py <BOM>

Example:
    python run_torch_fixer.py Class_NVL_S28C

Must be run from the repo root (next to the .sln file).
"""

import glob
import os
import subprocess
import sys


def get_dirty_files():
    """Return the set of files with unstaged modifications (git diff --name-only)."""
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True, text=True, check=True,
    )
    return {f for f in result.stdout.splitlines() if f}


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_torch_fixer.py <BOM>")
        print("Example: python run_torch_fixer.py Class_NVL_S28C")
        sys.exit(1)

    bom = sys.argv[1]

    # --- Validate environment ---
    torch_root = os.environ.get("TorchAPIExecPath", "")
    if not torch_root:
        print("ERROR: TorchAPIExecPath environment variable is not set.")
        sys.exit(1)

    torch_exe = os.path.join(torch_root, "Torch.exe")
    if not os.path.isfile(torch_exe):
        print(f"ERROR: Torch.exe not found at: {torch_exe}")
        sys.exit(1)

    # --- Auto-discover .sln file ---
    sln_files = glob.glob("*.sln")
    if not sln_files:
        print("ERROR: No .sln file found. Run this script from the repo root.")
        sys.exit(1)
    sln_file = sln_files[0]

    # --- Build tpproj path ---
    tpproj = f"POR_TP/{bom}/{bom}.tpproj"
    if not os.path.isfile(tpproj):
        print(f"ERROR: .tpproj not found: {tpproj}")
        print("  Check that the BOM name is correct and POR_TP/<BOM>/ exists.")
        sys.exit(1)

    print(f"BOM      : {bom}")
    print(f"Solution : {sln_file}")
    print(f"Project  : {tpproj}")
    print()

    # --- Snapshot user's pre-existing dirty files ---
    pre_fixer_dirty = get_dirty_files()
    if pre_fixer_dirty:
        print(f"Pre-fixer dirty files ({len(pre_fixer_dirty)}):")
        for f in sorted(pre_fixer_dirty):
            print(f"  {f}")
        print()

    # --- Run Torch fixer ---
    cmd = [torch_exe, "fix-tp", "--sln-config", bom, "-s", sln_file, "-p", tpproj]
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    result = subprocess.run(cmd)
    print("-" * 60)

    if result.returncode != 0:
        print(f"ERROR: Torch fixer exited with code {result.returncode}.")
        sys.exit(result.returncode)

    # --- Detect and discard fixer side effects ---
    # .stpl files are intentionally excluded — they must be kept.
    post_fixer_dirty = get_dirty_files()
    side_effects = {
        f for f in (post_fixer_dirty - pre_fixer_dirty)
        if not f.endswith(".stpl")
    }
    kept_stpl = {
        f for f in (post_fixer_dirty - pre_fixer_dirty)
        if f.endswith(".stpl")
    }

    if side_effects:
        print(f"\nDiscarding {len(side_effects)} fixer side-effect file(s):")
        for f in sorted(side_effects):
            print(f"  - {f}")
            subprocess.run(["git", "checkout", "--", f], check=True)
        print()

    if kept_stpl:
        print(f"Keeping {len(kept_stpl)} .stpl file(s) (not discarded):")
        for f in sorted(kept_stpl):
            print(f"  ~ {f}")
        print()
    else:
        print("\nNo fixer side effects to discard.")

    # --- Summary ---
    remaining_dirty = get_dirty_files()
    print("Torch fixer done.")
    if remaining_dirty:
        print(f"Files still modified ({len(remaining_dirty)}) — your intended changes:")
        for f in sorted(remaining_dirty):
            print(f"  {f}")
    else:
        print("Working tree is clean.")


if __name__ == "__main__":
    main()
