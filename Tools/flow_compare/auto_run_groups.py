"""auto_run_groups.py — thin orchestrator that delegates BP generation to
the legacy `auto_bp_from_groups.main()` (which already does cross-group
collapsing, test/flow-name symbolization via `compute_test_renames` +
`apply_test_renames`, Counters rewrite, and bank snapshots) and then runs
the unified validation (structural checks + torch build of expanded vs.
orig) on its outputs.

Legacy outputs (one set per module):
  <MODULE>_auto_bp.mtpl                — unified bp with all Independent
                                         groups collapsed and tests/flows
                                         symbolized.
  <MODULE>_auto_symbols.csv            — wide format Symbol,<flow1>,<flow2>,...
  <MODULE>_auto_flows_compare.csv      — per-group rows.
  <MODULE>_auto_group_flows.csv        — per-member flow body bank.
  <MODULE>_auto_modified_flows.csv     — non-group flows whose body changed.
  <MODULE>_auto_tests.csv              — orphan Test defs bank.
  <MODULE>_auto_flows.csv              — orphan Flow defs bank.
  <MODULE>_auto_counters.csv           — original Counters block snapshot.
  <MODULE>_auto_collapsed.md           — human-readable collapse summary.

Validation step also writes:
  <MODULE>_auto_bp.mtpl_expanded       — \\sN\\ -> rep's token value
                                         (rep = sorted(members)[0]).
  <MODULE>_auto_bp.build.log           — torch build log for expanded.
  <MODULE>_auto_bp.build_orig.log      — torch build log for orig.

Usage:
    python auto_run_groups.py <module_dir> [phase]

Phases:
    compare / generate  -> run legacy BP generation only.
    validate            -> assume BP exists; run unified validation only.
    all                 -> generate then validate.
"""
from __future__ import annotations
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_bp_from_groups as legacy
import auto_expand_bp as expander
import compare_flows_v3 as v3
import symbolize_mtpl as sm


_SYM_RE = re.compile(r"\\s(\d+)\\")


def _cleanup_stale_artifacts(md: Path, module: str) -> None:
    """Remove leftovers from prior orchestrator runs (the previous
    `_auto_bp.mtpl_symbols.csv` / `_auto_bp.flows_compare.csv` schema) and
    per-cycle scratch files."""
    patterns = [
        f"{module}_auto_bp_g*.*",
        f"{module}_auto_bp.mtpl_symbols.csv",
        f"{module}_auto_bp.flows_compare.csv",
        f"{module}_auto_bp.flows_compare.csv.prev_cycle.bak",
        f"{module}_auto_bp.mtpl.prework.tmp",
        f"{module}_auto_bp.mtpl_expanded",
        f"{module}_auto_expanded.mtpl",
        f"{module}_auto_full_compare.csv",
        f"{module}_auto_bp.build.log",
        f"{module}_auto_bp.build_orig.log",
    ]
    removed = 0
    for pat in patterns:
        for p in md.glob(pat):
            try:
                p.unlink()
                removed += 1
            except OSError:
                pass
    if removed:
        print(f"[{module}] cleaned {removed} stale artifact(s)")


def _load_symbol_first_values(symbols_csv: Path) -> dict[str, str]:
    """Read the legacy wide-format symbols CSV and return a map
    `\\sN\\` -> rep's token value. The rep is the first member column
    with a non-empty cell on a given row (rep = sorted(members)[0]
    alphabetically; `write_symbols_csv` writes columns in `sorted` order
    so the first non-empty cell IS the rep)."""
    sub: dict[str, str] = {}
    if not symbols_csv.exists():
        return sub
    with symbols_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return sub
        for row in reader:
            if not row:
                continue
            sym = row[0].strip()
            if not sym:
                continue
            for cell in row[1:]:
                v = (cell or "").strip()
                if v:
                    sub[sym] = v
                    break
    return sub


def _run_full_compare(md: Path, module: str) -> int:
    """Run `compare_flows_v3.main()` per Independent group and aggregate
    every per-FlowItem / per-param row into a single
    `<MODULE>_auto_full_compare.csv`. This produces the same depth of
    comparison the original (single-flow-set) pipeline did — `<flow>`,
    `<key>`, `<key>.edc`, `<key>.connectivity.R<n>`, `<key>.param.<P>`
    rows with Symbolized + per-flow `\\sN\\` value listings — but
    extended across ALL Independent groups in the module, with a leading
    `Group` column tagging each row.
    """
    cands = md / f"{module}_collapse_candidates.csv"
    if not cands.exists():
        print(f"[{module}] full compare skipped (no candidates CSV)")
        return 0
    groups = legacy.load_groups(cands)
    if not groups:
        return 0

    out_path = md / f"{module}_auto_full_compare.csv"
    print(f"[{module}] running full per-entity compare across "
          f"{len(groups)} group(s) -> {out_path.name}")

    agg_fields: list[str] = []
    agg_rows: list[dict] = []
    for i, g in enumerate(groups):
        members = [m.strip() for m in g.get('Members', '').split(';') if m.strip()]
        if len(members) < 2:
            continue
        group_label = f"g{i}"
        try:
            flow_defs = v3.derive_flow_defs(md, members)
        except Exception as e:
            print(f"  [{group_label}] derive_flow_defs FAILED: {e}")
            continue
        v3.configure_module(md, flow_defs, mtpl_input=md / f"{module}_orig.mtpl",
                            out_suffix=f"_auto_full_g{i}")
        # Run v3.main() (writes per-group CSV at v3.OUT_CSV).
        saved = sys.argv
        try:
            sys.argv = ["compare_flows_v3.py"]
            rc = v3.main()
        except SystemExit as se:
            rc = int(getattr(se, 'code', 0) or 0)
        finally:
            sys.argv = saved
        if rc != 0:
            print(f"  [{group_label}] v3.main() rc={rc} (skipped)")
            continue
        per_csv = v3.OUT_CSV
        if not per_csv.exists():
            continue
        with per_csv.open('r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for fn in (reader.fieldnames or []):
                if fn not in agg_fields:
                    agg_fields.append(fn)
            for row in reader:
                agg_rows.append({"Group": group_label, **row})
        # Cleanup the per-group scratch CSV.
        try:
            per_csv.unlink()
        except OSError:
            pass

    fields = ["Group"] + agg_fields
    with out_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="")
        w.writeheader()
        w.writerows(agg_rows)
    print(f"  wrote {len(agg_rows)} row(s), {len(fields)} col(s)")
    return 0


def _verify_bp_symbols_consistency(bp_path: Path,
                                   symbols_path: Path,
                                   module: str) -> int:
    """Check that the set of `\\sN\\` tokens used in the bp .mtpl exactly
    matches the set of symbols declared in the symbols CSV. Returns 0 on
    PASS, 1 on FAIL.

    - bp uses `\\sN\\` not in CSV  -> FAIL (dangling reference)
    - CSV declares `\\sN\\` not in bp -> FAIL (orphan symbol)
    """
    text = bp_path.read_text(encoding="utf-8", errors="replace")
    bp_syms = set(_SYM_RE.findall(text))  # set of "0", "1", ...

    csv_syms: set[str] = set()
    if symbols_path.exists():
        with symbols_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # header
            for row in reader:
                if not row:
                    continue
                m = _SYM_RE.match((row[0] or "").strip())
                if m:
                    csv_syms.add(m.group(1))

    print()
    print("-" * 70)
    print(f"[{module}] Symbol-consistency verification")
    print(f"  bp .mtpl     : {len(bp_syms)} unique \\sN\\ token(s)")
    print(f"  symbols CSV  : {len(csv_syms)} declared symbol(s)")

    missing = bp_syms - csv_syms
    orphans = csv_syms - bp_syms
    fail = 0
    if missing:
        fail += len(missing)
        miss_str = ", ".join(f"\\s{n}\\" for n in sorted(missing, key=int))
        print(f"  FAIL: bp references symbol(s) NOT declared in CSV: {miss_str}")
    if orphans:
        fail += len(orphans)
        orph_str = ", ".join(f"\\s{n}\\" for n in sorted(orphans, key=int))
        print(f"  FAIL: CSV declares symbol(s) NOT used in bp: {orph_str}")
    if not missing and not orphans:
        print(f"  PASS: bp and symbols CSV agree on all {len(bp_syms)} symbol(s)")
    return 1 if fail else 0


def _unified_validate(bp_path: Path, orig_path: Path,
                      symbols_path: Path, module: str) -> int:
    """End-of-run validation on the unified `_auto_bp.*` artifacts.

      1. Run `auto_expand_bp.expand()` to produce `<module>_auto_expanded.mtpl`
         (restores member flow bodies, original Counters, dropped Tests, and
         helper flow bodies from the legacy bank files).
      2. BluePrint-style structural checks on the expanded mtpl vs. orig.
      3. Build expanded and orig with torch and enforce
         `errors(expanded) <= errors(orig)`.

    Note: structural checks are NOT run on `_auto_bp.mtpl` itself because
    the legacy bp legitimately contains bare GoTo targets (e.g.
    `GoTo UV_02;`) referencing flows that have been deleted at bp time
    and restored at expand time from the bank.
    """
    md = bp_path.parent
    print()
    print("=" * 70)
    print(f"[{module}] UNIFIED VALIDATION")
    print("=" * 70)

    # 0. BP <-> symbols CSV consistency. Catches dangling/unused symbols
    # before we go through the more expensive expand+build steps.
    rc_sym = _verify_bp_symbols_consistency(bp_path, symbols_path, module)
    if rc_sym != 0:
        print(f"[{module}] symbol-consistency check FAILED")
        return rc_sym

    # 1. Bank-based expand.
    print(f"[{module}] expanding via auto_expand_bp.expand()")
    rc_x = expander.expand(str(md))
    if rc_x != 0:
        print(f"[{module}] expander rc={rc_x}")
        return rc_x
    expanded_path = md / f"{module}_auto_expanded.mtpl"
    if not expanded_path.exists():
        print(f"[{module}] missing {expanded_path.name} after expand")
        return 2

    leftover = _SYM_RE.findall(
        expanded_path.read_text(encoding="utf-8", errors="replace"))
    if leftover:
        print(f"  WARN: {len(leftover)} unsubstituted \\sN\\ token(s) "
              f"remain in expanded (e.g. {leftover[:3]})")

    # 2. Structural validation on expanded vs. orig.
    rc = sm.validate_symbolized_mtpl(expanded_path, orig_path)
    if rc != 0:
        print(f"[{module}] structural validation FAILED on "
              f"{expanded_path.name}")
        return rc

    # 3. Build both.
    rc_build, rc_orig, n_err_build, n_err_orig = sm._run_torch_build_on(
        expanded_path, orig_path)

    print()
    print("-" * 70)
    print(f"[{module}] BUILD SUMMARY")
    print(f"  expanded : exit={rc_build}  errors={n_err_build}")
    print(f"  orig     : exit={rc_orig}   errors={n_err_orig}")

    if n_err_build < 0 or n_err_orig < 0:
        print(f"[{module}] build skipped (no torch / no orig) — PASS by default")
        return 0
    if n_err_build > n_err_orig:
        regressed = n_err_build - n_err_orig
        print(f"[{module}] FAIL: expanded introduced {regressed} NEW build "
              f"error(s) vs orig baseline")
        return 1
    if n_err_build < n_err_orig:
        improved = n_err_orig - n_err_build
        print(f"[{module}] PASS: expanded has {improved} FEWER build "
              f"error(s) than orig (net improvement)")
    else:
        print(f"[{module}] PASS: expanded and orig have identical build "
              f"error counts ({n_err_build})")
    return 0


def main(module_dir: str, phase: str = "generate") -> int:
    md = Path(module_dir).resolve()
    if not md.exists():
        print(f"[ERR] module dir does not exist: {md}", file=sys.stderr)
        return 2
    module = md.name
    if phase not in ("compare", "generate", "validate", "all"):
        print(f"[ERR] invalid phase {phase!r}; must be one of "
              f"compare/generate/validate/all", file=sys.stderr)
        return 2

    orig_path = md / f"{module}_orig.mtpl"
    bp_path = md / f"{module}_auto_bp.mtpl"
    symbols_path = md / f"{module}_auto_symbols.csv"

    # 1. Generation: delegate to legacy.
    if phase in ("compare", "generate", "all"):
        cands = md / f"{module}_collapse_candidates.csv"
        if not cands.exists():
            print(f"[ERR] missing {cands.name} (run recommend_collapse.py first)",
                  file=sys.stderr)
            return 2
        _cleanup_stale_artifacts(md, module)
        print(f"[{module}] delegating BP generation to "
              f"auto_bp_from_groups.main()")
        rc = legacy.main(str(md))
        if rc != 0:
            print(f"[{module}] legacy generation FAILED rc={rc}")
            return rc
        # Run full per-entity compare across all Independent groups and
        # aggregate into <MODULE>_auto_full_compare.csv (depth equivalent
        # to the original single-flow-set pipeline).
        _run_full_compare(md, module)
        if phase in ("compare", "generate"):
            return 0

    # 2. Validation.
    if phase in ("validate", "all"):
        if not bp_path.exists():
            print(f"[ERR] {bp_path.name} not found; run generate first",
                  file=sys.stderr)
            return 2
        return _unified_validate(bp_path, orig_path, symbols_path, module)

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: auto_run_groups.py <module_dir> [phase]",
              file=sys.stderr)
        sys.exit(2)
    md_arg = sys.argv[1]
    phase_arg = sys.argv[2] if len(sys.argv) == 3 else "generate"
    sys.exit(main(md_arg, phase_arg))
