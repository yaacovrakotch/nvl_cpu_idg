r"""
Produce a collapsed BluePrint version of the module's mtpl that contains
only the kept flow (F1XAT), with that flow's test parameters rewritten to
the symbolized template form (e.g. `arr_cdie_f\s0\xat_...`), plus a CSV
mapping each symbol to its per-flow value.

Iterative pipeline (input source picked by compare_flows_v3.MTPL_PRIMARY):
  - First run : input = <module>.mtpl_orig
  - Re-runs   : input = <module>_bp.mtpl  (overwritten in place via temp file)

Outputs (siblings of the source .mtpl):
  <module>_bp.mtpl                  (collapsed/symbolized)
  <module>_bp.mtpl_symbols.csv      (per-flow values for each symbol)
  <module>_bp.mtpl_expanded         (expanded back to a buildable mtpl using
                                     the kept-flow column from the symbols CSV)

Reuses helpers and global state derivation from compare_flows_v3.
"""
from __future__ import annotations
import csv
import os
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

import compare_flows_v3 as v3

KEEP_FLOW = "ARR_ATOM_CXX_F1XAT"
REMOVE_FLOWS = ["ARR_ATOM_CXX_F2XAT", "ARR_ATOM_CXX_F3XAT"]
ALL_FLOWS = [KEEP_FLOW, *REMOVE_FLOWS]
SYMBOL_OPEN = "\\"   # \s0\
SYMBOL_CLOSE = "\\"

# Output naming: <module>_bp.mtpl + sidecar files. Resolved against the
# module directory of MTPL_PRIMARY (which is _bp.mtpl on re-runs, .mtpl_orig
# on first run -- both live in the same module dir).
_MODULE_DIR = v3.MTPL_PRIMARY.parent
_MODULE_NAME = _MODULE_DIR.name
OUT_MTPL = _MODULE_DIR / f"{_MODULE_NAME}_bp.mtpl"
OUT_SYMBOLS = _MODULE_DIR / f"{_MODULE_NAME}_bp.mtpl_symbols.csv"
OUT_EXPANDED = _MODULE_DIR / f"{_MODULE_NAME}_bp.mtpl_expanded"


def _find_flow_block(lines, flow_name):
    rgx = re.compile(rf"^\s*Flow\s+{re.escape(flow_name)}\s*(@\S+)?\s*$")
    for i, line in enumerate(lines):
        if rgx.match(line):
            j = i
            while j < len(lines) and "{" not in lines[j]:
                j += 1
            end = v3.find_block_end(lines, j)
            return (i, end)
    return None


def _scan_flow_refs(lines, start, end):
    """Inside a Flow {...} block, collect referenced test instance names
    (FlowItem 2nd token + GoTo targets) and counter names (IncrementCounters X)."""
    test_names: set[str] = set()
    counter_names: set[str] = set()
    incr_re = re.compile(r"^\s*IncrementCounters\s+([^;]+);")
    goto_re = re.compile(r"^\s*GoTo\s+([^;]+);")
    for k in range(start, end + 1):
        m = v3.FLOWITEM_RE.match(lines[k])
        if m:
            test_names.add(m.group(2))
            continue
        gm = goto_re.match(lines[k])
        if gm:
            target = gm.group(1).strip()
            # GoTo target could be a sub-flow or a test instance — keep as-is
            test_names.add(target)
            continue
        im = incr_re.match(lines[k])
        if im:
            for c in im.group(1).split(","):
                c = c.strip()
                # strip optional `Module::` prefix
                if "::" in c:
                    c = c.split("::")[-1]
                if c:
                    counter_names.add(c)
    return test_names, counter_names


def _scan_outside_refs(lines, removed_blocks):
    """Return (test_names, counter_names) referenced in any OTHER Flow{} block
    (i.e. not in `removed_blocks` and not the kept flow). Test execution refs
    live in FlowItem / GoTo / IncrementCounters lines inside Flow blocks.
    Names appearing only in Counter declarations or SetBin tokens are derived
    and not counted as live refs."""
    in_removed = [False] * len(lines)
    for s, e in removed_blocks:
        for i in range(s, e + 1):
            in_removed[i] = True
    test_names: set[str] = set()
    counter_names: set[str] = set()
    incr_re = re.compile(r"^\s*IncrementCounters\s+([^;]+);")
    goto_re = re.compile(r"^\s*GoTo\s+([^;]+);")
    flow_re = re.compile(r"^\s*Flow\s+(\S+)\s*(@\S+)?\s*$")
    i = 0
    while i < len(lines):
        if in_removed[i]:
            i += 1
            continue
        if not flow_re.match(lines[i]):
            i += 1
            continue
        j = i
        while j < len(lines) and "{" not in lines[j]:
            j += 1
        end = v3.find_block_end(lines, j)
        for k in range(i, end + 1):
            if in_removed[k]:
                continue
            ln = lines[k]
            m = v3.FLOWITEM_RE.match(ln)
            if m:
                test_names.add(m.group(2))
                continue
            gm = goto_re.match(ln)
            if gm:
                test_names.add(gm.group(1).strip())
                continue
            im = incr_re.match(ln)
            if im:
                for c in im.group(1).split(","):
                    c = c.strip()
                    if "::" in c:
                        c = c.split("::")[-1]
                    if c:
                        counter_names.add(c)
        i = end + 1
    return test_names, counter_names


def _format_sym(sym: str) -> str:
    return f"{SYMBOL_OPEN}{sym}{SYMBOL_CLOSE}"


_SYM_TOKEN_RE = re.compile(r"\\s(\d+)\\")


def _merge_adjacent_symbols(mtpl_path: Path,
                            symbol_map: dict[tuple, str]) -> None:
    """Collapse always-adjacent symbol pairs in `mtpl_path` and the in-memory
    `symbol_map`. A pair (sN, sM) is merged iff:
      * every occurrence of sN in the file is immediately followed by sM, AND
      * every occurrence of sM in the file is immediately preceded by sN.
    The merged symbol replaces sN; sM is removed. Per-flow values become the
    char-wise concatenation. Iterates until no more pairs found (handles 3+
    consecutive symbols collapsing into one)."""
    text = mtpl_path.read_text(encoding="utf-8", errors="replace")
    # Reverse-lookup: sym_name -> hole tuple.
    sym_to_hole = {sym: hole for hole, sym in symbol_map.items()}

    total_merges = 0
    while True:
        # Count occurrences of each symbol name AND of each adjacent pair.
        all_occ: dict[str, int] = {}
        for m in _SYM_TOKEN_RE.finditer(text):
            n = m.group(1)
            all_occ[n] = all_occ.get(n, 0) + 1

        adj_pairs: dict[tuple[str, str], int] = {}
        adj_re = re.compile(r"\\s(\d+)\\\\s(\d+)\\")
        for m in adj_re.finditer(text):
            a, b = m.group(1), m.group(2)
            if a == b:
                continue  # don't merge a symbol with itself
            adj_pairs[(a, b)] = adj_pairs.get((a, b), 0) + 1

        # Find a mergeable pair: pair_count == count(a) == count(b).
        merge: tuple[str, str] | None = None
        for (a, b), c in adj_pairs.items():
            if c == all_occ.get(a, 0) and c == all_occ.get(b, 0):
                merge = (a, b)
                break

        if merge is None:
            break

        a, b = merge
        sym_a, sym_b = f"s{a}", f"s{b}"
        hole_a = sym_to_hole.get(sym_a)
        hole_b = sym_to_hole.get(sym_b)
        if hole_a is None or hole_b is None:
            break  # safety: refuse if either side isn't in the map
        merged_hole = tuple(hole_a[i] + hole_b[i] for i in range(len(hole_a)))

        # Replace `\sa\\sb\` with `\sa\` (keep sym_a, drop sym_b).
        text = text.replace(f"\\s{a}\\\\s{b}\\", f"\\s{a}\\")

        # Update map: remove old hole_a, hole_b; add merged_hole -> sym_a.
        # NOTE: there may already be an entry with merged_hole (collision);
        # if so we keep sym_a as the canonical name and rewrite uses of the
        # collided one. Skip that rewrite for simplicity unless it occurs.
        del symbol_map[hole_a]
        del symbol_map[hole_b]
        symbol_map[merged_hole] = sym_a
        sym_to_hole[sym_a] = merged_hole
        del sym_to_hole[sym_b]

        print(f"Merged adjacent symbols   : \\s{a}\\\\s{b}\\ -> \\s{a}\\  "
              f"(values now {merged_hole})")
        total_merges += 1

    if total_merges == 0:
        return
    # Persist the rewritten mtpl atomically.
    tmp_out = mtpl_path.with_suffix(mtpl_path.suffix + ".tmp")
    tmp_out.write_text(text, encoding="utf-8", newline="")
    if mtpl_path.exists():
        mtpl_path.unlink()
    tmp_out.replace(mtpl_path)
    print(f"Symbol merges performed   : {total_merges}")


_UNDERSCORE_SEG_RE = re.compile(r"(?<=_)[^_\r\n]+(?=_)")


def _merge_underscore_segments(mtpl_path: Path,
                               symbol_map: dict[tuple, str]) -> None:
    """Generalized merge: collapse every `\\sA\\lit1\\sB\\lit2...\\sZ\\` run
    that sits BETWEEN two `_` chars (no `_` inside) into one symbol, when:
      * the run contains >= 2 symbol tokens, AND
      * every involved symbol's total occurrences across the file are
        accounted for by occurrences of this exact segment pattern.
    Per-flow merged values are the textual concatenation of the originals'
    per-flow values interleaved with the literal pieces.
    Iterates until stable."""
    text = mtpl_path.read_text(encoding="utf-8", errors="replace")
    sym_to_hole = {sym: hole for hole, sym in symbol_map.items()}
    n_flows = len(next(iter(symbol_map))) if symbol_map else 0
    if n_flows == 0:
        return

    sym_count_re = _SYM_TOKEN_RE
    total = 0
    while True:
        # Collect candidate segments: keep ones with >=2 symbol tokens.
        # Also count occurrences of each (deduplicated) segment string.
        seg_counts: dict[str, int] = {}
        for m in _UNDERSCORE_SEG_RE.finditer(text):
            seg = m.group(0)
            syms_in_seg = sym_count_re.findall(seg)
            if len(syms_in_seg) < 2:
                continue
            seg_counts[seg] = seg_counts.get(seg, 0) + 1

        # Find a segment whose involved symbols' total file-counts equal the
        # multiplicity implied by this one segment alone (i.e. exclusive use).
        chosen: tuple[str, int, list[str]] | None = None
        for seg, cnt in seg_counts.items():
            sym_nums = sym_count_re.findall(seg)
            ok = True
            seen: dict[str, int] = {}
            for n in sym_nums:
                seen[n] = seen.get(n, 0) + 1
            for n, expected_per in seen.items():
                total_file = len(sym_count_re.findall(text)) if False else None
                # count this specific token in the whole text
                file_count = text.count(f"\\s{n}\\")
                if file_count != cnt * expected_per:
                    ok = False
                    break
            if ok:
                chosen = (seg, cnt, sym_nums)
                break

        if chosen is None:
            break

        seg, cnt, sym_nums = chosen
        # Decompose seg into ordered pieces of literals + symbol refs.
        pieces: list[tuple[str, str]] = []
        idx = 0
        for m in sym_count_re.finditer(seg):
            if m.start() > idx:
                pieces.append(("lit", seg[idx:m.start()]))
            pieces.append(("sym", m.group(1)))
            idx = m.end()
        if idx < len(seg):
            pieces.append(("lit", seg[idx:]))

        # Compose per-flow merged values.
        merged_vals: list[str] = []
        abort = False
        for f in range(n_flows):
            buf: list[str] = []
            for kind, val in pieces:
                if kind == "lit":
                    buf.append(val)
                else:
                    h = sym_to_hole.get(f"s{val}")
                    if h is None:
                        abort = True
                        break
                    buf.append(h[f])
            if abort:
                break
            merged_vals.append("".join(buf))
        if abort:
            break

        merged_hole = tuple(merged_vals)
        # Reuse the first involved symbol's name as the survivor.
        survivor_num = sym_nums[0]
        survivor_name = f"s{survivor_num}"

        # Remove all involved symbols from the map.
        for n in set(sym_nums):
            sn = f"s{n}"
            h = sym_to_hole.get(sn)
            if h is not None and symbol_map.get(h) == sn:
                del symbol_map[h]
            if sn in sym_to_hole:
                del sym_to_hole[sn]

        # Install the merged symbol (skip if a collision exists for this
        # hole; in that case map the survivor name to the existing one).
        if merged_hole in symbol_map:
            survivor_name = symbol_map[merged_hole]
        else:
            symbol_map[merged_hole] = survivor_name
            sym_to_hole[survivor_name] = merged_hole

        # Replace every occurrence of the segment with the survivor symbol.
        text = text.replace(seg, f"\\{survivor_name}\\")

        print(f"Merged underscore segment : _{seg}_ -> _\\{survivor_name}\\_  "
              f"({cnt} occurrences, values now {merged_hole})")
        total += 1

    if total == 0:
        return
    tmp_out = mtpl_path.with_suffix(mtpl_path.suffix + ".tmp")
    tmp_out.write_text(text, encoding="utf-8", newline="")
    if mtpl_path.exists():
        mtpl_path.unlink()
    tmp_out.replace(mtpl_path)
    print(f"Underscore-segment merges : {total}")


def _symbolized_to_mtpl(template: str) -> str:
    """Convert the v3 `<sK>` placeholders to the chosen `\\sK\\` syntax."""
    return re.sub(r"<(s\d+)>", lambda m: _format_sym(m.group(1)), template)


_CSV_SYM_TOKEN_RE = re.compile(r"<s(\d+)>")
_CSV_UNDERSCORE_SEG_RE = re.compile(r"(?<=_)[^_\r\n]+(?=_)")


def _merge_symbols_in_compare_csv(csv_path: Path, flows: list[str]) -> None:
    """Post-process the per-flow comparison CSV, applying the underscore-
    segment merge rule to the `Symbolized` column (and updating each
    `<flow>_symbols` column accordingly).

    Rule (mirror of `_merge_underscore_segments` for the .mtpl side):
      In the `Symbolized` column, for any underscore-bounded segment
      containing >= 2 distinct `<sN>` tokens, if EVERY occurrence of each
      involved symbol across the whole CSV column appears inside that
      same segment-template, collapse them into a single new symbol
      whose per-flow values are the literal concatenation.
    """
    if not csv_path.exists():
        return
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    if "Symbolized" not in fieldnames:
        return
    symbol_cols = [f"{fn}_symbols" for fn in flows
                   if f"{fn}_symbols" in fieldnames]

    # Build per-symbol per-flow value maps from the *_symbols columns.
    # Format example: "s0=1; s9=1; s10="
    per_flow_values: dict[str, dict[str, str]] = {fn: {} for fn in flows}
    for row in rows:
        for fn in flows:
            col = f"{fn}_symbols"
            blob = (row.get(col) or "").strip()
            if not blob:
                continue
            for piece in blob.split(";"):
                piece = piece.strip()
                if not piece or "=" not in piece:
                    continue
                k, _, v = piece.partition("=")
                k = k.strip()
                # Normalize: regex captures emit the bare digit (e.g. "9"
                # for `<s9>`), but the CSV cells use "s9=...". Store under
                # the bare-digit form to match _CSV_SYM_TOKEN_RE groups.
                if k.startswith("s") and k[1:].isdigit():
                    k = k[1:]
                # Only update if not already set (rows agree by construction).
                per_flow_values[fn].setdefault(k, v)

    total = 0
    while True:
        # Count occurrences of each symbol token across all Symbolized cells.
        sym_total: dict[str, int] = {}
        for row in rows:
            s = row.get("Symbolized") or ""
            for m in _CSV_SYM_TOKEN_RE.finditer(s):
                n = m.group(1)
                sym_total[n] = sym_total.get(n, 0) + 1

        # Collect candidate underscore-segment templates with >= 2 symbols.
        seg_total: dict[str, int] = {}
        for row in rows:
            s = row.get("Symbolized") or ""
            for m in _CSV_UNDERSCORE_SEG_RE.finditer(s):
                seg = m.group(0)
                if len(_CSV_SYM_TOKEN_RE.findall(seg)) < 2:
                    continue
                seg_total[seg] = seg_total.get(seg, 0) + 1

        chosen_seg: str | None = None
        for seg, cnt in seg_total.items():
            sym_nums = _CSV_SYM_TOKEN_RE.findall(seg)
            seen: dict[str, int] = {}
            for n in sym_nums:
                seen[n] = seen.get(n, 0) + 1
            ok = True
            for n, expected_per in seen.items():
                if sym_total.get(n, 0) != cnt * expected_per:
                    ok = False
                    break
            if ok:
                chosen_seg = seg
                break

        if chosen_seg is None:
            break

        # Decompose chosen_seg into ordered (lit | sym) pieces.
        pieces: list[tuple[str, str]] = []
        idx = 0
        for m in _CSV_SYM_TOKEN_RE.finditer(chosen_seg):
            if m.start() > idx:
                pieces.append(("lit", chosen_seg[idx:m.start()]))
            pieces.append(("sym", m.group(1)))
            idx = m.end()
        if idx < len(chosen_seg):
            pieces.append(("lit", chosen_seg[idx:]))
        sym_nums = [n for k, n in pieces if k == "sym"]
        survivor = sym_nums[0]

        # Compute per-flow merged values.
        merged: dict[str, str] = {}
        for fn in flows:
            buf = []
            for k, v in pieces:
                if k == "lit":
                    buf.append(v)
                else:
                    buf.append(per_flow_values[fn].get(v, ""))
            merged[fn] = "".join(buf)

        # Rewrite all rows: replace segment in Symbolized with `<sSURVIVOR>`,
        # remove the merged-out symbols from per-flow symbols cells, and
        # update the survivor's value to the merged literal+symbol concat.
        replacement = f"<s{survivor}>"
        kill = set(sym_nums) - {survivor}
        for row in rows:
            s = row.get("Symbolized") or ""
            if chosen_seg in s:
                row["Symbolized"] = s.replace(chosen_seg, replacement)
            for fn in flows:
                col = f"{fn}_symbols"
                if col not in row:
                    continue
                blob = (row.get(col) or "").strip()
                if not blob:
                    continue
                pieces_out: list[str] = []
                for piece in blob.split(";"):
                    piece = piece.strip()
                    if not piece or "=" not in piece:
                        continue
                    k, _, v = piece.partition("=")
                    k = k.strip()
                    # Normalize key: "s9" -> "9" for comparisons.
                    k_bare = k[1:] if k.startswith("s") and k[1:].isdigit() else k
                    if k_bare in kill:
                        continue
                    if k_bare == survivor:
                        pieces_out.append(f"s{survivor}={merged[fn]}")
                    else:
                        pieces_out.append(f"{k}={v}")
                row[col] = "; ".join(pieces_out)

        # Update per_flow_values map for the next iteration.
        for fn in flows:
            for n in kill:
                per_flow_values[fn].pop(n, None)
            per_flow_values[fn][survivor] = merged[fn]

        print(f"CSV merged segment        : _{chosen_seg}_ -> _<s{survivor}>_  "
              f"(killed: {sorted(kill)}, merged values: "
              f"{[merged[fn] for fn in flows]})")
        total += 1

    if total == 0:
        return
    # Rewrite the CSV.
    tmp_out = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with tmp_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    if csv_path.exists():
        csv_path.unlink()
    tmp_out.replace(csv_path)
    print(f"CSV underscore-segment merges: {total}")


def _merge_adjacent_symbols_in_compare_csv(csv_path: Path,
                                            flows: list[str]) -> None:
    """Compare-CSV mirror of `_merge_adjacent_symbols`. Collapse always-
    adjacent pairs `<sN><sM>` (no chars between) when adjacency holds for
    EVERY occurrence of both symbols across the `Symbolized` column.
    Per-flow merged values become the literal concatenation. Iterates."""
    if not csv_path.exists():
        return
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    if "Symbolized" not in fieldnames:
        return

    # Build per-flow value maps (same shape as in underscore version).
    per_flow_values: dict[str, dict[str, str]] = {fn: {} for fn in flows}
    for row in rows:
        for fn in flows:
            blob = (row.get(f"{fn}_symbols") or "").strip()
            if not blob:
                continue
            for piece in blob.split(";"):
                piece = piece.strip()
                if not piece or "=" not in piece:
                    continue
                k, _, v = piece.partition("=")
                k = k.strip()
                if k.startswith("s") and k[1:].isdigit():
                    k = k[1:]
                per_flow_values[fn].setdefault(k, v)

    adj_re = re.compile(r"<s(\d+)><s(\d+)>")
    total = 0
    while True:
        sym_total: dict[str, int] = {}
        for row in rows:
            s = row.get("Symbolized") or ""
            for m in _CSV_SYM_TOKEN_RE.finditer(s):
                n = m.group(1)
                sym_total[n] = sym_total.get(n, 0) + 1

        adj_pairs: dict[tuple[str, str], int] = {}
        for row in rows:
            s = row.get("Symbolized") or ""
            for m in adj_re.finditer(s):
                a, b = m.group(1), m.group(2)
                if a == b:
                    continue
                adj_pairs[(a, b)] = adj_pairs.get((a, b), 0) + 1

        merge: tuple[str, str] | None = None
        for (a, b), c in adj_pairs.items():
            if c == sym_total.get(a, 0) and c == sym_total.get(b, 0):
                merge = (a, b)
                break

        if merge is None:
            break

        a, b = merge
        merged: dict[str, str] = {}
        for fn in flows:
            merged[fn] = (per_flow_values[fn].get(a, "")
                          + per_flow_values[fn].get(b, ""))

        # Survivor = a; kill = b.
        survivor, kill = a, b
        replacement = f"<s{survivor}>"
        for row in rows:
            s = row.get("Symbolized") or ""
            if f"<s{a}><s{b}>" in s:
                row["Symbolized"] = s.replace(f"<s{a}><s{b}>", replacement)
            for fn in flows:
                col = f"{fn}_symbols"
                if col not in row:
                    continue
                blob = (row.get(col) or "").strip()
                if not blob:
                    continue
                pieces_out: list[str] = []
                for piece in blob.split(";"):
                    piece = piece.strip()
                    if not piece or "=" not in piece:
                        continue
                    k, _, v = piece.partition("=")
                    k = k.strip()
                    k_bare = (k[1:] if k.startswith("s") and k[1:].isdigit()
                              else k)
                    if k_bare == kill:
                        continue
                    if k_bare == survivor:
                        pieces_out.append(f"s{survivor}={merged[fn]}")
                    else:
                        pieces_out.append(f"{k}={v}")
                row[col] = "; ".join(pieces_out)

        for fn in flows:
            per_flow_values[fn].pop(kill, None)
            per_flow_values[fn][survivor] = merged[fn]

        print(f"CSV merged adjacent       : <s{a}><s{b}> -> <s{survivor}>  "
              f"(merged values: {[merged[fn] for fn in flows]})")
        total += 1

    if total == 0:
        return
    tmp_out = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with tmp_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    if csv_path.exists():
        csv_path.unlink()
    tmp_out.replace(csv_path)
    print(f"CSV adjacent-symbol merges: {total}")


def _merge_dot_separated_symbols_in_compare_csv(csv_path: Path,
                                                 flows: list[str]) -> None:
    """Compare-CSV merge: collapse `<sA>.<sB>` pairs when EVERY occurrence
    of both symbols across the `Symbolized` column is part of that exact
    `<sA>.<sB>` pattern. Per-flow merged values become `valA.valB`.
    Example: s15=2; s16=8  =>  s15=2.8 (kills s16). Iterates."""
    if not csv_path.exists():
        return
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    if "Symbolized" not in fieldnames:
        return

    per_flow_values: dict[str, dict[str, str]] = {fn: {} for fn in flows}
    for row in rows:
        for fn in flows:
            blob = (row.get(f"{fn}_symbols") or "").strip()
            if not blob:
                continue
            for piece in blob.split(";"):
                piece = piece.strip()
                if not piece or "=" not in piece:
                    continue
                k, _, v = piece.partition("=")
                k = k.strip()
                if k.startswith("s") and k[1:].isdigit():
                    k = k[1:]
                per_flow_values[fn].setdefault(k, v)

    dot_re = re.compile(r"<s(\d+)>\.<s(\d+)>")
    total = 0
    while True:
        sym_total: dict[str, int] = {}
        for row in rows:
            s = row.get("Symbolized") or ""
            for m in _CSV_SYM_TOKEN_RE.finditer(s):
                n = m.group(1)
                sym_total[n] = sym_total.get(n, 0) + 1

        dot_pairs: dict[tuple[str, str], int] = {}
        for row in rows:
            s = row.get("Symbolized") or ""
            for m in dot_re.finditer(s):
                a, b = m.group(1), m.group(2)
                if a == b:
                    continue
                dot_pairs[(a, b)] = dot_pairs.get((a, b), 0) + 1

        merge: tuple[str, str] | None = None
        for (a, b), c in dot_pairs.items():
            if c == sym_total.get(a, 0) and c == sym_total.get(b, 0):
                merge = (a, b)
                break

        if merge is None:
            break

        a, b = merge
        merged: dict[str, str] = {}
        for fn in flows:
            merged[fn] = (per_flow_values[fn].get(a, "")
                          + "." + per_flow_values[fn].get(b, ""))

        survivor, kill = a, b
        replacement = f"<s{survivor}>"
        for row in rows:
            s = row.get("Symbolized") or ""
            if f"<s{a}>.<s{b}>" in s:
                row["Symbolized"] = s.replace(f"<s{a}>.<s{b}>", replacement)
            for fn in flows:
                col = f"{fn}_symbols"
                if col not in row:
                    continue
                blob = (row.get(col) or "").strip()
                if not blob:
                    continue
                pieces_out: list[str] = []
                for piece in blob.split(";"):
                    piece = piece.strip()
                    if not piece or "=" not in piece:
                        continue
                    k, _, v = piece.partition("=")
                    k = k.strip()
                    k_bare = (k[1:] if k.startswith("s") and k[1:].isdigit()
                              else k)
                    if k_bare == kill:
                        continue
                    if k_bare == survivor:
                        pieces_out.append(f"s{survivor}={merged[fn]}")
                    else:
                        pieces_out.append(f"{k}={v}")
                row[col] = "; ".join(pieces_out)

        for fn in flows:
            per_flow_values[fn].pop(kill, None)
            per_flow_values[fn][survivor] = merged[fn]

        print(f"CSV merged dot-separated  : <s{a}>.<s{b}> -> <s{survivor}>  "
              f"(merged values: {[merged[fn] for fn in flows]})")
        total += 1

    if total == 0:
        return
    tmp_out = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with tmp_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    if csv_path.exists():
        csv_path.unlink()
    tmp_out.replace(csv_path)
    print(f"CSV dot-separated merges  : {total}")


def _load_symbols_from_compare_csv(
        csv_path: Path, flows: list[str]
) -> tuple[dict[tuple, str], dict[str, dict]]:
    """Read the per-flow comparison CSV (the SOLE source of truth for
    symbols, post-merge). Returns:
      * symbol_map  : { (per_flow_value_tuple) -> 'sN' } in v3.FLOWS order
      * csv_rows    : { Entity -> row_dict }  for downstream lookups
    """
    symbol_map: dict[tuple, str] = {}
    csv_rows: dict[str, dict] = {}
    if not csv_path.exists():
        return symbol_map, csv_rows

    sym_to_hole: dict[str, list[str]] = {}
    n_flows = len(flows)
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ent = row.get("Entity", "")
            csv_rows[ent] = row
            for fi, fn in enumerate(flows):
                blob = (row.get(f"{fn}_symbols") or "").strip()
                if not blob:
                    continue
                for piece in blob.split(";"):
                    piece = piece.strip()
                    if not piece or "=" not in piece:
                        continue
                    k, _, v = piece.partition("=")
                    k = k.strip()
                    if k.startswith("s") and k[1:].isdigit():
                        k = k[1:]
                    arr = sym_to_hole.setdefault(k, [""] * n_flows)
                    if not arr[fi]:
                        arr[fi] = v
    for sym_num, vals in sym_to_hole.items():
        symbol_map[tuple(vals)] = f"s{sym_num}"
    return symbol_map, csv_rows


def _verify_symbols_consistency(mtpl_path: Path, symbols_csv_path: Path,
                                 compare_csv_path: Path,
                                 flows: list[str]) -> int:
    """Final sanity: every `\\sN\\` token in the collapsed .mtpl must have a
    matching row in the symbols CSV, and the symbols CSV must agree with
    the compare CSV's symbol cells. CYCLE-AWARE: uses the union of flow
    columns present in each file. Returns 0 on PASS, 1 on FAIL."""
    text = mtpl_path.read_text(encoding="utf-8", errors="replace")
    mtpl_syms = set(re.findall(r"\\s(\d+)\\", text))

    csv_syms: dict[str, dict[str, str]] = {}
    sym_cols: list[str] = []
    with symbols_csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        sym_cols = [c for c in (reader.fieldnames or []) if c != "Symbol"]
        for row in reader:
            m = re.match(r"\\s(\d+)\\", row.get("Symbol", ""))
            if m:
                csv_syms[m.group(1)] = {c: row.get(c, "") for c in sym_cols}

    cmp_syms: dict[str, dict[str, str]] = {}
    cmp_cols: list[str] = list(flows)
    if compare_csv_path.exists():
        with compare_csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fns = list(reader.fieldnames or [])
            if "Entity" in fns and "DIFF" in fns:
                cmp_cols = fns[fns.index("Entity")+1:fns.index("DIFF")]
        cmp_map, _ = _load_symbols_from_compare_csv(
            compare_csv_path, cmp_cols)
        for hole, sym in cmp_map.items():
            n = sym[1:]
            cmp_syms[n] = {c: hole[i] for i, c in enumerate(cmp_cols)}

    print()
    print("-" * 60)
    print("Symbol-consistency verification")
    print("-" * 60)

    fail = 0

    missing_in_csv = mtpl_syms - set(csv_syms.keys())
    if missing_in_csv:
        fail += len(missing_in_csv)
        print(f"  FAIL: {len(missing_in_csv)} \\sN\\ token(s) in {mtpl_path.name}"
              f" missing from {symbols_csv_path.name}: "
              f"{sorted(missing_in_csv, key=int)[:10]}")
    else:
        print(f"  PASS: all {len(mtpl_syms)} \\sN\\ token(s) in mtpl have "
              f"symbol-table rows.")

    orphans = set(csv_syms.keys()) - mtpl_syms
    if orphans:
        fail += len(orphans)
        print(f"  FAIL: {len(orphans)} unused symbol(s) in "
              f"{symbols_csv_path.name} (not referenced in mtpl): "
              f"{sorted(orphans, key=int)[:10]}")

    if cmp_syms:
        # Compare per-flow values for flows present in BOTH CSVs.
        common_cols = [c for c in sym_cols if c in cmp_cols]
        mismatches = []
        for n, vals in csv_syms.items():
            ref = cmp_syms.get(n)
            if ref is None:
                mismatches.append((n, vals, None))
                continue
            for c in common_cols:
                if vals.get(c, "") != ref.get(c, ""):
                    mismatches.append((n, {c: vals.get(c, "")},
                                       {c: ref.get(c, "")}))
                    break
        if mismatches:
            fail += len(mismatches)
            print(f"  FAIL: {len(mismatches)} symbol(s) differ between "
                  f"{symbols_csv_path.name} and {compare_csv_path.name}:")
            for n, v, r in mismatches[:5]:
                print(f"    \\s{n}\\  symbols={v}  compare={r}")
        else:
            print(f"  PASS: symbols.csv is 1:1 with compare CSV "
                  f"({len(csv_syms)} symbols).")

    if fail:
        print(f"Symbol-consistency: FAILED ({fail} issue(s))")
        return 1
    print("Symbol-consistency: PASSED")
    return 0


def _replace_param_value(line: str, param_name: str, new_value: str) -> str:
    """Rewrite the param line, preserving indent, quoting style, and trailing
    suffix after `;` (comments). Returns the modified line."""
    rgx = re.compile(rf"^(\s*){re.escape(param_name)}\s*=\s*(.*?);(.*)$")
    m = rgx.match(line)
    if not m:
        return line
    indent, original_value, tail = m.group(1), m.group(2).strip(), m.group(3)
    # If the original value was quoted (starts AND ends with `"`), re-wrap
    # the new value in `"..."`. Do NOT escape interior `"` -- in MTPL,
    # values like `"foo:"+__shared__::X+"bar"` are quoted-string-concat
    # expressions where the interior `"` chars are structural (open/close
    # of each fragment), not embedded data needing escape. Since
    # parse_params strips ONE pair of outer quotes for any
    # `"..."`-bounded value, the new_value passed in already has the
    # correct interior structure -- we just put one pair back on.
    quoted = (original_value.startswith('"') and original_value.endswith('"')
              and len(original_value) >= 2)
    if quoted:
        new_text = '"' + new_value + '"'
    else:
        new_text = new_value
    return f"{indent}{param_name} = {new_text};{tail}"


# ---------------------------------------------------------------------------
# Pre-work (Step 0): normalize BaseNumbers + BypassPort on relevant tests.
# ---------------------------------------------------------------------------

# Default BypassPort (per the user's contract: always -1).
_PREWORK_BYPASSPORT_DEFAULT = "-1"

# Per-test-instance regexes (any *Test keyword, same shape as _RE_TEST_DEF
# but evaluated lazily here to avoid forward-reference at import time).
_PREWORK_TEST_RE = re.compile(
    r"^\s*(?!TestPlan\b|TestProgram\b)"
    r"(?P<kind>[A-Za-z_][A-Za-z_0-9]*Test)\s+"
    r"(?:\S+\s+(?P<n2>\S+)|(?P<n1>\S+))\s*$"
)
_PREWORK_BASE_RE = re.compile(r"^(\s*)BaseNumbers\s*=\s*([^;]+);(.*)$")
_PREWORK_BYPASS_RE = re.compile(r"^(\s*)BypassPort\s*=\s*[^;]+;(.*)$")


def _prework_collect_targets() -> set[str]:
    """Return the set of test instance names that are reachable under the
    input flows according to the skill CSV. Strips each per-flow prefix from
    `compare_flows_v3.FLOW_DEFS` so the result matches the bare CSharpTest
    instance names defined in the mtpl."""
    out: set[str] = set()
    if not v3.SKILL_CSV.exists():
        return out
    prefixes = tuple(v3.FLOW_DEFS.values())
    with v3.SKILL_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n = row.get("Test Instance Name") or ""
            for p in prefixes:
                if n.startswith(p):
                    out.add(n[len(p):])
                    break
    return out


def _apply_prework(lines: list[str]) -> None:
    """Mutate `lines` in place:
      - On every test instance whose name is in the relevant-tests set,
        replace `BaseNumbers = <X>;` with `BaseNumbers = <DEFAULT>;` where
        DEFAULT is the most frequent existing value across those tests
        (falls back to `\"12522\"` if no values are present).
      - Replace `BypassPort = <X>;` with `BypassPort = -1;` on the same
        tests.
    Idempotent: if values are already at the chosen defaults, nothing
    changes (and counts are reported as 0)."""
    targets = _prework_collect_targets()
    if not targets:
        print("Pre-work: no relevant tests found in skill CSV - skipped")
        return

    # Pass 1: locate every target-test block and collect existing
    # BaseNumbers values for majority vote.
    blocks: list[tuple[int, int]] = []  # (block_start_line_idx, block_end)
    base_values: list[str] = []
    i = 0
    while i < len(lines):
        m = _PREWORK_TEST_RE.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group("n2") or m.group("n1")
        j = i
        while j < len(lines) and "{" not in lines[j]:
            j += 1
        end = v3.find_block_end(lines, j)
        if name in targets:
            blocks.append((j + 1, end))
            for k in range(j + 1, end):
                ln = lines[k]
                if ln.lstrip().startswith("#"):
                    continue
                bm = _PREWORK_BASE_RE.match(ln)
                if bm:
                    base_values.append(bm.group(2).strip())
        i = end + 1

    if not blocks:
        print("Pre-work: no target test blocks found in input - skipped")
        return

    # Choose default BaseNumbers by majority vote (ties broken by first
    # occurrence). Fall back to "12522" if no values were present.
    default_basenum = '"12522"'
    if base_values:
        counts: dict[str, int] = {}
        for v in base_values:
            counts[v] = counts.get(v, 0) + 1
        # pick most frequent; ties -> first encountered
        best, best_count = base_values[0], counts[base_values[0]]
        for v in base_values:
            if counts[v] > best_count:
                best, best_count = v, counts[v]
        default_basenum = best
    print(f"Pre-work: targets={len(targets)}  test-blocks-matched={len(blocks)}  "
          f"BaseNumbers default='{default_basenum}' (chosen from "
          f"{len(set(base_values))} distinct value(s))")

    # Pass 2: rewrite BaseNumbers + BypassPort on each target block.
    bn = bp = tests_modified = 0
    for j_start, end in blocks:
        modified = False
        for k in range(j_start, end):
            ln = lines[k]
            if ln.lstrip().startswith("#"):
                continue
            bm = _PREWORK_BASE_RE.match(ln)
            if bm:
                new = f"{bm.group(1)}BaseNumbers = {default_basenum};{bm.group(3)}"
                if new != ln:
                    lines[k] = new
                    bn += 1
                    modified = True
                continue
            bpm = _PREWORK_BYPASS_RE.match(ln)
            if bpm:
                new = (f"{bpm.group(1)}BypassPort = "
                       f"{_PREWORK_BYPASSPORT_DEFAULT};{bpm.group(2)}")
                if new != ln:
                    lines[k] = new
                    bp += 1
                    modified = True
        if modified:
            tests_modified += 1
    print(f"Pre-work: tests modified={tests_modified}  "
          f"BaseNumbers updates={bn}  BypassPort updates={bp}")


def _detect_previous_cycle() -> tuple[int, list[str], list[dict], list[str]]:
    """Inspect the on-disk artifacts to detect whether a previous cycle
    has run. Returns (max_sym_num, prev_flows, prev_symbols_rows,
    prev_symbols_fieldnames). When no previous cycle is present, returns
    (-1, [], [], [])."""
    if not OUT_SYMBOLS.exists():
        return -1, [], [], []
    with OUT_SYMBOLS.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not fieldnames or fieldnames[0] != "Symbol":
        return -1, [], [], []
    prev_flows = [c for c in fieldnames if c != "Symbol"]
    max_n = -1
    for row in rows:
        m = re.match(r"\\s(\d+)\\", row.get("Symbol", ""))
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return max_n, prev_flows, rows, fieldnames


def _merge_compare_csv_across_cycles(
        new_csv_path: Path, prev_csv_path: Path,
        cur_flows: list[str], prev_flows: list[str]) -> None:
    """Merge the cycle-N compare CSV with the cycle-(N-1) compare CSV in
    place at `new_csv_path`. Result has:
      * column union (all flows from both cycles, preserved order: prev
        flows first, then any current-only flows)
      * row union by Entity (cycle-N rows take precedence for shared
        entities; cycle-prev rows fill in OLD-flow columns and add
        unique entities)
    """
    if not prev_csv_path.exists():
        return  # cycle 1 -> nothing to merge

    with prev_csv_path.open("r", encoding="utf-8", newline="") as f:
        prev_reader = csv.DictReader(f)
        prev_rows = list(prev_reader)
        prev_fieldnames = list(prev_reader.fieldnames or [])

    with new_csv_path.open("r", encoding="utf-8", newline="") as f:
        new_reader = csv.DictReader(f)
        new_rows = list(new_reader)
        new_fieldnames = list(new_reader.fieldnames or [])

    # Build the merged column order. Schema: Entity, <all_flows>, DIFF,
    # <all_flow_lines>, Symbolized, <all_flow_symbols>.
    all_flows: list[str] = []
    for f in prev_flows + cur_flows:
        if f not in all_flows:
            all_flows.append(f)
    line_cols = [f"{fn}_line" for fn in all_flows]
    sym_cols = [f"{fn}_symbols" for fn in all_flows]
    out_fields = ["Entity", *all_flows, "DIFF", "Is_MTT", *line_cols, "Symbolized",
                  *sym_cols]

    # Index prev rows by Entity; merge with new rows (new wins on
    # conflict for shared columns).
    prev_by_ent: dict[str, dict] = {r.get("Entity", ""): r for r in prev_rows}

    merged: list[dict] = []
    seen: set[str] = set()
    for nr in new_rows:
        ent = nr.get("Entity", "")
        seen.add(ent)
        out: dict = {c: "" for c in out_fields}
        out["Entity"] = ent
        # Carry forward prev values for OLD flow columns.
        pr = prev_by_ent.get(ent)
        if pr:
            for c in out_fields:
                if c in pr and pr.get(c, "") != "":
                    out[c] = pr[c]
        # Now overlay new-cycle values (cycle N takes precedence).
        for c in out_fields:
            if c in nr and nr.get(c, "") != "":
                out[c] = nr[c]
        merged.append(out)

    # Append prev-only entities (not present in cycle N).
    for pr in prev_rows:
        ent = pr.get("Entity", "")
        if ent in seen:
            continue
        out = {c: "" for c in out_fields}
        for c in out_fields:
            if c in pr:
                out[c] = pr[c]
        out["Entity"] = ent
        merged.append(out)

    tmp_out = new_csv_path.with_suffix(new_csv_path.suffix + ".tmp")
    with tmp_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        w.writerows(merged)
    if new_csv_path.exists():
        new_csv_path.unlink()
    tmp_out.replace(new_csv_path)
    print(f"Cycle-merge compare CSV   : "
          f"prev={len(prev_rows)}  cur={len(new_rows)}  "
          f"merged={len(merged)}  cols={len(out_fields)}")


def phase_compare() -> tuple[list[str], str]:
    """PHASE 1 — COMPARE.

    Reads the input .mtpl, applies pre-work (BaseNumbers majority +
    BypassPort=-1), and produces the per-flow comparison CSV
    (`<module>_bp.flows_compare.csv`). The CSV is then post-processed by
    the merge rules (underscore-bounded, adjacent, dot-separated) so that
    it is the SOLE source of truth for symbol numbering downstream.

    Returns the pre-worked source lines + their newline flavour, so the
    next phase can reuse them without re-reading.
    """
    print()
    print("=" * 60)
    print("PHASE 1 / 3  —  COMPARE")
    print("=" * 60)

    # CYCLE-AWARE detection: if `_bp.mtpl_symbols.csv` already exists, this
    # is cycle N (N >= 2). Seed v3's symbol-numbering floor so new symbols
    # get numbers > max(existing). Backup the previous compare CSV so we
    # can merge it back in after this cycle's CSV is generated+merged.
    max_n, prev_flows, prev_sym_rows, _prev_sym_fields = \
        _detect_previous_cycle()
    if max_n >= 0:
        v3.PRESEED_MAX_SYMBOL = max_n
        # Build a hole-tuple -> sN map projected onto the CURRENT FLOWS
        # order. When current FLOWS overlap with prev_flows, identical
        # tuples will REUSE the existing sN name. Tuples with empty cells
        # (current FLOWS that weren't in prev) are skipped to avoid false
        # matches.
        preseed: dict[tuple, str] = {}
        for row in prev_sym_rows:
            m = re.match(r"\\s(\d+)\\", row.get("Symbol", ""))
            if not m:
                continue
            sym = f"s{m.group(1)}"
            try:
                hole = tuple(row[fn] for fn in v3.FLOWS)
            except KeyError:
                continue  # current FLOWS not all present in prev symbols.csv
            if all(v == "" for v in hole):
                continue
            preseed[hole] = sym
        v3.PRESEED_SYMBOL_MAP = preseed
        print(f"Cycle-aware: previous symbols.csv found "
              f"(max=\\s{max_n}\\, prev_flows={prev_flows}, "
              f"reuse-seeds={len(preseed)})")
    else:
        v3.PRESEED_MAX_SYMBOL = -1
        v3.PRESEED_SYMBOL_MAP = {}
        print("Cycle 1: no previous artifacts found")

    prev_compare_backup: Path | None = None
    if v3.OUT_CSV.exists() and max_n >= 0:
        prev_compare_backup = v3.OUT_CSV.with_suffix(
            v3.OUT_CSV.suffix + ".prev_cycle.bak")
        if prev_compare_backup.exists():
            prev_compare_backup.unlink()
        v3.OUT_CSV.replace(prev_compare_backup)
        print(f"Backed up previous compare CSV -> "
              f"{prev_compare_backup.name}")

    primary_text = v3.MTPL_PRIMARY.read_text(encoding="utf-8", errors="replace")
    nl = "\r\n" if "\r\n" in primary_text[:4096] else "\n"
    lines = primary_text.split(nl)

    # 1a. Pre-work: normalize BaseNumbers + BypassPort on every test
    # instance reachable under the input flows. MUST run BEFORE the
    # comparison CSV so the diff doesn't flag BaseNumbers/BypassPort as
    # per-flow differences (they get unified to one value across all
    # input flows here).
    _apply_prework(lines)

    # 1b. Generate the per-flow comparison CSV AFTER pre-work
    # normalization. We can't overwrite the input on disk (it may be
    # `.mtpl_orig` which is sacred), so we materialize the pre-worked
    # content to a stable temp file in the module dir and point v3 at it
    # for the duration of v3.main().
    prework_tmp = OUT_MTPL.with_suffix(OUT_MTPL.suffix + ".prework.tmp")
    prework_tmp.write_text(nl.join(lines), encoding="utf-8", newline="")
    print("\n[v3] generating per-flow comparison CSV ...")
    _orig_primary = v3.MTPL_PRIMARY
    v3.MTPL_PRIMARY = prework_tmp
    try:
        v3.main()
    finally:
        v3.MTPL_PRIMARY = _orig_primary
        if prework_tmp.exists():
            prework_tmp.unlink()
    print(f"Wrote {v3.OUT_CSV}")

    # 1c. Apply merge rules to the comparison CSV (single source of truth).
    #   - underscore-bounded: collapse `_<sA>lit<sB>_` style runs
    #   - adjacent          : collapse `<sA><sB>` (no chars between)
    #   - dot-separated     : collapse `<sA>.<sB>` (e.g. 2 + 8 -> 2.8)
    _merge_symbols_in_compare_csv(v3.OUT_CSV, list(v3.FLOWS))
    _merge_adjacent_symbols_in_compare_csv(v3.OUT_CSV, list(v3.FLOWS))
    _merge_dot_separated_symbols_in_compare_csv(v3.OUT_CSV, list(v3.FLOWS))
    # One more underscore pass in case any merge unlocked new candidates.
    _merge_symbols_in_compare_csv(v3.OUT_CSV, list(v3.FLOWS))

    # 1d. Cycle-merge: union the cycle-N compare CSV with the cycle-(N-1)
    # backup, so old entities + old flow columns are preserved.
    if prev_compare_backup is not None:
        _merge_compare_csv_across_cycles(
            v3.OUT_CSV, prev_compare_backup,
            list(v3.FLOWS), prev_flows)
        prev_compare_backup.unlink()

    return lines, nl


def phase_generate(lines: list[str], nl: str) -> dict[tuple, str]:
    """PHASE 2 — GENERATE.

    Consumes the (now-merged) comparison CSV and produces:
      * `<module>_bp.mtpl`            — collapsed BluePrint with `\\sN\\` tokens
      * `<module>_bp.mtpl_symbols.csv` — 1:1 transposition of CSV symbol cells

    Returns the global symbol map used by downstream validation.
    """
    print()
    print("=" * 60)
    print("PHASE 2 / 3  —  GENERATE")
    print("=" * 60)

    # 2a. Locate flow blocks
    flow_blocks: dict[str, tuple[int, int]] = {}
    for fn in ALL_FLOWS:
        blk = _find_flow_block(lines, fn)
        if blk is None:
            print(f"WARN: flow {fn} not found in {v3.MTPL_PRIMARY.name}")
            continue
        flow_blocks[fn] = blk

    if KEEP_FLOW not in flow_blocks:
        print(f"ERROR: kept flow {KEEP_FLOW} not found", file=sys.stderr)
        raise SystemExit(2)

    keep_block = flow_blocks[KEEP_FLOW]
    remove_blocks = [flow_blocks[fn] for fn in REMOVE_FLOWS if fn in flow_blocks]

    # 2b. Scan refs inside each flow block
    keep_tests, keep_counters = _scan_flow_refs(lines, *keep_block)
    removed_tests, removed_counters = set(), set()
    for blk in remove_blocks:
        t, c = _scan_flow_refs(lines, *blk)
        removed_tests |= t
        removed_counters |= c

    # 2c. References anywhere outside the 3 flow blocks
    outside_tests, outside_counters = _scan_outside_refs(
        lines, [keep_block, *remove_blocks]
    )

    candidate_tests = removed_tests - keep_tests - outside_tests
    candidate_counters = removed_counters - keep_counters - outside_counters
    print(f"Removed-flow-only test refs : {len(removed_tests)}")
    print(f"Removable CSharpTest defs   : {len(candidate_tests)}")
    print(f"Removed-flow-only counters  : {len(removed_counters)}")
    print(f"Removable counters          : {len(candidate_counters)}")

    # 2d. Load the symbol map FROM the comparison CSV (single source of
    # truth, post-merge). The CSV is built by compare_flows_v3 from
    # TRACE_API-parsed parameter rows; symbolize_mtpl no longer invents
    # its own numbering -- it CONSUMES the CSV's `<sN>` tokens directly.
    print("\n[csv] loading symbol map from comparison CSV ...")
    global_symbol_map, csv_rows = _load_symbols_from_compare_csv(
        v3.OUT_CSV, list(v3.FLOWS))
    print(f"Symbols loaded from CSV   : {len(global_symbol_map)}")

    # We still need the per-flow MTPL parses for line numbers and to
    # discover which kept-flow (instance, param) pairs need rewriting.
    mtpl_per_flow = {fn: v3.parse_flow_body(lines, fn) for fn in v3.FLOWS}
    skill_per_flow = v3.load_skill_csv()

    # parse param line numbers from all source mtpls
    param_lines: dict[str, dict[str, int]] = {}
    for src in v3.MTPL_TEST_SOURCES:
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        src_nl = "\r\n" if "\r\n" in text[:4096] else "\n"
        src_lines = text.split(src_nl)
        per_inst = v3.parse_test_param_lines(src_lines)
        for inst, params in per_inst.items():
            if inst not in param_lines:
                param_lines[inst] = {}
            for pname, ln in params.items():
                param_lines[inst].setdefault(pname, ln)

    per_flow_items: dict[str, list[dict]] = {}
    for fn in v3.FLOWS:
        mtpl_idx = {it["instance"]: it for it in mtpl_per_flow[fn]}
        merged = []
        for s in skill_per_flow[fn]:
            m = mtpl_idx.get(s["instance"])
            merged.append({
                "instance": s["instance"],
                "params": s["params"],
            })
        per_flow_items[fn] = merged

    per_flow_keys = {
        fn: [(v3.normalize(it["instance"]), it) for it in per_flow_items[fn]]
        for fn in v3.FLOWS
    }
    seen = set()
    ordered_keys: list[str] = []
    for fn in v3.FLOWS:
        for key, _ in per_flow_keys[fn]:
            if key not in seen:
                seen.add(key)
                ordered_keys.append(key)
    flow_index = {}
    for fn in v3.FLOWS:
        idx = {}
        for key, it in per_flow_keys[fn]:
            base = key
            n = 1
            while base in idx:
                n += 1
                base = f"{key}#{n}"
            idx[base] = it
        flow_index[fn] = idx

    # For each (kept-flow instance, param) pull the symbolized template
    # straight from the CSV row whose Entity is `<key>.param.<pname>`.
    sym_for_kept: dict[tuple[str, str], str] = {}
    inst_name_rewrite: dict[str, str] = {}

    keep_idx_position = v3.FLOWS.index(KEEP_FLOW)
    for key in ordered_keys:
        items = [flow_index[fn].get(key) for fn in v3.FLOWS]
        if items[keep_idx_position] is None:
            continue  # entity not present in kept flow
        kept_inst = items[keep_idx_position]["instance"]
        # union of param names across flows (mirror v3 ordering)
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
            row = csv_rows.get(f"{key}.param.{p}")
            if not row:
                continue
            tpl = (row.get("Symbolized") or "").strip()
            if tpl:
                sym_for_kept[(kept_inst, p)] = tpl

    print(f"Kept-flow params symbolized: {len(sym_for_kept)}")

    # 2e. Build instance-name rewrite map. Pull the symbolized form
    # straight from the CSV's identity row (Entity = `<key>`).
    mtpl_per_flow_keys = {
        fn: [(v3.normalize(it["instance"]), it) for it in mtpl_per_flow[fn]]
        for fn in v3.FLOWS
    }
    mtpl_seen: set[str] = set()
    mtpl_ordered: list[str] = []
    for fn in v3.FLOWS:
        for k, _ in mtpl_per_flow_keys[fn]:
            if k not in mtpl_seen:
                mtpl_seen.add(k); mtpl_ordered.append(k)
    mtpl_flow_index = {}
    for fn in v3.FLOWS:
        idx = {}
        for k, it in mtpl_per_flow_keys[fn]:
            b = k; n = 1
            while b in idx:
                n += 1; b = f"{k}#{n}"
            idx[b] = it
        mtpl_flow_index[fn] = idx
    keep_pos = v3.FLOWS.index(KEEP_FLOW)
    for key in mtpl_ordered:
        items = [mtpl_flow_index[fn].get(key) for fn in v3.FLOWS]
        if items[keep_pos] is None:
            continue
        kept_name = items[keep_pos]["instance"]
        row = csv_rows.get(key)
        if not row:
            continue
        tpl = (row.get("Symbolized") or "").strip()
        if not tpl:
            continue
        sym = _symbolized_to_mtpl(tpl)
        if sym != kept_name:
            inst_name_rewrite[kept_name] = sym
    print(f"Instance names symbolized  : {len(inst_name_rewrite)}")

    # 2f. Build new mtpl content
    # Mark line ranges to delete (Flow blocks of removed flows)
    delete = [False] * len(lines)
    for s, e in remove_blocks:
        for i in range(s, e + 1):
            delete[i] = True

    # Mark test-definition blocks to delete.
    test_def_re = _RE_TEST_DEF
    i = 0
    while i < len(lines):
        if delete[i]:
            i += 1
            continue
        m = test_def_re.match(lines[i])
        if not m:
            i += 1
            continue
        tname = m.group("n2") or m.group("n1")
        j = i
        while j < len(lines) and "{" not in lines[j]:
            j += 1
        end = v3.find_block_end(lines, j)
        if tname in candidate_tests:
            for k in range(i, end + 1):
                delete[k] = True
        i = end + 1

    # Mark counter lines inside the Counters {} block
    cnt_block = _find_counters_block(lines)
    if cnt_block:
        cs, ce = cnt_block
        cnt_line_re = re.compile(r"^\s*([A-Za-z_][A-Za-z_0-9]*)\s*,?\s*$")
        for k in range(cs + 1, ce):
            m = cnt_line_re.match(lines[k])
            if m and m.group(1) in candidate_counters:
                delete[k] = True

    # Apply param symbolization on kept lines (use param_lines map)
    rewritten = list(lines)
    rewrites = 0
    for (inst, pname), template in sym_for_kept.items():
        ln_no = param_lines.get(inst, {}).get(pname)
        if not ln_no:
            continue
        idx = ln_no - 1
        if idx >= len(rewritten) or delete[idx]:
            continue
        new_value = _symbolized_to_mtpl(template)
        new_line = _replace_param_value(rewritten[idx], pname, new_value)
        if new_line != rewritten[idx]:
            rewritten[idx] = new_line
            rewrites += 1
    print(f"Param lines rewritten     : {rewrites}")

    # Apply connectivity symbolization on kept Flow's `Result <code> { GoTo X; }`
    # / `Result <code> { Return n; }` lines. Mirrors the param rewrite: pulls
    # the Symbolized template from `csv_rows[<entity>.connectivity.R<code>]`
    # and rewrites the body line, anchoring `\sN\` tokens in the bp text.
    conn_rewrites = 0
    keep_s, keep_e = keep_block
    _result_re = re.compile(r"^\s*Result\s+(\S+)\s*$")
    _goto_re = re.compile(r"^(\s*)GoTo\s+([^;]+);(.*)$")
    _return_re = re.compile(r"^(\s*)Return\s+([^;]+);(.*)$")
    i = keep_s
    while i <= keep_e:
        m = v3.FLOWITEM_RE.match(rewritten[i])
        if not m:
            i += 1
            continue
        inst_name = m.group(2)
        # locate FlowItem body
        j = i
        while j <= keep_e and "{" not in rewritten[j]:
            j += 1
        if j > keep_e:
            i += 1
            continue
        fi_end = v3.find_block_end(rewritten, j)
        # Resolve the entity key for this FlowItem (normalize -> ordered_keys)
        norm_inst = v3.normalize(inst_name)
        # Walk Result blocks
        cur_code: str | None = None
        for kk in range(j + 1, min(fi_end, keep_e) + 1):
            rm = _result_re.match(rewritten[kk])
            if rm:
                cur_code = rm.group(1).strip()
                continue
            if cur_code is None:
                continue
            row = csv_rows.get(f"{norm_inst}.connectivity.R{cur_code}")
            if not row:
                # try with #N collision suffix not handled — skip
                cur_code = None
                continue
            tpl = (row.get("Symbolized") or "").strip()
            if not tpl:
                cur_code = None
                continue
            symbolic = _symbolized_to_mtpl(tpl)
            gm = _goto_re.match(rewritten[kk])
            if gm:
                # `GoTo X;`  -> the ENTIRE phrase (including the GoTo verb)
                # is encoded in the symbolized template, which already
                # ends with the literal text `;` removed by the splitter.
                # Reconstruct: indent + symbolic + ; + tail.
                indent, _tgt, tail = gm.group(1), gm.group(2), gm.group(3)
                new_line = f"{indent}{symbolic};{tail}"
                if new_line != rewritten[kk]:
                    rewritten[kk] = new_line
                    conn_rewrites += 1
                cur_code = None
                continue
            rrm = _return_re.match(rewritten[kk])
            if rrm:
                indent, _n, tail = rrm.group(1), rrm.group(2), rrm.group(3)
                new_line = f"{indent}{symbolic};{tail}"
                if new_line != rewritten[kk]:
                    rewritten[kk] = new_line
                    conn_rewrites += 1
                cur_code = None
                continue
        i = fi_end + 1
    print(f"Connectivity lines rewritten: {conn_rewrites}")

    # Rewrite the kept Flow header line so the flow name itself is
    # symbolized (e.g. `Flow ARR_ATOM_CXX_F\s0\XAT`).
    flow_row = csv_rows.get("<flow>")
    flow_template = (flow_row.get("Symbolized") or "").strip() if flow_row else ""
    if flow_template:
        flow_sym_name = _symbolized_to_mtpl(flow_template)
        keep_start = keep_block[0]
        if 0 <= keep_start < len(rewritten):
            old = rewritten[keep_start]
            new = re.sub(
                rf"(^\s*Flow\s+){re.escape(KEEP_FLOW)}(\s*(?:@\S+)?\s*)$",
                lambda m: f"{m.group(1)}{flow_sym_name}{m.group(2)}",
                old,
            )
            if new != old:
                rewritten[keep_start] = new
                print(f"Flow header symbolized    : {KEEP_FLOW} -> {flow_sym_name}")

    # Rewrite kept instance names (CSharpTest defs, FlowItem refs, GoTo
    # targets, and counter names that embed them) using a global literal
    # substring replace. Sort by descending length to avoid a shorter
    # name being a prefix of a longer one.
    inst_subst = sorted(inst_name_rewrite.items(), key=lambda kv: -len(kv[0]))
    inst_lines_changed = 0
    if inst_subst:
        for i in range(len(rewritten)):
            if delete[i]:
                continue
            line = rewritten[i]
            new_line = line
            for src, dst in inst_subst:
                if src in new_line:
                    new_line = new_line.replace(src, dst)
            if new_line != line:
                rewritten[i] = new_line
                inst_lines_changed += 1
    print(f"Instance-name lines rewritten: {inst_lines_changed}")

    # Emit (atomic via temp file -- safe even when OUT_MTPL == input).
    kept = [rewritten[i] for i in range(len(rewritten)) if not delete[i]]
    tmp_out = OUT_MTPL.with_suffix(OUT_MTPL.suffix + ".tmp")
    tmp_out.write_text(nl.join(kept), encoding="utf-8", newline="")
    if OUT_MTPL.exists():
        OUT_MTPL.unlink()
    tmp_out.replace(OUT_MTPL)
    print(f"Wrote {OUT_MTPL}")

    # 2g. Symbols CSV (1:1 transposition of compare CSV symbol cells,
    # CYCLE-AWARE: column union across all cycles).
    # Read the merged compare CSV's flow columns directly so the resulting
    # symbols.csv has one column per flow ever seen across all cycles.
    with v3.OUT_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        compare_fields = list(reader.fieldnames or [])
    # Compare CSV schema: Entity, <flows>, DIFF, <flow_lines>, Symbolized,
    # <flow_symbols>. Extract <flows> as the columns between Entity and DIFF.
    all_flows: list[str] = []
    if "Entity" in compare_fields and "DIFF" in compare_fields:
        i_start = compare_fields.index("Entity") + 1
        i_end = compare_fields.index("DIFF")
        all_flows = compare_fields[i_start:i_end]
    if not all_flows:
        all_flows = list(v3.FLOWS)

    # Build per-symbol per-flow values map for ALL flows by re-reading
    # the merged compare CSV's <flow>_symbols cells.
    sym_to_vals: dict[str, dict[str, str]] = {}
    with v3.OUT_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for fn in all_flows:
                blob = (row.get(f"{fn}_symbols") or "").strip()
                if not blob:
                    continue
                for piece in blob.split(";"):
                    piece = piece.strip()
                    if not piece or "=" not in piece:
                        continue
                    k, _, v = piece.partition("=")
                    k = k.strip()
                    if k.startswith("s") and k[1:].isdigit():
                        k = k[1:]
                    arr = sym_to_vals.setdefault(k, {})
                    arr.setdefault(fn, v)

    headers = ["Symbol", *all_flows]
    rows = []
    for sym_num in sorted(sym_to_vals.keys(), key=int):
        row = {"Symbol": _format_sym(f"s{sym_num}")}
        for fn in all_flows:
            row[fn] = sym_to_vals[sym_num].get(fn, "")
        rows.append(row)
    with OUT_SYMBOLS.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT_SYMBOLS}  ({len(rows)} symbols, "
          f"{len(all_flows)} flow columns)")

    return global_symbol_map


def phase_validate() -> int:
    """PHASE 3 — FULL VALIDATION.

    Runs structural checks on the symbolized .mtpl, the symbol-consistency
    cross-check, expands `_bp.mtpl` into a buildable `.mtpl_expanded`,
    and builds both `expanded` and `orig` with torch. Enforces the hard
    contract: `errors(expanded) <= errors(orig)`."""
    print()
    print("=" * 60)
    print("PHASE 3 / 3  —  FULL VALIDATION")
    print("=" * 60)

    # 3a. Structural validation on the SYMBOLIZED file (no build).
    rc = validate_symbolized_mtpl(OUT_MTPL)
    if rc != 0:
        return rc

    # 3b. Symbol-consistency cross-check.
    rc_sym = _verify_symbols_consistency(
        OUT_MTPL, OUT_SYMBOLS, v3.OUT_CSV, list(v3.FLOWS))
    if rc_sym != 0:
        return rc_sym

    # 3c. Expand symbols -> buildable .mtpl_expanded
    expanded_path = _expand_symbols(OUT_MTPL, OUT_SYMBOLS, KEEP_FLOW)

    # 3d. Build the expanded file (always also build orig as baseline).
    orig_path = OUT_MTPL.parent / f"{OUT_MTPL.parent.name}_orig.mtpl"
    rc_build, rc_build_orig, n_err_build, n_err_orig = _run_torch_build_on(
        expanded_path, orig_path)

    print()
    print("=" * 60)
    print("FULL VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  expanded build : exit={rc_build}  errors={n_err_build}")
    print(f"  orig build     : exit={rc_build_orig}  errors={n_err_orig}")

    # Hard contract: PASS only if expanded <= orig.
    if n_err_build > n_err_orig:
        regressed = n_err_build - n_err_orig
        print(f"  FAIL: expanded introduced {regressed} NEW build error(s) "
              f"vs orig baseline.")
        print(f"  See logs:")
        print(f"    {expanded_path.with_suffix('').name}.build.log")
        print(f"    {expanded_path.with_suffix('').name}.build_orig.log")
        return 1
    if n_err_build < n_err_orig:
        improved = n_err_orig - n_err_build
        print(f"  PASS: expanded has {improved} FEWER build error(s) than orig "
              f"(net improvement).")
    else:
        print("  PASS: expanded and orig have identical build error counts.")
    return 0


def main() -> int:
    if not v3.SKILL_CSV.exists():
        print(f"ERROR: skill CSV missing: {v3.SKILL_CSV}", file=sys.stderr)
        return 2

    # CLI: `symbolize_mtpl.py [compare|generate|validate|all]`.
    # Default = `all` (full pipeline). Individual phases can be run
    # standalone provided their inputs (compare CSV / _bp.mtpl) exist.
    phase = "all"
    if len(sys.argv) > 1:
        phase = sys.argv[1].lower()
    if phase not in ("compare", "generate", "validate", "all"):
        print(f"ERROR: unknown phase '{phase}'. "
              f"Use one of: compare, generate, validate, all", file=sys.stderr)
        return 2

    cached_lines: list[str] | None = None
    cached_nl: str = "\n"

    if phase in ("compare", "all"):
        cached_lines, cached_nl = phase_compare()

    if phase in ("generate", "all"):
        if cached_lines is None:
            # Standalone generate: re-read source.
            primary_text = v3.MTPL_PRIMARY.read_text(
                encoding="utf-8", errors="replace")
            cached_nl = "\r\n" if "\r\n" in primary_text[:4096] else "\n"
            cached_lines = primary_text.split(cached_nl)
            _apply_prework(cached_lines)
        phase_generate(cached_lines, cached_nl)

    if phase in ("validate", "all"):
        return phase_validate()

    return 0


def _expand_symbols(symbolized_path: Path, symbols_csv: Path,
                    keep_flow: str) -> Path:
    """Substitute every `\\sN\\` placeholder in the symbolized file with the
    value from `keep_flow`'s column in the symbols CSV (the value that was
    originally present in the kept flow). Empty-column substitutions are
    valid -- they restore the original by removing the optional fragment.
    Writes `<module>.mtpl_expanded` and returns its Path."""
    text = symbolized_path.read_text(encoding="utf-8", errors="replace")
    nl = "\r\n" if "\r\n" in text[:4096] else "\n"

    # Read CSV: header has Symbol + one column per flow.
    sub_map: dict[str, str] = {}
    with symbols_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if keep_flow not in reader.fieldnames:
            print(f"ERROR: keep_flow column '{keep_flow}' not in "
                  f"{symbols_csv.name} (have: {reader.fieldnames})",
                  file=sys.stderr)
            sys.exit(2)
        for row in reader:
            sym = row["Symbol"]  # e.g. "\\s0\\"
            sub_map[sym] = row[keep_flow] or ""

    # Substitute longest first so e.g. \s10\ matches before \s1\.
    keys = sorted(sub_map.keys(), key=lambda s: -len(s))
    pattern = re.compile("|".join(re.escape(k) for k in keys))
    counts = {k: 0 for k in keys}
    def _sub(m):
        k = m.group(0)
        counts[k] += 1
        return sub_map[k]
    expanded = pattern.sub(_sub, text)

    OUT_EXPANDED.write_text(expanded, encoding="utf-8", newline="")
    total = sum(counts.values())
    print()
    print(f"Wrote {OUT_EXPANDED}  ({total} symbol substitutions "
          f"using column '{keep_flow}')")
    # Sanity: any \sN\ left after expansion?
    leftover = re.findall(r"\\s\d+\\", expanded)
    if leftover:
        print(f"  WARN expand: {len(leftover)} unsubstituted \\sN\\ tokens "
              f"remain (e.g. {leftover[:3]})")
    return OUT_EXPANDED


# ---------------------------------------------------------------------------
# Validation (ports of BluePrint validate_mtpl + Expand-BluePrint checks)
# ---------------------------------------------------------------------------

_RE_FLOWITEM = re.compile(r"^\s*\{?\s*(?:FlowItem|DUTFlowItem)\s+(\S+)\s+(\S+)")
# Match any current or future test-definition keyword: any identifier that
# ends in "Test" (CSharpTest, MultiTrialTest, Test, TrialTest, CSharpTrialTest,
# ...). Excluded: TestPlan / TestProgram (file-level openers).
# Two grammar shapes:
#   <Kind> <TemplateName> <InstanceName>
#   <Kind> <InstanceName>
_RE_TEST_DEF = re.compile(
    r"^\s*(?!TestPlan\b|TestProgram\b)"
    r"(?P<kind>[A-Za-z_][A-Za-z_0-9]*Test)\s+"
    r"(?:\S+\s+(?P<n2>\S+)|(?P<n1>\S+))\s*$"
)
_RE_FLOW_DEF = re.compile(r"^\s*(?:Flow|DUTFlow)\s+(\S+)")
_RE_GOTO = re.compile(r"^\s*GoTo\s+([^\s;]+)")


def _strip_quotes(line: str) -> str:
    return re.sub(r'"[^"]*"', '', line)


def _strip_inline_comment(line: str) -> str:
    in_q = False
    for i, ch in enumerate(line):
        if ch == '"' and (i == 0 or line[i - 1] != '\\'):
            in_q = not in_q
        elif ch == '#' and not in_q:
            return line[:i]
    return line


def _check_braces(lines):
    issues = []
    depth = 0
    open_stack = []
    for idx, raw in enumerate(lines, start=1):
        line = _strip_quotes(raw)
        s = line.lstrip()
        if s.startswith('#') and not s.startswith('##'):
            continue
        for ch in line:
            if ch == '{':
                depth += 1
                open_stack.append(idx)
            elif ch == '}':
                if depth <= 0:
                    issues.append(f"Line {idx}: closing '}}' with no matching '{{'")
                else:
                    depth -= 1
                    open_stack.pop()
    if depth > 0:
        for ln in open_stack:
            issues.append(f"Line {ln}: opening '{{' never closed")
    return issues


def _check_backslash_pairs(lines):
    issues = []
    for idx, raw in enumerate(lines, start=1):
        s = raw.lstrip()
        if s.startswith('#') and not s.startswith('##'):
            continue
        content = _strip_inline_comment(raw)
        if content.count('\\') % 2 != 0:
            issues.append(f"Line {idx}: odd number of backslashes: {raw.rstrip()}")
    return issues


def _collect_defs_and_refs(lines):
    """Return (test_defs, flow_defs, flowitem_refs, goto_targets).
    Names are kept as-is (incl. \\sN\\ tokens)."""
    test_defs: dict[str, int] = {}
    flow_defs: dict[str, int] = {}
    fi_refs: list[tuple[int, str, str]] = []  # (line, fi_name, target_ref)
    goto_targets: list[tuple[int, str]] = []
    for idx, raw in enumerate(lines, start=1):
        line = _strip_inline_comment(raw).rstrip()
        if not line.strip():
            continue
        m = _RE_FLOWITEM.match(line)
        if m:
            fi_refs.append((idx, m.group(1), m.group(2).split('@', 1)[0].rstrip()))
            continue
        m = _RE_TEST_DEF.match(line)
        if m:
            tname = m.group("n2") or m.group("n1")
            test_defs.setdefault(tname, idx); continue
        m = _RE_FLOW_DEF.match(line)
        if m:
            name = m.group(1).split('@', 1)[0]
            flow_defs.setdefault(name, idx); continue
        m = _RE_GOTO.match(line)
        if m:
            tgt = m.group(1)
            if tgt and not re.match(r'^(<NEXT>|EXIT|RETURN)', tgt, re.IGNORECASE):
                goto_targets.append((idx, tgt))
    return test_defs, flow_defs, fi_refs, goto_targets


def _check_flowitem_resolution(lines):
    test_defs, flow_defs, fi_refs, goto_targets = _collect_defs_and_refs(lines)
    defs = set(test_defs) | set(flow_defs)
    issues = []
    for ln, fi_name, tgt in fi_refs:
        if tgt in ('__BIN__', '__BNUM__', '__CTR__'):
            continue
        if re.match(r'^-?\d+$', tgt):
            continue
        if tgt not in defs:
            issues.append(
                f"Line {ln}: FlowItem '{fi_name}' references '{tgt}' which has no matching Test/Flow"
            )
    for ln, tgt in goto_targets:
        if tgt not in defs:
            issues.append(f"Line {ln}: GoTo target '{tgt}' has no matching Test/Flow")
    return issues


def _check_test_flow_coverage(lines):
    """Every CSharpTest/MultiTrialTest definition name must appear verbatim
    as a FlowItem ref. Templated names (with \\sN\\) must match templated refs
    character-for-character."""
    test_defs, _flow_defs, fi_refs, _goto = _collect_defs_and_refs(lines)
    referenced = {tgt for (_l, _fi, tgt) in fi_refs}
    issues = []
    for name, ln in test_defs.items():
        if name not in referenced:
            issues.append(f"Line {ln}: Test '{name}' has no FlowItem referencing it")
    return issues


def _normalize_issue_for_diff(issue: str) -> str:
    """Strip leading line-number prefix so the same logical issue text in two
    different files compares equal. Example:
      'Line 1234: Test "X" has no FlowItem...' -> 'Test "X" has no FlowItem...'
    """
    return re.sub(r"^Line\s+\d+:\s*", "", issue).strip()


def validate_symbolized_mtpl(path: Path, orig_path: Path | None = None) -> int:
    """Run BluePrint-style structural checks on the symbolized .mtpl, then
    on `orig_path` (defaults to `<module>.mtpl_orig` next to the symbolized).
    Issues that ALSO appear in the orig are downgraded from FATAL to WARN
    (they are pre-existing source-mtpl problems, not regressions of our
    generation). Returns 0 on success (no NEW fatal issues), 1 otherwise."""
    if orig_path is None:
        # Derive `<module>_orig.mtpl` next to the input. The input filename
        # may be `<module>_bp.mtpl` (re-runs) or `<module>.mtpl_symbolized`
        # (legacy) -- in either case the module name is everything before
        # the first `.` AND before any trailing `_bp` suffix.
        module_name = path.name.split('.', 1)[0]
        if module_name.endswith("_bp"):
            module_name = module_name[:-3]
        orig_path = path.parent / f"{module_name}_orig.mtpl"

    text = path.read_text(encoding="utf-8", errors="replace")
    nl = "\r\n" if "\r\n" in text[:4096] else "\n"
    lines = text.split(nl)

    orig_lines: list[str] | None = None
    if orig_path.exists():
        otext = orig_path.read_text(encoding="utf-8", errors="replace")
        orig_lines = otext.split("\r\n" if "\r\n" in otext[:4096] else "\n")

    print()
    print(f"Validating: {path.name}")
    if orig_lines is not None:
        print(f"  (orig baseline: {orig_path.name})")
    else:
        print("  (no .mtpl_orig found - all issues will be FATAL)")
    print("-" * 60)

    fatal = 0
    warn = 0
    structural = [
        ("Check 1: Brace matching", _check_braces),
        ("Check 4: Backslash pairing", _check_backslash_pairs),
        ("Check 11: FlowItem/GoTo resolution", _check_flowitem_resolution),
        ("Check 9: Test->FlowItem coverage (exact templated name)",
         _check_test_flow_coverage),
    ]
    for title, fn in structural:
        issues = fn(lines)
        if not issues:
            print(f"  PASS {title}")
            continue
        # Compute orig baseline.
        baseline = set()
        if orig_lines is not None:
            for it in fn(orig_lines):
                baseline.add(_normalize_issue_for_diff(it))
        new_issues = [it for it in issues
                      if _normalize_issue_for_diff(it) not in baseline]
        old_issues = [it for it in issues
                      if _normalize_issue_for_diff(it) in baseline]
        if new_issues:
            fatal += len(new_issues)
            print(f"  FAIL {title}: {len(new_issues)} NEW + "
                  f"{len(old_issues)} pre-existing")
            for it in new_issues[:20]:
                print(f"    NEW : {it}")
            if len(new_issues) > 20:
                print(f"    ...and {len(new_issues) - 20} more new")
        else:
            warn += len(old_issues)
            print(f"  WARN {title}: {len(old_issues)} pre-existing in orig "
                  f"(downgraded)")
        for it in old_issues[:5]:
            print(f"    WARN: {it}")
        if len(old_issues) > 5:
            print(f"    ...and {len(old_issues) - 5} more pre-existing")

    print("-" * 60)
    if fatal:
        print(f"Structural validation FAILED: {fatal} new fatal issue(s), "
              f"{warn} pre-existing warning(s)")
        return 1
    print(f"Structural validation PASSED: 0 new issues, {warn} pre-existing warning(s)")
    return 0


def _run_torch_build_on(buildable_path: Path,
                        orig_path: Path) -> tuple[int, int, int, int]:
    """Build `buildable_path` AND `orig_path` (always both, so caller can
    enforce the contract: expanded build errors must be <= orig build
    errors). Returns (rc_build, rc_orig, n_err_build, n_err_orig).
    A return code of 0 with -1 error counts means "build skipped"."""
    module_dir = buildable_path.parent
    module_name = module_dir.name
    # Find repo root: the directory containing NVL_CPU.sln.
    repo_root = module_dir
    while repo_root.parent != repo_root:
        if (repo_root / "NVL_CPU.sln").exists():
            break
        repo_root = repo_root.parent
    sln = repo_root / "NVL_CPU.sln"
    if not sln.exists():
        print(f"  SKIP build: NVL_CPU.sln not found above {module_dir}")
        return 0, 0, -1, -1
    build_class = os.environ.get("SYMBOLIZE_BUILD_CLASS", "Class_NVL_S28C")

    log_main = buildable_path.parent / f"{buildable_path.stem}.build.log"
    rc_b, n_b = _build_with_swap(buildable_path, repo_root, module_name,
                                 build_class, log_main, label="expanded")

    if not orig_path.exists():
        print("  SKIP orig-build: no .mtpl_orig found - cannot compare")
        return rc_b, 0, n_b, -1
    log_orig = buildable_path.parent / f"{buildable_path.stem}.build_orig.log"
    rc_o, n_o = _build_with_swap(orig_path, repo_root, module_name,
                                 build_class, log_orig, label="orig")
    return rc_b, rc_o, n_b, n_o


def _build_with_swap(source_file: Path, repo_root: Path,
                     module: str, build_class: str, log_file: Path,
                     label: str) -> tuple[int, int]:
    """Copy `source_file` over `<module_dir>/<module>.mtpl`, build, restore.
    Returns (return_code, error_count)."""
    module_dir = source_file.parent
    live_mtpl = module_dir / f"{module}.mtpl"
    backup = module_dir / f"{module}.mtpl.swap_backup"
    print(f"  RUN  build ({label}): swap {source_file.name} -> {live_mtpl.name}")
    if live_mtpl.exists():
        if backup.exists():
            backup.unlink()
        live_mtpl.replace(backup)
    try:
        live_mtpl.write_bytes(source_file.read_bytes())
        rc = _invoke_build(repo_root, module_dir, module, build_class,
                           log_file, label=label)
    finally:
        if backup.exists():
            if live_mtpl.exists():
                live_mtpl.unlink()
            backup.replace(live_mtpl)
    # Count `: error TP` occurrences in the build log (torch's standard
    # error-line format). This is the hard metric for the expanded-vs-orig
    # contract enforced by the caller.
    n_err = 0
    if log_file.exists():
        try:
            txt = log_file.read_text(encoding="utf-8", errors="replace")
            n_err = len(re.findall(r" error TP\d+:", txt))
        except OSError:
            pass
    print(f"  {('PASS' if rc == 0 else 'FAIL')} build ({label}): "
          f"exit={rc}  errors={n_err}  log={log_file.name}")
    return rc, n_err


# torch.exe path: matches build_modules.ps1 default. Override with
# SYMBOLIZE_TORCH_EXE if installed elsewhere.
_TORCH_EXE_DEFAULT = r"I:\tpapps\TORCH\Prod22\CLI\torch.exe"


def _invoke_build(repo_root: Path, module_dir: Path, module: str,
                  build_class: str, log_file: Path, label: str) -> int:
    """Invoke `torch.exe build` for THIS MODULE ONLY (no project-reference
    traversal -- pass `BuildProjectReferences=false` so MSBuild does not
    pull in Shared\\Common_Files etc.). Mirrors the torch invocation in
    build_modules.ps1 but skips the dependency walk that produces ~9000
    pre-existing errors from other projects."""
    torch_exe = os.environ.get("SYMBOLIZE_TORCH_EXE", _TORCH_EXE_DEFAULT)
    mtproj = module_dir / f"{module}.mtproj"
    if not mtproj.exists():
        print(f"  SKIP build: {mtproj.name} not found")
        return 0
    if not Path(torch_exe).exists():
        print(f"  SKIP build: torch.exe not found at {torch_exe}")
        return 0
    mtproj_rel = mtproj.relative_to(repo_root).as_posix().replace("/", "\\")
    cmd = [
        torch_exe, "build",
        "-s", "NVL_CPU.sln",
        "-p", mtproj_rel,
        "--ms",
        f"/p:Configuration={build_class}",
        "/p:Platform=Any CPU",
        "/p:BuildProjectReferences=false",
        "-v", "Normal",
    ]
    print(f"  RUN  build ({label}): torch build  module={module}  "
          f"class={build_class}  (module-only, no proj refs)")
    try:
        proc = subprocess.run(
            cmd, cwd=str(repo_root), capture_output=True, text=True,
            timeout=15 * 60,
        )
    except FileNotFoundError:
        print(f"  SKIP build: cannot launch {torch_exe}")
        return 0
    except subprocess.TimeoutExpired:
        print("  FAIL build: timed out after 15 min")
        return 1
    log_file.write_text(
        (proc.stdout or "") + ("\n--- STDERR ---\n" + proc.stderr if proc.stderr else ""),
        encoding="utf-8",
    )
    tail = []
    for ln in (proc.stdout or "").splitlines():
        if re.search(r"Error\(s\)|Warning\(s\)|SUCCESS|FAIL|Result:", ln):
            tail.append(ln.rstrip())
    for ln in tail[-6:]:
        print(f"    {ln}")
    return proc.returncode


def _find_counters_block(lines):
    for i, ln in enumerate(lines):
        if re.match(r"^\s*Counters\s*$", ln):
            j = i
            while j < len(lines) and "{" not in lines[j]:
                j += 1
            end = v3.find_block_end(lines, j)
            return i, end
    return None


if __name__ == "__main__":
    sys.exit(main())
