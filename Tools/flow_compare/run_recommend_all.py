"""run_recommend_all.py — batch run recommend_collapse over many modules and
produce a roll-up summary CSV.

Usage:
    python run_recommend_all.py <modules_root> [<glob>]
        e.g. python run_recommend_all.py ..\..\Modules ARR* FUN* SCN*

If no globs are given, runs on every direct sub-sub-directory of modules_root
that contains a `<MODULE>.mtpl` (or `<MODULE>_orig.mtpl`).
"""
from __future__ import annotations
import csv
import sys
import subprocess
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
RECOMMENDER = THIS_DIR / 'recommend_collapse.py'

# Threshold for inclusion in the roll-up summary
THRESH_OK = 0.70
THRESH_SIZE = 2


def discover(modules_root: Path, family_globs: list[str]) -> list[Path]:
    out: list[Path] = []
    if family_globs:
        for g in family_globs:
            for fam in modules_root.glob(g):
                if fam.is_dir():
                    out.extend(d for d in fam.iterdir() if d.is_dir())
    else:
        for fam in modules_root.iterdir():
            if fam.is_dir():
                out.extend(d for d in fam.iterdir() if d.is_dir())
    # Filter to dirs that have a matching mtpl
    keep = []
    for d in sorted(out):
        if (d / f"{d.name}.mtpl").exists() or (d / f"{d.name}_orig.mtpl").exists():
            keep.append(d)
    return keep


def run_recommender(module_dir: Path, py: str) -> Path | None:
    cmd = [py, str(RECOMMENDER), str(module_dir)]
    print(f"[run] {module_dir.name}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERR] returncode={r.returncode}\n  stderr: {r.stderr.strip()[:400]}")
        return None
    csv_path = module_dir / f"{module_dir.name}_collapse_candidates.csv"
    return csv_path if csv_path.exists() else None


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    modules_root = Path(argv[1]).resolve()
    family_globs = argv[2:]
    modules = discover(modules_root, family_globs)
    if not modules:
        print("[ERR] no modules found")
        return 1

    py = sys.executable
    print(f"[info] python={py}")
    print(f"[info] modules: {len(modules)}")

    rollup_rows: list[dict] = []
    for m in modules:
        csv_path = run_recommender(m, py)
        if not csv_path:
            continue
        with csv_path.open('r', newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                ok = float(row['OK_Ratio'])
                sz = int(row['GroupSize'])
                if ok < THRESH_OK or sz < THRESH_SIZE:
                    continue
                rollup_rows.append({
                    'Module': m.name,
                    'EntryPoint': row['EntryPoint'],
                    'MaxDepth': row['MaxDepth'],
                    'GroupSize': sz,
                    'OK_Ratio': ok,
                    'Total_Items': row['Total_Items'],
                    'Template': row['Template'],
                    'TokenValues': row['TokenValues'],
                    'Members': row['Members'],
                    'FirstLines': row['FirstLines'],
                })

    # Rank rollup: EntryPoint desc, MaxDepth desc, GroupSize desc, OK desc
    rollup_rows.sort(key=lambda r: (-int(r['EntryPoint']),
                                    -int(r['MaxDepth']),
                                    -r['GroupSize'],
                                    -r['OK_Ratio'],
                                    -int(r['Total_Items'])))

    out = THIS_DIR / 'collapse_candidates_rollup.csv'
    if rollup_rows:
        with out.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(rollup_rows[0].keys()))
            w.writeheader()
            w.writerows(rollup_rows)
        print(f"[out] {out}  ({len(rollup_rows)} rows)")
    else:
        print("[out] no candidates passed threshold")

    # Console summary: top 5 per module
    by_mod: dict[str, list[dict]] = {}
    for r in rollup_rows:
        by_mod.setdefault(r['Module'], []).append(r)
    print()
    print("=" * 100)
    print(f"Top recommendations per module  (OK>={THRESH_OK}, GroupSize>={THRESH_SIZE})")
    print("=" * 100)
    print(f"{'Module':<26} {'EP':>2} {'D':>2} {'Sz':>3} {'OK%':>4} {'Items':>5}  Template")
    print('-' * 100)
    for mod in sorted(by_mod):
        for r in by_mod[mod][:5]:
            print(f"{mod:<26} {r['EntryPoint']:>2} {r['MaxDepth']:>2} "
                  f"{r['GroupSize']:>3} {int(r['OK_Ratio']*100):>4} "
                  f"{r['Total_Items']:>5}  {r['Template']}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
