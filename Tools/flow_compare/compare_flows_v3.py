"""
v3 — like compare_flows_v2.py but with two enhancements:

1. Per-flow LINE NUMBER columns pointing to where each entity row originates
   in the source .mtpl files:
     - identity / .edc rows -> the `FlowItem` line in the Flow block
     - .connectivity.R<n>   -> the `Result <n>` line within that FlowItem
     - .param.<name>        -> the line where `<name> = ...;` appears inside
                               the matching `CSharpTest ... <instance>` block

   Source .mtpls scanned: every `.mtpl` referenced (transitively) by the STPL.
   For now, hard-coded to the two relevant modules:
     Modules/ARR/ARR_CORE_CXX/ARR_CORE_CXX.mtpl
     Modules/ARR/ARR_ATOM_CXX/ARR_ATOM_CXX.mtpl

2. SYMBOLIZED diff columns:
   - "Symbolized" — the common template across all N values, with the differing
     substrings replaced by `<sK>` placeholders. Same-shaped diffs (same hole
     values across all flows) reuse the same symbol within a row AND across
     rows (global symbol map).
   - "<flow>_symbols" — per-flow `s0=val0; s1=val1; ...` listing.

   Example:
     F1: arr_cdie_f1xat_..._galcol_f1_m0_...
     F2: arr_cdie_f2xat_..._galcol_f2_m0_...
     F3: arr_cdie_f3xat_..._galcol_f3_m0_...
     -> Symbolized: arr_cdie_f<s0>xat_..._galcol_f<s0>_m0_...
        F1_symbols: s0=1
        F2_symbols: s0=2
        F3_symbols: s0=3
"""
from __future__ import annotations
import csv
import re
import sys
from collections import OrderedDict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(r"C:\Users\yrakotch\source\repos\nvl_cpu_idg")
SKILL_CSV = ROOT / "Tools" / "flow_compare" / "P16C_all.csv"
# Module being collapsed. The pipeline is iterative: first run uses
# `<module>_orig.mtpl` as input and writes `<module>_bp.mtpl`. Subsequent
# runs use `<module>_bp.mtpl` as input and overwrite it (via temp file).
# `<module>_orig.mtpl` is auto-created on first run as a one-time snapshot
# of `<module>.mtpl` (see `ensure_orig_snapshot()` below).
_MODULE_DIR = ROOT / "Modules" / "ARR" / "ARR_ATOM_CXX"
_MODULE_NAME = _MODULE_DIR.name
_BP_PATH = _MODULE_DIR / f"{_MODULE_NAME}_bp.mtpl"
_ORIG_PATH = _MODULE_DIR / f"{_MODULE_NAME}_orig.mtpl"
_SRC_MTPL = _MODULE_DIR / f"{_MODULE_NAME}.mtpl"


def ensure_orig_snapshot() -> None:
    """Auto-create `<module>_orig.mtpl` on first run by copying the current
    `<module>.mtpl`. Also accepts a legacy `<module>.mtpl_orig` snapshot and
    migrates it to the new name. Idempotent: a no-op if `_orig.mtpl` already
    exists."""
    if _ORIG_PATH.exists():
        return
    legacy = _MODULE_DIR / f"{_MODULE_NAME}.mtpl_orig"
    if legacy.exists():
        legacy.rename(_ORIG_PATH)
        print(f"[orig] migrated legacy snapshot -> {_ORIG_PATH.name}")
        return
    if not _SRC_MTPL.exists():
        raise FileNotFoundError(
            f"Cannot create orig snapshot: source mtpl missing: {_SRC_MTPL}")
    import shutil
    shutil.copy2(_SRC_MTPL, _ORIG_PATH)
    print(f"[orig] created snapshot {_ORIG_PATH.name} from {_SRC_MTPL.name}")


ensure_orig_snapshot()

# XCR comparison: source from `_orig.mtpl` (clean) so previous XAT cycle's
# _bp.mtpl is not picked up.
MTPL_PRIMARY = _ORIG_PATH
MTPL_TEST_SOURCES = [
    MTPL_PRIMARY,
]
OUT_CSV = _MODULE_DIR / f"{_MODULE_NAME}_bp.flows_compare.csv"

# CYCLE-AWARE numbering floor. When running cycle N (N >= 2), symbolize_mtpl
# sets this to the highest `sN` index used by any previous cycle. New
# symbols this cycle get numbers strictly greater than this floor, so
# numbering never collides across cycles. -1 = cycle 1 (start at s0).
PRESEED_MAX_SYMBOL: int = -1

# CYCLE-AWARE seed: when running cycle N (N >= 2) AND the cycle's FLOWS
# overlap with previous cycles, symbolize_mtpl pre-populates this dict
# with `{ hole_tuple_in_FLOWS_order -> 'sN' }` so identical tuples reuse
# the existing name instead of allocating a new one. Empty by default.
PRESEED_SYMBOL_MAP: dict[tuple, str] = {}

FLOW_DEFS = OrderedDict([
    ("ARR_ATOM_CXX_F1XAT", "F1XAT_SubFlow_SPEEDPRL0CPU::"),
    ("ARR_ATOM_CXX_F2XAT", "F2XAT_SubFlow_SPEEDPRL2CPU::"),
    ("ARR_ATOM_CXX_F3XAT", "F3XAT_SubFlow_SPEEDPRL2CPU::"),
])
FLOWS = list(FLOW_DEFS.keys())

NORMALIZE_RULES = [
    (re.compile(r"F[1-5]XAT(LO)?", re.IGNORECASE), "FXAT"),
    (re.compile(r"FMINXAT", re.IGNORECASE), "FXAT"),
    (re.compile(r"_F[1-5]_"), "_F_"),
    (re.compile(r"_FMIN_"), "_F_"),
    (re.compile(r"\d+(?:\.\d+)?\s*(?:GHz|MHz)", re.IGNORECASE), "FREQ"),
    (re.compile(r"hptp\d{3,5}", re.IGNORECASE), "hptpFREQ"),
    (re.compile(r"_(?:800|1200|1600|2000|2400|2800|3000|3200|3600|4000|4100)_"), "_FREQ_"),
    # MTPL templated freq placeholder: `_F_X_` (after the F# collapse above).
    # Skill returns the resolved freq token (e.g. `_1200_`) which normalizes
    # to `_FREQ_`, so map the templated form to the same key for alignment.
    (re.compile(r"_F_X_"), "_F_FREQ_"),
]


def normalize(s: str) -> str:
    out = s
    for rgx, repl in NORMALIZE_RULES:
        out = rgx.sub(repl, out)
    return out


# -------- mtpl helpers --------

def find_block_end(lines: list[str], start_idx: int) -> int:
    depth, started = 0, False
    for i in range(start_idx, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return i
    return len(lines) - 1


FLOWITEM_RE = re.compile(r"^\s*FlowItem\s+(\S+)\s+(\S+)(.*)$")
RESULT_RE = re.compile(r"^\s*Result\s+(\S+)\s*$")
GOTO_RE = re.compile(r"^\s*GoTo\s+([^;]+);")
RETURN_RE = re.compile(r"^\s*Return\s+([^;]+);")


def parse_flow_body(lines: list[str], flow_name: str):
    """Return list of dicts with keys:
       flowItem, instance, edc, connectivity {code -> "GoTo X" / "Return n"},
       flowItem_line (1-based), connectivity_lines {code -> 1-based line}
    """
    rgx = re.compile(rf"^\s*Flow\s+{re.escape(flow_name)}\s*(@\S+)?\s*$")
    out = []
    i = 0
    while i < len(lines):
        if rgx.match(lines[i]):
            j = i
            while j < len(lines) and "{" not in lines[j]:
                j += 1
            end = find_block_end(lines, j)
            k = j + 1
            while k < end:
                m = FLOWITEM_RE.match(lines[k])
                if not m:
                    k += 1
                    continue
                fi_name, inst_name, tail = m.group(1), m.group(2), m.group(3)
                edc = "EDC" if re.search(r"@EDC", tail) else "KILL"
                fi_line = k + 1  # 1-based
                j2 = k
                while j2 < end and "{" not in lines[j2]:
                    j2 += 1
                fi_end = find_block_end(lines, j2)
                conn: dict[str, str] = {}
                conn_lines: dict[str, int] = {}
                cur = None
                cur_line = None
                for kk in range(j2 + 1, fi_end):
                    rm = RESULT_RE.match(lines[kk])
                    if rm:
                        cur = rm.group(1).strip()
                        cur_line = kk + 1
                        continue
                    if cur is None:
                        continue
                    gm = GOTO_RE.match(lines[kk])
                    if gm:
                        conn[cur] = f"GoTo {gm.group(1).strip()}"
                        conn_lines[cur] = cur_line
                        cur = None
                        continue
                    rrm = RETURN_RE.match(lines[kk])
                    if rrm:
                        conn[cur] = f"Return {rrm.group(1).strip()}"
                        conn_lines[cur] = cur_line
                        cur = None
                out.append({
                    "flowItem": fi_name,
                    "instance": inst_name,
                    "edc": edc,
                    "connectivity": conn,
                    "flowItem_line": fi_line,
                    "connectivity_lines": conn_lines,
                })
                k = fi_end + 1
            return out
        i += 1
    return out


def collect_subflows(lines, root_flow_name: str, max_depth: int = 5) -> list[str]:
    """Walk Flow {} bodies starting from `root_flow_name` and collect names of
    nested Flows reached via `GoTo <flow_name>`. A name is treated as a
    sub-flow iff there is a `Flow <name>` definition somewhere in the file
    (i.e. it's not just a sibling FlowItem reference).
    Returns names in discovery order (root excluded). De-duplicated.
    """
    flow_def_lines: dict[str, int] = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*Flow\s+(\S+)\s*(@\S+)?\s*$", ln)
        if m:
            flow_def_lines.setdefault(m.group(1), i)

    seen: set[str] = {root_flow_name}
    order: list[str] = []
    queue: list[tuple[str, int]] = [(root_flow_name, 0)]
    while queue:
        cur, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        body_start = flow_def_lines.get(cur)
        if body_start is None:
            continue
        j = body_start
        while j < len(lines) and "{" not in lines[j]:
            j += 1
        end = find_block_end(lines, j)
        for k in range(j + 1, end):
            gm = GOTO_RE.match(lines[k])
            if not gm:
                continue
            target = gm.group(1).strip()
            if target in flow_def_lines and target not in seen:
                seen.add(target)
                order.append(target)
                queue.append((target, depth + 1))
    return order


# -------- parse CSharpTest definitions for param line numbers --------

TEST_RE = re.compile(r"^\s*CSharpTest\s+\S+\s+(\S+)\s*$")
PARAM_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)$")


def parse_test_param_lines(lines: list[str]) -> dict[str, dict[str, int]]:
    """Return {instance_name: {param_name: 1-based_line_number}}."""
    out: dict[str, dict[str, int]] = {}
    i = 0
    while i < len(lines):
        m = TEST_RE.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group(1)
        j = i
        while j < len(lines) and "{" not in lines[j]:
            j += 1
        end = find_block_end(lines, j)
        params: dict[str, int] = {}
        for kk in range(j + 1, end):
            ln = lines[kk]
            stripped = ln.lstrip()
            if stripped.startswith("#"):
                continue
            pm = PARAM_RE.match(ln)
            if pm:
                pname = pm.group(1)
                params.setdefault(pname, kk + 1)  # first occurrence
        if params:
            out[name] = params
        i = end + 1
    return out


# -------- skill CSV parsing --------

def parse_params(blob: str) -> "OrderedDict[str, str]":
    result: OrderedDict[str, str] = OrderedDict()
    depth = 0
    in_q = False
    buf = []
    parts = []
    i = 0
    while i < len(blob):
        ch = blob[i]
        if ch == '"':
            in_q = not in_q
            buf.append(ch)
        elif not in_q and ch in "([{":
            depth += 1
            buf.append(ch)
        elif not in_q and ch in ")]}":
            depth -= 1
            buf.append(ch)
        elif not in_q and depth == 0 and ch == ";" and (i + 1 < len(blob) and blob[i + 1] == " "):
            parts.append("".join(buf).strip())
            buf = []
            i += 1
        else:
            buf.append(ch)
        i += 1
    if buf:
        parts.append("".join(buf).strip())
    for p in parts:
        if "=" not in p:
            continue
        name, _, val = p.partition("=")
        name = name.strip()
        val = val.strip()
        if len(val) >= 2 and val.startswith('""') and val.endswith('""'):
            # Doubled-quote-escaped style: strip outer pair AND un-double inner.
            val = val[2:-2].replace('""', '"')
        elif len(val) >= 2 and val.startswith('"') and val.endswith('"'):
            # Simple quoted value (no inner doubled quotes by definition).
            # Don't unescape "" here -- doing so corrupts legitimate empty
            # string literals like `If_PseudoVminForwarding(x, "")`.
            val = val[1:-1]
        result[name] = val
    return result


_MTT_FREQ_REVERT = re.compile(r"_F(\d+)_(\d{3,5})_")


def load_skill_csv() -> dict[str, list[dict]]:
    out = {fn: [] for fn in FLOWS}
    with SKILL_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tname = row["Test Instance Name"]
            is_mtt = (row.get("Is MTT") or "").strip().lower() == "yes"
            for fn, prefix in FLOW_DEFS.items():
                if tname.startswith(prefix):
                    bare = tname[len(prefix):]
                    # MultiTrialTest instances are dynamically created at
                    # runtime: skill returns the resolved freq token (e.g.
                    # `_F1_1200_`) but the source mtpl declares them with the
                    # templated `_F1_X_` form, and all references in .sbdefs /
                    # bin lists use that templated form. Revert the freq token
                    # so the per-flow value emitted to the compare CSV matches
                    # the source mtpl exactly.
                    if is_mtt:
                        bare = _MTT_FREQ_REVERT.sub(r"_F\1_X_", bare)
                    out[fn].append({
                        "instance": bare,
                        "params": parse_params(row["Test Parameters"] or ""),
                        "is_mtt": is_mtt,
                    })
                    break
    return out


# -------- diff status --------

def diff_status(values: list[str]) -> str:
    present = [v for v in values if v != ""]
    if len(present) == 0:
        return "OK"
    if len(present) < len(values):
        return "PARTIAL"
    # Strict equality: OK iff all raw values are identical, DIFF otherwise.
    return "OK" if len(set(values)) == 1 else "DIFF"


# -------- symbolization --------

def _common_segments(values: list[str]):
    """Find character segments common to ALL values.
    Returns list of [start_in_each_value, length] aligned tuples in order.
    Strategy: pairwise SequenceMatcher against values[0]; keep only ref positions
    that map (consistently) in every other value, and group consecutive ones into
    runs while keeping the per-value indices monotonic.
    """
    n = len(values)
    if n == 0:
        return []
    ref = values[0]
    if not ref or any(not v for v in values):
        return []
    # pair_match[i-1][r] = position in values[i] aligned to ref position r
    pair_match: list[dict[int, int]] = []
    for i in range(1, n):
        sm = SequenceMatcher(None, ref, values[i], autojunk=False)
        m: dict[int, int] = {}
        for r_start, o_start, length in sm.get_matching_blocks():
            for k in range(length):
                m[r_start + k] = o_start + k
        pair_match.append(m)

    # Walk ref; collect positions present in all others, tracking other-pos.
    segments = []  # list of (starts_per_value, length)
    cur_starts: list[int] | None = None
    cur_len = 0
    last_others: list[int] | None = None  # last assigned other-pos per value (for monotonicity)
    for r in range(len(ref)):
        others = []
        ok = True
        for i in range(1, n):
            o = pair_match[i - 1].get(r)
            if o is None:
                ok = False
                break
            others.append(o)
        if not ok:
            if cur_starts is not None:
                segments.append((cur_starts, cur_len))
                cur_starts, cur_len, last_others = None, 0, None
            continue

        if cur_starts is None:
            # start a new run only if monotonic w.r.t. previous accepted segment
            if segments:
                prev_starts, prev_len = segments[-1]
                ref_min = prev_starts[0] + prev_len
                if r < ref_min:
                    continue
                for i in range(1, n):
                    if others[i - 1] < prev_starts[i] + prev_len:
                        ok = False
                        break
                if not ok:
                    continue
            cur_starts = [r] + others
            cur_len = 1
            last_others = others
        else:
            # extend if all are immediate next char
            if all(others[i] == last_others[i] + 1 for i in range(n - 1)):
                cur_len += 1
                last_others = others
            else:
                segments.append((cur_starts, cur_len))
                cur_starts = [r] + others
                cur_len = 1
                last_others = others
    if cur_starts is not None:
        segments.append((cur_starts, cur_len))
    return segments


def _next_sym_name(symbol_map: dict[tuple, str]) -> str:
    """Return the next free `sN` name, strictly greater than every existing
    symbol number in `symbol_map` AND greater than the cycle-aware floor
    `PRESEED_MAX_SYMBOL`. Cycle-safe: when previous cycles used s0..sK,
    cycle N starts at sK+1 and never collides."""
    max_n = PRESEED_MAX_SYMBOL
    for s in symbol_map.values():
        if s.startswith("s") and s[1:].isdigit():
            n = int(s[1:])
            if n > max_n:
                max_n = n
    return f"s{max_n + 1}"


def symbolize(values: list[str], symbol_map: dict[tuple, str]):
    """Return (template_str, [(symbol, hole_values_per_value), ...])."""
    n = len(values)
    if any(v == "" for v in values):
        return "", []
    if len(set(values)) == 1:
        return values[0], []

    segs = _common_segments(values)
    pieces = []
    sym_assignments: list[tuple[str, tuple[str, ...]]] = []
    last_ends = [0] * n  # end position of last emitted common segment per value
    for starts, length in segs:
        # hole before this common segment
        hole = tuple(values[i][last_ends[i]:starts[i]] for i in range(n))
        if any(h for h in hole):
            if hole in symbol_map:
                sym = symbol_map[hole]
            else:
                sym = _next_sym_name(symbol_map)
                symbol_map[hole] = sym
            pieces.append(f"<{sym}>")
            sym_assignments.append((sym, hole))
        # emit the common literal (use ref text)
        pieces.append(values[0][starts[0]:starts[0] + length])
        for i in range(n):
            last_ends[i] = starts[i] + length
    # trailing hole
    hole = tuple(values[i][last_ends[i]:] for i in range(n))
    if any(h for h in hole):
        if hole in symbol_map:
            sym = symbol_map[hole]
        else:
            sym = _next_sym_name(symbol_map)
            symbol_map[hole] = sym
        pieces.append(f"<{sym}>")
        sym_assignments.append((sym, hole))
    return "".join(pieces), sym_assignments


def fmt_symbols_for_value(idx: int, sym_assignments) -> str:
    if not sym_assignments:
        return ""
    # de-dup by sym name keeping first occurrence
    seen = set()
    parts = []
    for sym, hole in sym_assignments:
        if sym in seen:
            continue
        seen.add(sym)
        parts.append(f"{sym}={hole[idx]}")
    return "; ".join(parts)


# -------- main --------

def main() -> int:
    if not SKILL_CSV.exists():
        print(f"ERROR: skill CSV not found: {SKILL_CSV}", file=sys.stderr)
        return 2

    primary_text = MTPL_PRIMARY.read_text(encoding="utf-8", errors="replace")
    nl = "\r\n" if "\r\n" in primary_text[:4096] else "\n"
    primary_lines = primary_text.split(nl)

    # Discover sub-flows reachable from each root input flow (per-flow set).
    subflows_per_root = {fn: collect_subflows(primary_lines, fn) for fn in FLOWS}
    for fn in FLOWS:
        sf = subflows_per_root[fn]
        if sf:
            print(f"  subflows {fn}: {len(sf)} -> {sf}")
        else:
            print(f"  subflows {fn}: (none)")

    # For each (root, body-flow) pair, parse the FlowItems. Body-flow is the
    # root itself plus any reachable sub-flow.
    mtpl_per_flow_per_subflow: dict[str, dict[str, list[dict]]] = {}
    for fn in FLOWS:
        per_sf: dict[str, list[dict]] = {}
        per_sf[fn] = parse_flow_body(primary_lines, fn)
        for sf in subflows_per_root[fn]:
            per_sf[sf] = parse_flow_body(primary_lines, sf)
        mtpl_per_flow_per_subflow[fn] = per_sf

    # Convenience: same-as-before per-root primary body
    mtpl_per_flow = {fn: mtpl_per_flow_per_subflow[fn][fn] for fn in FLOWS}
    for fn in FLOWS:
        print(f"  mtpl  {fn}: {len(mtpl_per_flow[fn])} FlowItems (root)")

    # parse test param line numbers from all source mtpls; later wins iff missing
    param_lines: dict[str, dict[str, int]] = {}
    param_source_file: dict[str, Path] = {}
    for src in MTPL_TEST_SOURCES:
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        src_nl = "\r\n" if "\r\n" in text[:4096] else "\n"
        src_lines = text.split(src_nl)
        per_inst = parse_test_param_lines(src_lines)
        for inst, params in per_inst.items():
            if inst not in param_lines:
                param_lines[inst] = {}
                param_source_file[inst] = src
            for pname, ln in params.items():
                param_lines[inst].setdefault(pname, ln)

    skill_per_flow = load_skill_csv()
    for fn in FLOWS:
        print(f"  skill {fn}: {len(skill_per_flow[fn])} instances")

    # merge per-flow items with mtpl info.
    # SCOPE FILTER: drop instances that have no FlowItem in the module's
    # own .mtpl for ANY of the compared flows. These are runtime instances
    # belonging to sibling-module flows that share the same execution
    # scope (e.g. F1XCR_SubFlow_SPEEDPRL0CPU::), not to the module under
    # comparison. Keeping them produces orphan symbols that the bp
    # rewriter cannot anchor in the local source text.
    # Match on NORMALIZED names: skill returns runtime-resolved instance
    # names (e.g. `..._3200_COMBINED`) while FlowItems in the mtpl carry
    # templated names (e.g. `..._X_COMBINED`). normalize() collapses both
    # forms (frequency token, F#) into the same canonical key.
    in_module_norm: set[str] = set()
    for fn in FLOWS:
        for it in mtpl_per_flow[fn]:
            in_module_norm.add(normalize(it["instance"]))
    dropped_cross_module = 0
    per_flow_items: dict[str, list[dict]] = {}
    for fn in FLOWS:
        mtpl_idx = {it["instance"]: it for it in mtpl_per_flow[fn]}
        merged = []
        for s in skill_per_flow[fn]:
            if normalize(s["instance"]) not in in_module_norm:
                dropped_cross_module += 1
                continue
            m = mtpl_idx.get(s["instance"])
            merged.append({
                "instance": s["instance"],
                "edc": (m["edc"] if m else ""),
                "connectivity": (m["connectivity"] if m else {}),
                "flowItem_line": (m["flowItem_line"] if m else None),
                "connectivity_lines": (m["connectivity_lines"] if m else {}),
                "params": s["params"],
                "is_mtt": s.get("is_mtt", False),
            })
        per_flow_items[fn] = merged
    if dropped_cross_module:
        print(f"  scope-filter: dropped {dropped_cross_module} cross-module "
              f"instance(s) (no FlowItem in module's own mtpl)")

    # align by normalized instance name
    per_flow_keys = {
        fn: [(normalize(it["instance"]), it) for it in per_flow_items[fn]]
        for fn in FLOWS
    }
    seen = set()
    ordered_keys: list[str] = []
    for fn in FLOWS:
        for key, _ in per_flow_keys[fn]:
            if key not in seen:
                seen.add(key)
                ordered_keys.append(key)

    flow_index: dict[str, dict[str, dict]] = {}
    for fn in FLOWS:
        idx: dict[str, dict] = {}
        for key, it in per_flow_keys[fn]:
            base = key
            n = 1
            while base in idx:
                n += 1
                base = f"{key}#{n}"
            idx[base] = it
        flow_index[fn] = idx

    rows: list[dict] = []
    counts = {"OK": 0, "DIFF": 0, "PARTIAL": 0}
    diff_entities: list[str] = []

    # GLOBAL symbol map shared across rows so identical hole-tuples reuse the
    # same symbol name throughout the whole file. Numbers above any
    # previously-used cycle's max are produced by `_next_sym_name` (which
    # consults the module-level `PRESEED_MAX_SYMBOL` floor). When the
    # cycle's FLOWS overlap with a previous cycle, the map is pre-seeded
    # with `PRESEED_SYMBOL_MAP` so identical hole-tuples REUSE the
    # previously-assigned `sN` name.
    global_symbol_map: dict[tuple, str] = dict(PRESEED_SYMBOL_MAP)

    line_cols = [f"{fn}_line" for fn in FLOWS]
    sym_cols = [f"{fn}_symbols" for fn in FLOWS]
    fieldnames = ["Entity", *FLOWS, "DIFF", "Is_MTT", *line_cols, "Symbolized", *sym_cols]

    def emit(entity: str, vals: list[str], lines_per_flow: list, force_symbolize: bool = False, is_mtt: bool = False):
        status = diff_status(vals)
        counts[status] += 1
        if status == "DIFF":
            diff_entities.append(entity)
        # Symbolize whenever raw values differ across flows, even when
        # `diff_status` reports OK (which uses normalized form). This makes
        # symbolic templates appear for instance/param rows whose raw text
        # carries the F1/F2/F3 / freq tokens that normalize collapses.
        non_empty = [v for v in vals if v != ""]
        raw_differs = len(set(non_empty)) > 1
        if status == "DIFF" or raw_differs or (force_symbolize and len(set(vals)) > 1):
            template, sym_assigns = symbolize(vals, global_symbol_map)
        else:
            template, sym_assigns = "", []
        row = {"Entity": entity}
        for fn, v in zip(FLOWS, vals):
            row[fn] = v
        row["DIFF"] = status
        row["Is_MTT"] = "Yes" if is_mtt else "No"
        for col, ln in zip(line_cols, lines_per_flow):
            row[col] = ("" if ln is None else ln)
        row["Symbolized"] = template
        for i, fn in enumerate(FLOWS):
            row[f"{fn}_symbols"] = fmt_symbols_for_value(i, sym_assigns)
        rows.append(row)

    # Top-level entity row: the flow names themselves. This feeds the global
    # symbol map so flow-token differences (e.g. `1`/`2`/`3`) get an `\s0\`
    # that is reused throughout the rest of the comparison.
    flow_lines = []
    for fn in FLOWS:
        items_for_fn = mtpl_per_flow.get(fn, [])
        flow_lines.append(items_for_fn[0]["flowItem_line"] if items_for_fn else None)
    emit("<flow>", list(FLOWS), flow_lines, force_symbolize=True)

    for key in ordered_keys:
        items = [flow_index[fn].get(key) for fn in FLOWS]
        key_is_mtt = any(bool(it.get("is_mtt")) for it in items if it)

        # identity
        emit(
            key,
            [it["instance"] if it else "" for it in items],
            [it["flowItem_line"] if it else None for it in items],
            is_mtt=key_is_mtt,
        )
        # edc — same line as FlowItem
        emit(
            f"{key}.edc",
            [it["edc"] if it else "" for it in items],
            [it["flowItem_line"] if it else None for it in items],
            is_mtt=key_is_mtt,
        )
        # connectivity rows
        codes = []
        seen_c = set()
        for it in items:
            if not it:
                continue
            for c in it["connectivity"].keys():
                if c not in seen_c:
                    seen_c.add(c)
                    codes.append(c)

        def code_key(c):
            try:
                return (0, int(c))
            except Exception:
                return (1, c)

        codes.sort(key=code_key)
        for c in codes:
            emit(
                f"{key}.connectivity.R{c}",
                [it["connectivity"].get(c, "") if it else "" for it in items],
                [it["connectivity_lines"].get(c) if it else None for it in items],
                is_mtt=key_is_mtt,
            )
        # params
        param_names = []
        seen_p = set()
        for it in items:
            if not it:
                continue
            for p in it["params"].keys():
                if p not in seen_p:
                    seen_p.add(p)
                    param_names.append(p)
        for p in param_names:
            # Skip params that are pre-normalized to a single value across
            # all flows by symbolize_mtpl._apply_prework -- they would only
            # add noise (always OK) to the comparison.
            if p in ("BaseNumbers", "BypassPort"):
                continue
            vals = [it["params"].get(p, "") if it else "" for it in items]
            line_vals = []
            for it in items:
                if not it:
                    line_vals.append(None)
                    continue
                pl = param_lines.get(it["instance"], {}).get(p)
                line_vals.append(pl)
            emit(f"{key}.param.{p}", vals, line_vals, is_mtt=key_is_mtt)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print()
    print("=" * 72)
    print("Summary")
    print("=" * 72)
    print(f"  Total rows : {len(rows)}")
    print(f"  OK         : {counts['OK']}")
    print(f"  DIFF       : {counts['DIFF']}")
    print(f"  PARTIAL    : {counts['PARTIAL']}")
    print(f"  Symbols    : {len(global_symbol_map)}")
    print()
    print(f"DIFF entities ({len(diff_entities)}):")
    for e in diff_entities:
        print(f"  {e}")
    print()
    print(f"CSV written: {OUT_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
