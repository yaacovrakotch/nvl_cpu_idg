"""Run auto_run_groups.py on every module under ARR/FUN/SCN/FUS and
aggregate group-level pass/fail. Writes a CSV summary to:
  Tools/flow_compare/auto_run_sweep.csv

Usage:
    python run_auto_sweep.py [phase]

phase default = 'generate' (fast). Use 'all' to include torch build.
"""
from __future__ import annotations
import csv
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Users\yrakotch\source\repos\nvl_cpu_idg")
TOOLS = ROOT / "Tools" / "flow_compare"
DRIVER = TOOLS / "auto_run_groups.py"
PYTHON = ROOT / "Modules" / ".venv" / "Scripts" / "python.exe"
OUT_CSV = TOOLS / "auto_run_sweep.csv"


def main(phase: str = "generate") -> int:
    modules: list[Path] = []
    for sub in ("ARR", "FUN", "SCN", "FUS"):
        sub_dir = ROOT / "Modules" / sub
        if not sub_dir.exists():
            continue
        for d in sorted(sub_dir.iterdir()):
            if d.is_dir() and (d / f"{d.name}_collapse_candidates.csv").exists():
                modules.append(d)

    print(f"Found {len(modules)} module(s) with collapse_candidates.csv")
    print(f"Phase: {phase}")
    print()

    rows: list[dict] = []
    t0_total = time.time()
    for i, md in enumerate(modules, 1):
        t0 = time.time()
        print(f"[{i}/{len(modules)}] {md.name} ... ", end="", flush=True)
        try:
            proc = subprocess.run(
                [str(PYTHON), str(DRIVER), str(md), phase],
                capture_output=True, text=True, timeout=1800,
            )
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT")
            rows.append({"Module": md.name, "Groups": "?", "OK": "?",
                         "Failed": "?", "Status": "TIMEOUT",
                         "Time_s": int(time.time() - t0)})
            continue
        # Parse summary from stdout: "SUMMARY: N/M group(s) OK"
        ok = failed = total = -1
        for line in proc.stdout.splitlines():
            if "SUMMARY:" in line and "group(s) OK" in line:
                # e.g. "[MODULE] SUMMARY: 3/3 group(s) OK"
                try:
                    frag = line.split("SUMMARY:")[1].strip()
                    nums = frag.split("group(s)")[0].strip()
                    ok_s, total_s = nums.split("/")
                    ok = int(ok_s); total = int(total_s); failed = total - ok
                except Exception:
                    pass
                break
        status = "OK" if (ok >= 0 and ok == total and total > 0) else \
                 "NONE" if (total == 0 and proc.returncode == 0) else \
                 "PARTIAL" if (ok > 0) else \
                 "FAIL" if (ok == 0 and total > 0) else \
                 "NONE" if (ok == -1 and proc.returncode == 0) else \
                 f"NORC={proc.returncode}"
        rows.append({"Module": md.name, "Groups": total, "OK": ok,
                     "Failed": failed, "Status": status,
                     "Time_s": int(time.time() - t0)})
        print(f"{status:8} {ok}/{total} groups ({int(time.time()-t0)}s)")
        # save log on failure for diagnostics
        if status not in ("OK",):
            (TOOLS / f"_sweep_{md.name}.log").write_text(
                proc.stdout + "\n--- STDERR ---\n" + proc.stderr,
                encoding="utf-8")

    print()
    print(f"Total elapsed: {int(time.time() - t0_total)}s")
    print(f"Writing summary to {OUT_CSV}")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Module", "Groups", "OK", "Failed",
                                          "Status", "Time_s"])
        w.writeheader()
        w.writerows(rows)

    # Print aggregate
    n_ok = sum(1 for r in rows if r["Status"] == "OK")
    n_none = sum(1 for r in rows if r["Status"] == "NONE")
    n_partial = sum(1 for r in rows if r["Status"] == "PARTIAL")
    n_fail = sum(1 for r in rows if r["Status"] in ("FAIL", "TIMEOUT")
                 or str(r["Status"]).startswith("NORC"))
    total_groups = sum(int(r["Groups"]) for r in rows if isinstance(r["Groups"], int) and r["Groups"] >= 0)
    total_ok = sum(int(r["OK"]) for r in rows if isinstance(r["OK"], int) and r["OK"] >= 0)
    print()
    print(f"Modules : OK={n_ok}  PARTIAL={n_partial}  FAIL={n_fail}  "
          f"NONE={n_none}  (total={len(rows)})")
    print(f"Groups  : {total_ok}/{total_groups} OK")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "generate"
    sys.exit(main(p))
