"""auto_expand_bp.py — expand <MODULE>_auto_bp.mtpl back to a full mtpl by
re-injecting the dropped Test/Flow definitions and replacing the kept
representative Flow blocks with their original group-member Flow blocks.

Inputs (per module dir):
  <MODULE>_auto_bp.mtpl
  <MODULE>_auto_group_flows.csv  (rep + non-rep Flow bodies; one row each)
  <MODULE>_auto_tests.csv        (orphan Test bodies; optional)
  <MODULE>_auto_flows.csv        (orphan helper-Flow bodies; optional)

Output:
  <MODULE>_auto_expanded.mtpl

Algorithm:
1. Read auto BP lines.
2. For each top-level Flow block whose name matches `*_\\sN\\` (the symbolized
   representative), delete the block.
3. After all deletions, append all member Flow bodies from
   <MODULE>_auto_group_flows.csv (verbatim originals).
4. Append all dropped Test bodies + dropped helper-Flow bodies.
5. Write expanded.

The expanded output is structurally equivalent to the original mtpl
(definitions present), though ordering differs — this is acceptable for
validate_mtpl.py which checks structure, not order.
"""
from __future__ import annotations
import csv
import re
import sys
from pathlib import Path

RE_FLOW_DEF = re.compile(r'^(\s*)(Flow|DUTFlow)\s+(\S+)(.*)$')
RE_SYMBOL_NAME = re.compile(r'\\s\d+\\')
RE_TEST_DEF       = re.compile(r'^\s*(?:Test|CSharpTest)\s+\S+\s+(\S+)')
RE_MULTITRIAL_DEF = re.compile(r'^\s*MultiTrialTest\s+(\S+)')
RE_TRIALTEST_DEF  = re.compile(r'^\s*(?:TrialTest|CSharpTrialTest)\s+\S+\s+"([^"]+)"')
RE_COUNTERS_BLOCK = re.compile(r'^\s*Counters\s*$')


def _strip_quotes(s: str) -> str:
    return re.sub(r'"[^"]*"', '', s)


def _find_flow_def_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    blocks = []
    n = len(lines)
    i = 0
    while i < n:
        m = RE_FLOW_DEF.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group(3).rstrip('{').strip()
        depth = 0
        j = i
        opened = False
        while j < n:
            for ch in _strip_quotes(lines[j]):
                if ch == '{':
                    depth += 1
                    opened = True
                elif ch == '}':
                    depth -= 1
            if opened and depth == 0:
                break
            j += 1
        if opened:
            blocks.append((name, i, j))
            i = j + 1
        else:
            i += 1
    return blocks


def _find_test_def_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    blocks = []
    n = len(lines)
    i = 0
    while i < n:
        raw = lines[i]
        name = None
        for rx in (RE_TEST_DEF, RE_MULTITRIAL_DEF, RE_TRIALTEST_DEF):
            m = rx.match(raw)
            if m:
                name = m.group(1)
                break
        if not name:
            i += 1
            continue
        depth = 0
        j = i
        opened = False
        while j < n:
            for ch in _strip_quotes(lines[j]):
                if ch == '{':
                    depth += 1
                    opened = True
                elif ch == '}':
                    depth -= 1
            if opened and depth == 0:
                break
            j += 1
        if opened:
            blocks.append((name, i, j))
            i = j + 1
        else:
            i += 1
    return blocks


def _find_counters_block(lines: list[str]) -> tuple[int, int] | None:
    n = len(lines)
    for i, ln in enumerate(lines):
        if RE_COUNTERS_BLOCK.match(ln):
            j = i
            depth = 0
            opened = False
            while j < n:
                for ch in _strip_quotes(lines[j]):
                    if ch == '{':
                        depth += 1
                        opened = True
                    elif ch == '}':
                        depth -= 1
                if opened and depth == 0:
                    return (i, j)
                j += 1
    return None


def _read_bank(path: Path, body_col: str = 'Body') -> list[dict]:
    if not path.exists():
        return []
    with path.open('r', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def expand(module_dir: str) -> int:
    md = Path(module_dir).resolve()
    module = md.name
    auto_bp = md / f"{module}_auto_bp.mtpl"
    if not auto_bp.exists():
        print(f"[skip] no {auto_bp.name}")
        return 0

    lines = auto_bp.read_text(encoding='utf-8',
                              errors='replace').splitlines(keepends=True)

    # 0. Restore modified non-group Flow bodies (replace in place).
    modified = _read_bank(md / f"{module}_auto_modified_flows.csv")
    if modified:
        mod_by_name = {r['Name']: r['Body'] for r in modified}
        blocks = _find_flow_def_blocks(lines)
        # Replace from bottom to top to keep indices valid
        for nm, s, e in sorted(blocks, key=lambda b: -b[1]):
            if nm in mod_by_name:
                body = mod_by_name[nm]
                if not body.endswith('\n'):
                    body += '\n'
                # Splice: replace lines[s:e+1] with body lines
                body_lines = body.splitlines(keepends=True)
                lines = lines[:s] + body_lines + lines[e + 1:]
        print(f"[expand] restored {len(modified)} modified non-group flow(s)")

    # 1. Drop symbolized rep Flow blocks
    blocks = _find_flow_def_blocks(lines)
    drop = {s: e for nm, s, e in blocks if RE_SYMBOL_NAME.search(nm)}
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if i in drop:
            e = drop[i]
            i = e + 1
            if i < n and lines[i].strip() == '':
                i += 1
            continue
        out.append(lines[i])
        i += 1
    print(f"[expand] dropped {len(drop)} symbolized Flow block(s)")

    # 1b. Drop symbolized top-level Test defs (renamed rep tests).
    test_blocks = _find_test_def_blocks(out)
    drop_t = {s: e for nm, s, e in test_blocks if RE_SYMBOL_NAME.search(nm)}
    if drop_t:
        filtered: list[str] = []
        i = 0
        n = len(out)
        while i < n:
            if i in drop_t:
                e = drop_t[i]
                i = e + 1
                if i < n and out[i].strip() == '':
                    i += 1
                continue
            filtered.append(out[i])
            i += 1
        out = filtered
        print(f"[expand] dropped {len(drop_t)} symbolized Test def(s)")

    # 1c. Restore original Counters block (replaces symbolized entries).
    counters_snap = md / f"{module}_auto_counters.csv"
    if counters_snap.exists():
        orig_cnt_body = counters_snap.read_text(encoding='utf-8')
        if not orig_cnt_body.endswith('\n'):
            orig_cnt_body += '\n'
        cnt_range = _find_counters_block(out)
        if cnt_range:
            cs, ce = cnt_range
            body_lines = orig_cnt_body.splitlines(keepends=True)
            out = out[:cs] + body_lines + out[ce + 1:]
            print(f"[expand] restored original Counters block")

    # 2. Re-inject member Flow bodies
    group_flows = _read_bank(md / f"{module}_auto_group_flows.csv")
    if group_flows:
        out.append("\n# === auto-expander: original group Flow bodies ===\n")
        for r in group_flows:
            body = r['Body']
            if not body.endswith('\n'):
                body += '\n'
            out.append(body)
            out.append('\n')
    print(f"[expand] re-injected {len(group_flows)} member Flow body(ies)")

    # 3. Re-inject dropped Tests
    tests = _read_bank(md / f"{module}_auto_tests.csv")
    if tests:
        out.append("\n# === auto-expander: dropped Test bodies ===\n")
        for r in tests:
            body = r['Body']
            if not body.endswith('\n'):
                body += '\n'
            out.append(body)
            out.append('\n')
    print(f"[expand] re-injected {len(tests)} Test body(ies)")

    # 4. Re-inject dropped helper Flows
    helpers = _read_bank(md / f"{module}_auto_flows.csv")
    if helpers:
        out.append("\n# === auto-expander: dropped helper Flow bodies ===\n")
        for r in helpers:
            body = r['Body']
            if not body.endswith('\n'):
                body += '\n'
            out.append(body)
            out.append('\n')
    print(f"[expand] re-injected {len(helpers)} helper Flow body(ies)")

    out_path = md / f"{module}_auto_expanded.mtpl"
    out_path.write_text(''.join(out), encoding='utf-8')
    print(f"[out] {out_path}  ({len(out)} lines)")
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: auto_expand_bp.py <module_dir>")
        sys.exit(2)
    sys.exit(expand(sys.argv[1]))
