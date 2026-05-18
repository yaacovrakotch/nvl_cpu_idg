"""auto_bp_from_groups.py — generate `_auto_bp.mtpl`, `_auto_symbols.csv` and
`_auto_flows_compare.csv` for a module using the **Independent** collapse
groups produced by recommend_collapse.py.

This is a focused, scope-limited auto-BP that ONLY collapses whole-flow
groups (it does NOT touch parameters / base numbers / connectivity-level
diffs the way the full BluePrint generator does). It exists to validate the
recommender end-to-end and to give a quick "what would auto-BP produce"
view.

Algorithm
---------
1. Read `<MODULE>_orig.mtpl` (or `<MODULE>.mtpl`).
2. Read `<MODULE>_collapse_candidates.csv` and keep rows with Independent=1.
3. For each group (sorted by FirstLines of representative):
     - Representative = alphabetically first member (deterministic).
     - Allocate a new symbol name `sN` (N = group index).
     - Record (sN, members, token values, diff token position).
4. Rewrite the mtpl:
     - For each top-level `Flow` block whose name is a group member:
         * Representative -> keep the block, but rewrite its name and every
           FlowItem name inside the body, symbolizing the diff token (and
           common-affix-bounded variants) to `\sN\`.
         * Non-representative -> skip the whole block.
     - Other top-level `Flow` blocks -> keep verbatim, but also symbolize any
       FlowItem-reference to a removed sibling so it points at the
       representative template (replace the sibling's name with the
       representative-template-name).
5. Emit `<MODULE>_auto_bp.mtpl`.
6. Emit `<MODULE>_auto_symbols.csv` in the canonical schema:
       Symbol,<flow1>,<flow2>,...
7. Emit `<MODULE>_auto_flows_compare.csv` minimally (one row per group with
   the symbolized template + per-flow symbol values).
"""
from __future__ import annotations
import csv
import re
import sys
from pathlib import Path

# Re-use parsing helpers from recommend_collapse
sys.path.insert(0, str(Path(__file__).resolve().parent))
from recommend_collapse import (  # noqa: E402
    find_flow_blocks, flowitems_in, _common_affix, symbolize_item,
)


def load_groups(csv_path: Path) -> list[dict]:
    with csv_path.open('r', newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    out = [r for r in rows if int(r.get('Independent', '0') or 0) == 1]
    # Sort: smaller FirstLine first (parents earlier in file). Stable so we
    # process top-of-file groups before bottom-of-file ones.
    def first_line(r):
        try:
            return int(r['FirstLines'].split(';')[0])
        except Exception:
            return 0
    out.sort(key=first_line)
    return out


def build_symbol_table(groups: list[dict]) -> list[dict]:
    """Annotate each group with: symbol name, representative, token_pos,
    template (name with diff token replaced by `\\sN\\`), per-member token
    value, common pre/suf around core (for body symbolization).

    Symbol DEDUP: groups with the same sorted token-value tuple AND the
    same rep-token value share a single `\\sN\\`. This avoids allocating
    `\\s2\\`/`\\s3\\` for groups whose value sequence is identical to a
    previously processed group within the same module (e.g. CPU0 and CPU1
    UV/OV families).
    """
    table = []
    # Map: (sorted token-values, rep-token) -> symbol-name (e.g. "s0").
    dedup: dict[tuple[tuple[str, ...], str], str] = {}
    next_idx = 0
    for g in groups:
        members = g['Members'].split('; ')
        token_vals_set = sorted({v for v in g['TokenValues'].split('; ') if v})
        pos = int(g['DiffTokenPos'])
        rep = sorted(members)[0]
        # Validate that for every member, the token at `pos` is one of values
        for m in members:
            parts = m.split('_')
            if pos >= len(parts):
                break
        all_token_vals = [m.split('_')[pos] for m in members]
        rep_token = rep.split('_')[pos]
        dedup_key = (tuple(sorted(all_token_vals)), rep_token)
        if dedup_key in dedup:
            symbol = dedup[dedup_key]
        else:
            symbol = f"s{next_idx}"
            dedup[dedup_key] = symbol
            next_idx += 1
        # Build template name with diff token replaced
        rep_parts = rep.split('_')
        rep_parts[pos] = f"\\{symbol}\\"
        template_name = '_'.join(rep_parts)
        # Common affix across tokens (for embedded-form symbolization)
        pre, suf = _common_affix(all_token_vals)
        table.append({
            'symbol': symbol,
            'members': members,
            'rep': rep,
            'pos': pos,
            'token_for': {m: m.split('_')[pos] for m in members},
            'template_name': template_name,
            'pre': pre,
            'suf': suf,
            'all_token_vals': all_token_vals,
            'orig_template': g['Template'],  # e.g. L2_<X>_MIN
            'ok_ratio': g['OK_Ratio'],
        })
    return table


def symbolize_with_symbol(item: str, this_value: str,
                          all_values: list[str], symbol: str) -> str:
    """Like recommend_collapse.symbolize_item but writes `\\sN\\` instead of
    `<X>`."""
    sym = symbolize_item(item, this_value, all_values)
    return sym.replace('<X>', f'\\{symbol}\\')


# Build a map: member-name -> (entry, this_value). Used to rewrite both
# flow-definition names AND FlowItem references that target removed siblings.
def build_member_index(table: list[dict]) -> dict[str, tuple[dict, str]]:
    idx = {}
    for entry in table:
        for m in entry['members']:
            idx[m] = (entry, entry['token_for'][m])
    return idx


RE_FLOW_DEF = re.compile(r'^(\s*)(Flow|DUTFlow)\s+(\S+)(.*)$')
RE_FLOWITEM = re.compile(r'^(\s*)(FlowItem|DUTFlowItem)\s+(\S+)\s+(\S+)(.*)$')

# Test-definition patterns (mirrors validate_mtpl.py)
RE_TEST_DEF       = re.compile(r'^\s*(?:Test|CSharpTest)\s+\S+\s+(\S+)')
RE_MULTITRIAL_DEF = re.compile(r'^\s*MultiTrialTest\s+(\S+)')
RE_TRIALTEST_DEF  = re.compile(r'^\s*(?:TrialTest|CSharpTrialTest)\s+\S+\s+"([^"]+)"')


def _collect_referenced_names(lines: list[str]) -> set[str]:
    """Return the set of names referenced by FlowItem/DUTFlowItem in lines."""
    refs = set()
    for ln in lines:
        m = RE_FLOWITEM.match(ln)
        if m:
            ref = m.group(4).split('@')[0].rstrip()
            refs.add(ref)
    return refs


def _find_test_def_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """Find top-level Test/MultiTrialTest/CSharpTrialTest blocks.
    Returns list of (name, start_idx, end_idx_inclusive_of_close_brace)."""
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
        # Find matching brace block
        depth = 0
        j = i
        opened = False
        while j < n:
            content = re.sub(r'"[^"]*"', '', lines[j])
            for ch in content:
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


def _find_flow_def_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """Find top-level Flow/DUTFlow blocks.
    Returns list of (name, start_idx, end_idx_inclusive_of_close_brace)."""
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
            content = re.sub(r'"[^"]*"', '', lines[j])
            for ch in content:
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


def compute_test_renames(table: list[dict],
                         lines: list[str],
                         flows: list[tuple[str, int, int]]
                         ) -> dict[str, dict]:
    """For each group, walk the rep flow's FlowItems in order; find the test
    at the same ordinal position in each member flow; if the rep's group
    token value (`this_value`) is a substring of the rep test name AND
    substituting it with each member's token value yields the actual
    member's test name -> register a rename.

    A rename is rejected if the test is also referenced from outside the
    group's member flows (would break the outside reference).

    Returns: {rep_test_name: {
        'symbol':           'sN',         # group symbol
        'this_value':       'XX',         # rep's group token value
        'symbolized':       'name_\\sN\\_…',
        'per_member':       {member_flow: member_test_name, …},
        'token_for':        {member_flow: token_value, …},
    }}
    """
    raw = [l.rstrip('\n') for l in lines]
    flow_ranges = {n: (s, e) for n, s, e in flows}

    def items_of(flow_name: str) -> list[str]:
        if flow_name not in flow_ranges:
            return []
        s, e = flow_ranges[flow_name]
        return [it[0] for it in flowitems_in(raw, s, e)]

    # Map: test-def name -> raw body text (from orig). Used to validate
    # whole-body substring substitution safety: if every member test body
    # equals the rep's body after `rep_val -> member_val`, the rep_val
    # token is safe to symbolize as `\sN\` everywhere in the rep body
    # (param values, counter labels, etc.).
    test_body_by_name: dict[str, str] = {}
    for nm, s, e in _find_test_def_blocks(lines):
        test_body_by_name[nm] = ''.join(lines[s:e + 1])

    # Build per-flow referenced-name sets. ref_in_flow[F] = set of test/flow
    # names referenced by FlowItems AND GoTo statements inside flow F's body.
    goto_re = re.compile(r'^\s*GoTo\s+([^;]+);')
    ref_in_flow: dict[str, set[str]] = {}
    for fn, fs, fe in flows:
        s = set()
        for k in range(fs, fe + 1):
            m = RE_FLOWITEM.match(lines[k])
            if m:
                ref = m.group(4).split('@')[0].rstrip()
                ref = ref.split('::')[-1].split('.')[0]
                s.add(ref)
                s.add(m.group(3))  # FlowItem first token (test name)
            else:
                gm = goto_re.match(lines[k])
                if gm:
                    g = gm.group(1).strip()
                    g = g.split('::')[-1].split('.')[0]
                    s.add(g)
        ref_in_flow[fn] = s

    renames: dict[str, dict] = {}
    for entry in table:
        rep = entry['rep']
        sym = entry['symbol']
        rep_val = entry['token_for'][rep]
        rep_items = items_of(rep)
        # Per-member item lists (skip rep)
        member_items = {m: items_of(m) for m in entry['members']}
        if not all(len(member_items[m]) == len(rep_items)
                   for m in entry['members']):
            continue  # shape mismatch -> skip whole entry
        group_member_set = set(entry['members'])
        for pos, rep_test in enumerate(rep_items):
            per_member = {m: member_items[m][pos] for m in entry['members']}
            if len(set(per_member.values())) == 1:
                continue  # all identical
            if rep_val == '' or rep_val not in rep_test:
                continue  # cannot substring-substitute
            # Validate: subst(rep_test, rep_val, member_val) == member_test
            ok = True
            for m, mt in per_member.items():
                mv = entry['token_for'][m]
                if rep_test.replace(rep_val, mv) != mt:
                    ok = False
                    break
            if not ok:
                continue
            # Reject if any of the per-member test names is referenced from
            # OUTSIDE the group's member flows (renaming would dangle).
            outside_ref = False
            for member_test_name in per_member.values():
                for fn, refs in ref_in_flow.items():
                    if fn in group_member_set:
                        continue
                    if member_test_name in refs:
                        outside_ref = True
                        break
                if outside_ref:
                    break
            if outside_ref:
                continue
            if rep_test in renames:
                continue  # already registered (shared across groups)
            symbolized = rep_test.replace(rep_val, f"\\{sym}\\")
            # Whole-body substitution safety check: if for EVERY member,
            # the member test's body equals the rep's body after
            # `rep_val -> member_val`, then `rep_val` is safe to
            # symbolize anywhere in the rep body (param values, counter
            # labels, sub-bin entries, ...). Any rep_val occurrence that
            # isn't truly a variant would cause a mismatch and reject.
            safe_body_subst = False
            rep_body = test_body_by_name.get(rep_test)
            if rep_body and rep_val in rep_body:
                ok_body = True
                for m, mt in per_member.items():
                    mv = entry['token_for'][m]
                    member_body = test_body_by_name.get(mt)
                    if member_body is None:
                        ok_body = False
                        break
                    if rep_body.replace(rep_val, mv) != member_body:
                        ok_body = False
                        break
                safe_body_subst = ok_body
            renames[rep_test] = {
                'symbol': sym,
                'this_value': rep_val,
                'symbolized': symbolized,
                'per_member': per_member,
                'token_for': dict(entry['token_for']),
                'safe_body_subst': safe_body_subst,
            }
    return renames


def _snapshot_test_defs(lines: list[str], names: set[str]) -> list[dict]:
    """Return list of {'name','body'} for top-level Test defs whose name is in
    `names`. Body is the raw multi-line text."""
    out = []
    for nm, s, e in _find_test_def_blocks(lines):
        if nm in names:
            out.append({'name': nm, 'body': ''.join(lines[s:e + 1])})
    return out


RE_COUNTERS_BLOCK = re.compile(r'^\s*Counters\s*$')


def _find_counters_block(lines: list[str]) -> tuple[int, int] | None:
    """Return (start, end_inclusive) of the top-level `Counters { ... }`
    block, or None if not found."""
    n = len(lines)
    for i, ln in enumerate(lines):
        if RE_COUNTERS_BLOCK.match(ln):
            j = i
            depth = 0
            opened = False
            while j < n:
                for ch in re.sub(r'"[^"]*"', '', lines[j]):
                    if ch == '{':
                        depth += 1
                        opened = True
                    elif ch == '}':
                        depth -= 1
                if opened and depth == 0:
                    return (i, j)
                j += 1
    return None


def apply_test_renames(new_lines: list[str],
                       renames: dict[str, dict],
                       rep_flow_template_names: set[str]) -> list[str]:
    """Apply substring substitutions across the auto-BP text:
      * In each rep Flow block (header matches `*\\sN\\*`): every
        occurrence of `rep_test_name` -> `symbolized_name` AND every
        occurrence of `this_value` inside lines that reference the rep
        test (counter/bin labels) gets rewritten naturally via the
        rep_test_name substitution (since it contains `this_value`).
      * In each top-level Test def whose name is a rename key: header is
        renamed.
      * In the Counters {} block: each entry containing `rep_test_name` is
        renamed (substring) so the rep's counter declarations match the
        symbolized IncrementCounters refs in the rep body.
    Returns updated lines.
    """
    if not renames:
        return new_lines

    # Build sorted rename keys by length DESC so longer names substitute
    # before shorter ones (avoid partial-overlap bugs).
    sorted_renames = sorted(renames.items(), key=lambda kv: -len(kv[0]))

    def rewrite_text(text: str) -> str:
        for rep_test, info in sorted_renames:
            if rep_test in text:
                text = text.replace(rep_test, info['symbolized'])
        return text

    # Token-value substitution (e.g. "07" -> "\\s1\\") — only applied
    # inside rep test/flow bodies and only for renames where the WHOLE
    # rep body equals each member body under `rep_val -> member_val`
    # (validated by `safe_body_subst`). We index by group symbol so a
    # rep flow body uses the correct (rep_val, symbol) pair: all rep
    # test names in a given rep flow share the same group symbol.
    # Map: symbol-name (e.g. "s0") -> rep_val (e.g. "07").
    safe_token_for_sym: dict[str, str] = {}
    for _name, info in sorted_renames:
        if info.get('safe_body_subst'):
            safe_token_for_sym.setdefault(info['symbol'], info['this_value'])

    def rewrite_with_token(text: str, sym: str | None) -> str:
        text = rewrite_text(text)
        if sym is None:
            return text
        rep_val = safe_token_for_sym.get(sym)
        if rep_val and rep_val in text:
            text = text.replace(rep_val, f"\\{sym}\\")
        return text

    _sym_in_name_re = re.compile(r"\\s(\d+)\\")

    def _sym_of(flow_or_test_name: str) -> str | None:
        m = _sym_in_name_re.search(flow_or_test_name)
        return f"s{m.group(1)}" if m else None

    out: list[str] = []
    n = len(new_lines)
    i = 0
    flow_blocks = _find_flow_def_blocks(new_lines)
    # Rep flow body: name carries the group symbol (e.g. `UV_\s0\`).
    rep_block_ranges: dict[int, tuple[int, str | None]] = {
        s: (e, _sym_of(nm)) for nm, s, e in flow_blocks
        if nm in rep_flow_template_names
    }
    # Sub-Flow def renamed (matches rename key): name still original; look up
    # the symbol in the rename info.
    rep_flow_def_ranges: dict[int, tuple[int, str | None]] = {
        s: (e, renames[nm]['symbol']) for nm, s, e in flow_blocks
        if nm in renames
    }
    test_blocks = _find_test_def_blocks(new_lines)
    rep_test_ranges: dict[int, tuple[int, str | None]] = {
        s: (e, renames[nm]['symbol']) for nm, s, e in test_blocks
        if nm in renames
    }
    counters = _find_counters_block(new_lines)

    while i < n:
        # Rep flow body
        if i in rep_block_ranges:
            e, sym = rep_block_ranges[i]
            for k in range(i, e + 1):
                out.append(rewrite_with_token(new_lines[k], sym))
            i = e + 1
            continue
        # Sub-Flow def renamed (matches rename key)
        if i in rep_flow_def_ranges:
            e, sym = rep_flow_def_ranges[i]
            for k in range(i, e + 1):
                out.append(rewrite_with_token(new_lines[k], sym))
            i = e + 1
            continue
        # Rep test def (rename header + body)
        if i in rep_test_ranges:
            e, sym = rep_test_ranges[i]
            for k in range(i, e + 1):
                out.append(rewrite_with_token(new_lines[k], sym))
            i = e + 1
            continue
        # Counters block: rewrite per-line (only lines containing rep_test)
        if counters and counters[0] <= i <= counters[1]:
            out.append(rewrite_text(new_lines[i]))
            i += 1
            continue
        out.append(new_lines[i])
        i += 1
    return out


def drop_orphan_tests(new_lines: list[str], orig_lines: list[str],
                      keep_flow_names: set[str]
                      ) -> tuple[list[str], list[dict], list[dict]]:
    """Remove top-level Test AND helper Flow definitions that became orphan
    because of the collapse. Orphan = referenced in orig but not in new.

    keep_flow_names are Flow names that must be kept regardless (rep flows
    and the MainFlow). Iterates until fixed point so cascading orphans are
    removed too.

    Returns (filtered_lines, dropped_tests, dropped_flows).
    """
    orig_refs = _collect_referenced_names(orig_lines)
    dropped_tests: list[dict] = []
    dropped_flows: list[dict] = []
    current = new_lines

    # Iterate to fixed point. Cap to avoid infinite loops.
    for _ in range(10):
        new_refs = _collect_referenced_names(current)
        newly_orphan = orig_refs - new_refs

        # Tests
        t_blocks = _find_test_def_blocks(current)
        t_drop = [b for b in t_blocks if b[0] in newly_orphan]
        # Flows (skip protected ones and MainFlow)
        f_blocks = _find_flow_def_blocks(current)
        f_drop = []
        for nm, s, e in f_blocks:
            if nm in keep_flow_names:
                continue
            if nm == 'MainFlow':
                continue
            # An orphan flow def has zero FlowItem refs in current.
            # Use orig_refs as the trigger so we only drop flows that USED to
            # be referenced (avoid touching pre-existing baseline orphans).
            if nm in orig_refs and nm not in new_refs:
                f_drop.append((nm, s, e))

        if not t_drop and not f_drop:
            break

        drop_map: dict[int, tuple[str, int, str]] = {}
        for nm, s, e in t_drop:
            drop_map[s] = (nm, e, 'test')
        for nm, s, e in f_drop:
            drop_map[s] = (nm, e, 'flow')
        out: list[str] = []
        i = 0
        n = len(current)
        while i < n:
            if i in drop_map:
                nm, e, kind = drop_map[i]
                body = ''.join(current[i:e + 1])
                rec = {'name': nm, 'body': body}
                if kind == 'test':
                    dropped_tests.append(rec)
                else:
                    dropped_flows.append(rec)
                i = e + 1
                if i < n and current[i].strip() == '':
                    i += 1
                continue
            out.append(current[i])
            i += 1
        current = out

    return current, dropped_tests, dropped_flows


def write_tests_bank_csv(out_path: Path, dropped: list[dict]) -> None:
    """Persist the dropped Test definitions so the auto-expander can re-inject
    them. Stored as: Name,Body (multi-line body kept in one CSV cell)."""
    with out_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Name', 'Body'])
        for d in dropped:
            w.writerow([d['name'], d['body']])


def write_collapsed_flows_md(out_path: Path, module: str,
                             table: list[dict]) -> None:
    """Human-readable summary of which flows were collapsed."""
    lines = [
        f"# {module} — collapsed flows ({len(table)} group(s))",
        "",
        "One row per collapse group. **Representative** is the kept Flow "
        "definition (renamed with a `\\sN\\` symbol). **Members removed** "
        "are the Flow definitions deleted from the BP (their FlowItem refs "
        "now point at the representative's symbolized template).",
        "",
        "| # | Symbol | Template | OK | Representative (kept) | Members removed | Token values |",
        "|---|--------|----------|----|----------------------|-----------------|--------------|",
    ]
    for i, e in enumerate(table, 1):
        removed = [m for m in e['members'] if m != e['rep']]
        tokens = ', '.join(sorted({e['token_for'][m] for m in e['members']}))
        ok = f"{float(e['ok_ratio']) * 100:.0f}%"
        lines.append(
            f"| {i} | `\\{e['symbol']}\\` | `{e['template_name']}` | {ok} | "
            f"`{e['rep']}` | {', '.join(f'`{m}`' for m in removed)} | "
            f"{tokens} |"
        )
    lines.append("")
    out_path.write_text('\n'.join(lines), encoding='utf-8')


def emit_auto_bp(src_lines: list[str], flows: list[tuple[str, int, int]],
                 table: list[dict], member_idx: dict) -> list[str]:
    """Rewrite the mtpl. Returns new list of lines."""
    flow_ranges = {n: (s, e) for n, s, e in flows}
    # Find the full block (including the `Flow <name>` header line and the
    # closing brace). flowitems_in body is (start, end) where start=header+1
    # and end=index-of-matching-}. We need to know the header line too.
    header_of: dict[str, int] = {}
    for n, s, e in flows:
        # header is the first line at/before `s` that matches RE_FLOW_DEF
        for k in range(s - 1, max(-1, s - 5), -1):
            if RE_FLOW_DEF.match(src_lines[k]):
                if RE_FLOW_DEF.match(src_lines[k]).group(3).rstrip('{') == n:
                    header_of[n] = k
                    break

    # Map each line index -> "skip" or "rewrite-with-entry" or "verbatim"
    n = len(src_lines)
    out: list[str] = []
    i = 0
    while i < n:
        line = src_lines[i]
        m = RE_FLOW_DEF.match(line)
        if m:
            name = m.group(3).rstrip('{')
            if name in member_idx:
                entry, this_val = member_idx[name]
                # Determine block end (matching brace) from flow_ranges
                if name in flow_ranges:
                    _bstart, bend = flow_ranges[name]
                    if name != entry['rep']:
                        # Drop entire block including closing }
                        i = bend + 1
                        continue
                    # Representative: rewrite header (Flow's own name) but
                    # keep the body verbatim. Rationale: matching the
                    # human-built BP, only the Flow *definition name* carries
                    # the symbol; body FlowItem refs stay literal so the
                    # static validator can still resolve them to existing
                    # Test / Flow definitions in the module. Cross-group refs
                    # (a body ref whose target is ITSELF a non-rep member of
                    # another collapse group) are rewritten to point at that
                    # other group's representative template.
                    indent, kw, _nm, tail = m.group(1), m.group(2), m.group(3), m.group(4)
                    new_name = entry['template_name']
                    out.append(f"{indent}{kw} {new_name}{tail}\n" if not line.endswith('\n')
                               else f"{indent}{kw} {new_name}{tail}\n")
                    for j in range(i + 1, bend + 1):
                        body = src_lines[j]
                        body_m = RE_FLOWITEM.match(body)
                        if body_m:
                            indent2, kw2, fname, fref, tail2 = body_m.groups()
                            new_fname, new_fref = fname, fref
                            # Cross-group rewrite: only if the ref's head is a
                            # non-rep member of a DIFFERENT collapse group.
                            head = fref.split('::')[-1].split('.')[0]
                            if head in member_idx and head != name:
                                other_entry, _ov = member_idx[head]
                                if head != other_entry['rep']:
                                    new_fref = fref.replace(
                                        head, other_entry['template_name'], 1)
                            if fname in member_idx and fname != name:
                                other_entry, _ov = member_idx[fname]
                                if fname != other_entry['rep']:
                                    new_fname = other_entry['template_name']
                            if new_fname != fname or new_fref != fref:
                                out.append(f"{indent2}{kw2} {new_fname} {new_fref}{tail2}\n")
                            else:
                                out.append(body if body.endswith('\n') else body + '\n')
                        else:
                            out.append(body if body.endswith('\n') else body + '\n')
                    i = bend + 1
                    continue
            # name not in member_idx -> verbatim header; fall through to default
        # Default: keep line verbatim, but if it's a FlowItem ref to a removed
        # sibling, symbolize the ref. Also rewrite refs in top-level flow
        # bodies (outside any group block).
        item_m = RE_FLOWITEM.match(line)
        if item_m:
            indent, kw, fname, fref, tail = item_m.groups()
            # fref may be `MODULE::SUBFLOW.LEAF` — split and check head
            new_fref = fref
            # Try matching the bare head against member_idx
            head = fref.split('::')[-1].split('.')[0]
            if head in member_idx:
                entry, this_val = member_idx[head]
                # Replace head with the symbolized template head
                rep_tmpl_head = entry['template_name']
                new_fref = fref.replace(head, rep_tmpl_head, 1)
            # Also symbolize fname if it directly references a member
            new_fname = fname
            if fname in member_idx:
                entry, this_val = member_idx[fname]
                new_fname = entry['template_name']
            if new_fname != fname or new_fref != fref:
                out.append(f"{indent}{kw} {new_fname} {new_fref}{tail}\n")
                i += 1
                continue
        out.append(line if line.endswith('\n') else line + '\n')
        i += 1
    return out


def _parse_flow_results(body_text: str) -> dict[str, dict[str, list[str]]]:
    """Parse a Flow body's text. Returns:
       { flowitem_name: { result_code: [body_line, ...] } }

    body_line list excludes the `Result N {` and matching `}` lines — only
    the inner content."""
    lines = body_text.splitlines(keepends=True)
    out: dict[str, dict[str, list[str]]] = {}
    n = len(lines)
    i = 0
    cur_fi: str | None = None
    fi_brace_depth = 0
    fi_started = False
    while i < n:
        ln = lines[i]
        m_fi = RE_FLOWITEM.match(ln)
        if m_fi and (cur_fi is None or not fi_started):
            cur_fi = m_fi.group(3)
            out.setdefault(cur_fi, {})
            fi_brace_depth = 0
            fi_started = False
            # Walk this FlowItem block
            j = i
            while j < n:
                content = re.sub(r'"[^"]*"', '', lines[j])
                for ch in content:
                    if ch == '{':
                        fi_brace_depth += 1
                        fi_started = True
                    elif ch == '}':
                        fi_brace_depth -= 1
                if fi_started and fi_brace_depth == 0:
                    break
                j += 1
            # Within lines[i+1:j], find Result blocks
            k = i + 1
            while k < j:
                m_r = re.match(r'^\s*Result\s+(\S+)\s*$', lines[k])
                if not m_r:
                    k += 1
                    continue
                code = m_r.group(1)
                # Find matching brace
                kk = k
                depth = 0
                opened = False
                while kk < j:
                    content = re.sub(r'"[^"]*"', '', lines[kk])
                    for ch in content:
                        if ch == '{':
                            depth += 1
                            opened = True
                        elif ch == '}':
                            depth -= 1
                    if opened and depth == 0:
                        break
                    kk += 1
                # Body = lines between k+1 (Result line) and kk-1 (close brace).
                # The Result line is at k, the open brace `{` may be on k+1.
                body_start = k + 1
                if body_start < n and lines[body_start].strip() == '{':
                    body_start += 1
                body_end = kk - 1
                if body_end >= 0 and lines[body_end].strip() == '}':
                    body_end -= 1
                body = lines[body_start:body_end + 1]
                out[cur_fi][code] = body
                k = kk + 1
            i = j + 1
            cur_fi = None
            fi_started = False
            continue
        i += 1
    return out


def _normalize_body(body_lines: list[str], from_token: str,
                    to_token: str) -> str:
    """Return body text after substituting `from_token` -> `to_token`."""
    text = ''.join(body_lines)
    if from_token and from_token != to_token:
        text = text.replace(from_token, to_token)
    return text


# Whole-statement patterns used by `_shape_normalize` for body-shape
# dedup. We abstract `SetBin <label>;` and `IncrementCounters <label>;`
# to placeholders because the labels embed bin numbers, module name,
# FlowItem name, member token, and result-code suffix — none of which
# carry structural information about the port behavior.
_SETBIN_RE = re.compile(r'SetBin\s+\S+?;')
_INCR_RE = re.compile(r'IncrementCounters\s+\S+?;')


def _shape_normalize(text: str) -> str:
    """Shape-normalized form of a Result body for body-symbol dedup.

    Abstracts `SetBin ...;` -> `SetBin <BIN>;` and
    `IncrementCounters ...;` -> `IncrementCounters <CTR>;` so two Result
    bodies sharing the same port-behavior structure (kill / pass /
    continue / goto) collapse to one body-symbol regardless of which
    bin or counter identifier is set.
    """
    s = _SETBIN_RE.sub('SetBin <BIN>;', text)
    s = _INCR_RE.sub('IncrementCounters <CTR>;', s)
    return s


def symbolize_divergent_results(bp_lines: list[str],
                                table: list[dict],
                                member_bodies: list[dict]
                                ) -> tuple[list[str], dict]:
    """Post-pass on `_auto_bp.mtpl` lines: walk every rep Flow block (those
    whose name contains `\\sN\\`) and, for each FlowItem inside, compare its
    Result blocks against the corresponding sibling members' Result blocks.
    Where bodies diverge across members (after canonicalizing the variant
    token to the rep's), replace the rep's Result body with a single
    `\\sM\\` placeholder line. Allocate fresh symbols starting at one past
    the highest existing name-symbol number. Returns:
        (new_bp_lines, body_symbols)
        body_symbols: { 'sM': { member_name: body_text, ... } }

    The expander already restores all member Flow bodies verbatim from
    `_auto_group_flows.csv`, so this purely-cosmetic symbolization does
    NOT affect build correctness; it only makes the BP file informative
    (port-divergence inline-visible)."""
    body_symbols: dict[str, dict[str, str]] = {}
    # Highest existing name-symbol number.
    max_idx = -1
    for e in table:
        sym = e.get('symbol', '')
        m = re.match(r's(\d+)$', sym)
        if m:
            n = int(m.group(1))
            if n > max_idx:
                max_idx = n
    next_idx = max_idx + 1
    # Memoize symbol assignment by per-member-SHAPE-tuple so
    # structurally-equivalent divergence patterns share a single symbol
    # across FlowItems / Results / groups. The shape strips numeric
    # identifiers (bin numbers `b\d+`, counter numbers `n\d+`) and member
    # token (already canonicalized to rep_token) so e.g. all "kill on
    # R-2 with bin" bodies dedup to one symbol regardless of which bin
    # number is set.
    body_to_sym: dict[tuple, str] = {}

    # Group member bodies by group symbol.
    members_by_group_sym: dict[str, list[dict]] = {}
    for mb in member_bodies:
        members_by_group_sym.setdefault(mb['symbol'], []).append(mb)

    # Pre-parse each member's Flow body once.
    parsed_by_member: dict[str, dict] = {}  # member_name -> parsed dict
    for mb in member_bodies:
        parsed_by_member[mb['name']] = _parse_flow_results(mb['body'])

    # Find rep Flow blocks in current bp_lines (post-rename, post-trim).
    blocks = _find_flow_def_blocks(bp_lines)
    # Process bottom-up to keep indices valid as we splice.
    for fname, fs, fe in sorted(blocks, key=lambda b: -b[1]):
        m = re.search(r'\\(s\d+)\\', fname)
        if not m:
            continue
        sym = m.group(1)
        members = members_by_group_sym.get(sym)
        if not members or len(members) < 2:
            continue
        # Symbol-dedup in `build_symbol_table` can put multiple physically-
        # distinct groups under the same `\sN\` (e.g. UV_* and UV_*_CPU1
        # both share `s0` because they have the same sorted token tuple
        # and the same rep token). Filter members to ONLY those whose
        # literal name, when their variant token is replaced by the
        # symbolic placeholder, matches THIS rep block's name. Otherwise
        # FlowItem lookups against those out-of-block members would fail
        # and the divergence detection would silently skip every Result.
        block_relevant = []
        sym_placeholder = f"\\{sym}\\"
        for mb in members:
            if not mb['token']:
                continue
            if mb['name'].replace(mb['token'], sym_placeholder) == fname:
                block_relevant.append(mb)
        if len(block_relevant) < 2:
            continue
        rep_mb = next((mb for mb in block_relevant if mb['is_rep'] == '1'),
                      None)
        if rep_mb is None:
            # Fallback: when build_symbol_table assigned IsRep across the
            # whole symbol-group (not per physical group), this block's
            # subset may have no IsRep=1. Pick the alphabetically-first
            # member as a deterministic substitute (matches build_symbol_
            # table's sort).
            rep_mb = sorted(block_relevant, key=lambda x: x['name'])[0]
        rep_token = rep_mb['token']
        # Rewrite this block.
        block_lines = list(bp_lines[fs:fe + 1])
        new_block_lines = _rewrite_rep_block(
            block_lines, sym, block_relevant, parsed_by_member, rep_token,
            body_symbols, body_to_sym, next_idx)
        # Update next_idx based on what was allocated.
        for s in body_symbols.keys():
            mm = re.match(r's(\d+)$', s)
            if mm:
                v = int(mm.group(1))
                if v >= next_idx:
                    next_idx = v + 1
        bp_lines = bp_lines[:fs] + new_block_lines + bp_lines[fe + 1:]

    return bp_lines, body_symbols


def _rewrite_rep_block(block_lines: list[str], group_sym: str,
                       members: list[dict],
                       parsed_by_member: dict,
                       rep_token: str,
                       body_symbols: dict,
                       body_to_sym: dict,
                       next_idx_start: int) -> list[str]:
    """Walk FlowItem/Result structure inside a single rep Flow block; replace
    each diverging Result body with `\\sM\\`. Returns new block lines."""
    out: list[str] = []
    n = len(block_lines)
    i = 0
    next_idx = [next_idx_start]
    while i < n:
        ln = block_lines[i]
        m_fi = RE_FLOWITEM.match(ln)
        if not m_fi:
            out.append(ln)
            i += 1
            continue
        # FlowItem name in the BP may carry a `\sN\` token. Map it back to
        # the rep's literal name to look up in parsed_by_member.
        bp_fi_name = m_fi.group(3)
        rep_fi_name = bp_fi_name.replace(f"\\{group_sym}\\", rep_token)
        # Find the FlowItem's brace range.
        depth = 0
        opened = False
        j = i
        while j < n:
            content = re.sub(r'"[^"]*"', '', block_lines[j])
            for ch in content:
                if ch == '{':
                    depth += 1
                    opened = True
                elif ch == '}':
                    depth -= 1
            if opened and depth == 0:
                break
            j += 1
        if not opened:
            out.append(ln)
            i += 1
            continue
        # Inside lines[i+1:j], find Result blocks and possibly rewrite.
        fi_lines = list(block_lines[i:j + 1])
        new_fi_lines = _rewrite_flowitem(
            fi_lines, group_sym, members, parsed_by_member,
            rep_fi_name, rep_token, body_symbols, body_to_sym, next_idx)
        out.extend(new_fi_lines)
        i = j + 1
    return out


def _rewrite_flowitem(fi_lines: list[str], group_sym: str,
                      members: list[dict], parsed_by_member: dict,
                      rep_fi_name: str, rep_token: str,
                      body_symbols: dict, body_to_sym: dict,
                      next_idx: list) -> list[str]:
    """Within a FlowItem block, walk Result subblocks, compare per-member
    Result bodies, and replace divergent rep bodies with `\\sM\\`."""
    out: list[str] = []
    n = len(fi_lines)
    k = 0
    while k < n:
        ln = fi_lines[k]
        m_r = re.match(r'^(\s*)Result\s+(\S+)\s*$', ln)
        if not m_r:
            out.append(ln)
            k += 1
            continue
        indent = m_r.group(1)
        code = m_r.group(2)
        # Find matching `{` ... `}`.
        depth = 0
        opened = False
        j = k
        while j < n:
            content = re.sub(r'"[^"]*"', '', fi_lines[j])
            for ch in content:
                if ch == '{':
                    depth += 1
                    opened = True
                elif ch == '}':
                    depth -= 1
            if opened and depth == 0:
                break
            j += 1
        if not opened:
            out.append(ln)
            k += 1
            continue
        # body lines: between the `{` line and the `}` line (exclusive).
        body_start = k + 1
        if body_start < n and fi_lines[body_start].strip() == '{':
            body_start += 1
        body_end = j - 1
        if body_end >= 0 and fi_lines[body_end].strip() == '}':
            body_end -= 1
        rep_body_lines = fi_lines[body_start:body_end + 1]
        # Gather per-member body content.
        per_member_body: dict[str, str] = {}
        all_present = True
        for mb in members:
            parsed = parsed_by_member.get(mb['name'], {})
            # Member's literal flowitem name = rep_fi_name with rep_token
            # replaced by member's token.
            if rep_token:
                mem_fi_name = rep_fi_name.replace(rep_token, mb['token'])
            else:
                mem_fi_name = rep_fi_name
            fi_results = parsed.get(mem_fi_name)
            if fi_results is None or code not in fi_results:
                all_present = False
                break
            mem_body_lines = fi_results[code]
            per_member_body[mb['name']] = ''.join(mem_body_lines)
        if not all_present:
            # Shape mismatch — leave verbatim.
            out.extend(fi_lines[k:j + 1])
            k = j + 1
            continue
        # Extract the TERMINATOR line (last non-blank line) of each
        # member's body — typically `Return N;` or `GoTo <flow>;`.
        # Only the terminator is candidate for symbolization; all
        # preceding lines (Property, SetBin, IncrementCounters …) are
        # emitted verbatim from the rep body so the BP stays readable.
        def _terminator(text: str) -> tuple[str, str]:
            """Return (stripped_terminator, leading_indent)."""
            lines = text.splitlines()
            for ln_ in reversed(lines):
                if ln_.strip():
                    stripped = ln_.lstrip()
                    indent_ = ln_[:len(ln_) - len(stripped)]
                    return stripped, indent_
            return '', ''

        canon_terms: dict[str, str] = {}
        for mb in members:
            tok = mb['token']
            text = per_member_body[mb['name']]
            term, _ind = _terminator(text)
            if tok and tok != rep_token:
                term = term.replace(tok, rep_token)
            canon_terms[mb['name']] = term
        if len(set(canon_terms.values())) <= 1:
            # Terminator agrees across members — leave verbatim.
            out.extend(fi_lines[k:j + 1])
            k = j + 1
            continue
        # Divergent terminator: allocate a symbol keyed by the
        # position-ordered tuple of canonical terminators so identical
        # divergence patterns share a single symbol across FlowItems /
        # Results / families.
        ordered_names = sorted(canon_terms.keys())
        body_key = tuple(canon_terms[mn] for mn in ordered_names)
        sym = body_to_sym.get(body_key)
        if sym is None:
            sym = f"s{next_idx[0]}"
            next_idx[0] += 1
            body_to_sym[body_key] = sym
            body_symbols[sym] = dict(canon_terms)
        else:
            for mn, mv in canon_terms.items():
                body_symbols[sym].setdefault(mn, mv)
        # Emit Result line, opening `{` lines, all body lines EXCEPT the
        # last non-blank one, then the `\sN\` placeholder at that line's
        # indentation, then the closing `}`.
        out.append(fi_lines[k])
        for mid in range(k + 1, body_start):
            out.append(fi_lines[mid])
        # Locate the terminator line within rep_body_lines.
        term_local_idx = -1
        for li in range(len(rep_body_lines) - 1, -1, -1):
            if rep_body_lines[li].strip():
                term_local_idx = li
                break
        if term_local_idx < 0:
            # No content — fall back to verbatim.
            out.extend(rep_body_lines)
        else:
            for li, line_text in enumerate(rep_body_lines):
                if li == term_local_idx:
                    line_stripped = line_text.lstrip()
                    line_indent = line_text[:len(line_text) -
                                            len(line_stripped)]
                    out.append(f"{line_indent}\\{sym}\\\n")
                else:
                    out.append(line_text)
        for tail in range(body_end + 1, j + 1):
            out.append(fi_lines[tail])
        k = j + 1
    return out


def write_symbols_csv(out_path: Path, table: list[dict],
                      body_symbols: dict | None = None) -> None:
    """Canonical schema: Symbol,<flow1>,<flow2>,...
    One row per UNIQUE symbol (dedup-aware: when build_symbol_table assigns
    the same `\\sN\\` to multiple groups, their per-member token cells are
    merged into a single row spanning the union of members).

    `body_symbols` (optional) holds the divergent-Result-body symbols
    allocated by `symbolize_divergent_results()`. Each entry is
    `{symbol_name: {member_name: body_text, ...}}`. These rows are appended
    after the name-symbol rows. Cells are multi-line; csv.writer quotes
    them automatically."""
    all_members = sorted({m for e in table for m in e['members']})
    # Merge entries by symbol -> {member: token}
    merged: dict[str, dict[str, str]] = {}
    sym_order: list[str] = []
    for e in table:
        sym = e['symbol']
        if sym not in merged:
            merged[sym] = {}
            sym_order.append(sym)
        for m, t in e['token_for'].items():
            merged[sym][m] = t
    # Union body-symbol members into all_members so columns line up.
    if body_symbols:
        extra_members = set()
        for per_member in body_symbols.values():
            extra_members.update(per_member.keys())
        all_members = sorted(set(all_members) | extra_members)
    with out_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Symbol'] + all_members)
        for sym in sym_order:
            row = [f"\\{sym}\\"]
            tok_for = merged[sym]
            for m in all_members:
                row.append(tok_for.get(m, ''))
            w.writerow(row)
        if body_symbols:
            # Sort by numeric symbol index so output is deterministic.
            def _idx(s: str) -> int:
                m = re.match(r's(\d+)', s)
                return int(m.group(1)) if m else 0
            for sym in sorted(body_symbols.keys(), key=_idx):
                per_member = body_symbols[sym]
                row = [f"\\{sym}\\"]
                for m in all_members:
                    row.append(per_member.get(m, ''))
                w.writerow(row)


def write_flows_compare_csv(out_path: Path, table: list[dict],
                            flow_items: dict[str, list[str]]) -> None:
    """Minimal compare-style: one row per group with Symbolized + per-member
    symbol values. (Full per-FlowItem rows would require running compare_v3,
    which is out of scope for this auto tool.)"""
    all_members = sorted({m for e in table for m in e['members']})
    header = (['Entity'] + all_members + ['DIFF'] +
              [f"{m}_line" for m in all_members] +
              ['Symbolized'] +
              [f"{m}_symbols" for m in all_members])
    with out_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        for e in table:
            row = [f"<flow:{e['orig_template']}>"]
            for m in all_members:
                row.append(m if m in e['members'] else '')
            row.append('OK' if float(e['ok_ratio']) == 1.0 else 'DIFF')
            for m in all_members:
                row.append('')  # line numbers omitted in minimal output
            row.append(e['template_name'])
            for m in all_members:
                if m in e['members']:
                    row.append(f"{e['symbol']}={e['token_for'][m]}")
                else:
                    row.append('')
            w.writerow(row)


def main(module_dir: str) -> int:
    md = Path(module_dir).resolve()
    module = md.name
    src = md / f"{module}_orig.mtpl"
    if not src.exists():
        src = md / f"{module}.mtpl"
    if not src.exists():
        print(f"[ERR] no mtpl in {md}")
        return 2
    cands = md / f"{module}_collapse_candidates.csv"
    if not cands.exists():
        print(f"[ERR] missing {cands} (run recommend_collapse.py first)")
        return 2

    lines = src.read_text(encoding='utf-8', errors='replace').splitlines(keepends=True)
    if not lines or not lines[-1].endswith('\n'):
        # Normalize: re-read without keepends and rebuild
        pass

    print(f"[scan] {src}  ({len(lines)} lines)")
    flows = find_flow_blocks([l.rstrip('\n') for l in lines])
    flow_items: dict[str, list[str]] = {}
    for n, s, e in flows:
        flow_items[n] = [it[0] for it in flowitems_in([l.rstrip('\n') for l in lines], s, e)]

    groups = load_groups(cands)
    if not groups:
        print("[info] no Independent groups; nothing to collapse")
        return 0
    print(f"[plan] independent groups to collapse: {len(groups)}")

    table = build_symbol_table(groups)
    member_idx = build_member_index(table)

    write_collapsed_flows_md(md / f"{module}_auto_collapsed.md", module, table)
    print(f"[out] {md / (module + '_auto_collapsed.md')}")

    # Save the ORIGINAL Flow bodies for every group member (rep + non-reps)
    # so the auto-expander can restore them verbatim.
    flow_def_blocks = _find_flow_def_blocks(lines)
    flow_def_idx = {nm: (s, e) for nm, s, e in flow_def_blocks}
    member_bodies: list[dict] = []
    for entry in table:
        for m in entry['members']:
            if m in flow_def_idx:
                s, e = flow_def_idx[m]
                member_bodies.append({
                    'name': m,
                    'symbol': entry['symbol'],
                    'token': entry['token_for'][m],
                    'is_rep': '1' if m == entry['rep'] else '0',
                    'body': ''.join(lines[s:e + 1]),
                })
    if member_bodies:
        out_mb = md / f"{module}_auto_group_flows.csv"
        with out_mb.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Name', 'Symbol', 'Token', 'IsRep', 'Body'])
            for r in member_bodies:
                w.writerow([r['name'], r['symbol'], r['token'],
                            r['is_rep'], r['body']])
        print(f"[out] {out_mb}  ({len(member_bodies)} group member flows)")

    new_lines = emit_auto_bp(lines, flows, table, member_idx)

    # Snapshot: any non-group, non-symbolized top-level Flow whose body in the
    # new BP differs from its original body. We need these so the auto-expander
    # can restore the original body (because cross-group ref rewrites in those
    # blocks would otherwise leave dangling refs to symbolized template names
    # after expansion).
    member_names = {m for e in table for m in e['members']}
    orig_flow_blocks = _find_flow_def_blocks(lines)
    new_flow_blocks = _find_flow_def_blocks(new_lines)
    orig_flow_idx = {nm: (s, e) for nm, s, e in orig_flow_blocks}
    new_flow_idx = {nm: (s, e) for nm, s, e in new_flow_blocks}
    modified_flows: list[dict] = []
    for nm in new_flow_idx:
        if nm in member_names:
            continue  # group rep flows are handled by group_flows.csv
        if '\\s' in nm and nm.endswith('\\'):
            continue  # symbolized template names
        if nm not in orig_flow_idx:
            continue
        ns, ne = new_flow_idx[nm]
        os_, oe = orig_flow_idx[nm]
        new_body = ''.join(new_lines[ns:ne + 1])
        orig_body = ''.join(lines[os_:oe + 1])
        if new_body != orig_body:
            modified_flows.append({'name': nm, 'body': orig_body})
    if modified_flows:
        out_mf = md / f"{module}_auto_modified_flows.csv"
        with out_mf.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Name', 'Body'])
            for r in modified_flows:
                w.writerow([r['name'], r['body']])
        print(f"[out] {out_mf}  ({len(modified_flows)} modified non-group flows)")

    # Compute test-name renames (symbolize tests inside collapsed rep flows).
    renames = compute_test_renames(table, lines, flows)
    if renames:
        # Snapshot rep test defs BEFORE renaming (so expander can restore
        # them under their original names).
        rep_test_snaps = _snapshot_test_defs(new_lines, set(renames.keys()))
        # Snapshot rep sub-Flow defs that are in renames (e.g. helper flows
        # like L2_C6_M0_VMINREP_COMP) so expander can restore them.
        rep_subflow_snaps: list[dict] = []
        for nm, s, e in _find_flow_def_blocks(new_lines):
            if nm in renames:
                rep_subflow_snaps.append({'name': nm,
                                          'body': ''.join(new_lines[s:e + 1])})
        # Snapshot the ORIGINAL Counters block (to restore at expansion).
        orig_counters = _find_counters_block(lines)
        if orig_counters:
            os_, oe = orig_counters
            cnt_body = ''.join(lines[os_:oe + 1])
            (md / f"{module}_auto_counters.csv").write_text(
                cnt_body, encoding='utf-8')
        rep_template_names = {e['template_name'] for e in table}
        new_lines = apply_test_renames(new_lines, renames, rep_template_names)
        print(f"[rename] symbolized {len(renames)} test/sub-flow name(s)")
    else:
        rep_test_snaps = []
        rep_subflow_snaps = []

    keep = {e['template_name'] for e in table}
    new_lines, dropped_tests, dropped_flows = drop_orphan_tests(
        new_lines, lines, keep)
    # Append snapshotted rep test defs so expansion restores them under
    # their original names (drop_orphan_tests cannot capture them because
    # they've been renamed to symbolized form in new_lines).
    if rep_test_snaps:
        dropped_tests.extend(rep_test_snaps)
        print(f"[snap] preserved {len(rep_test_snaps)} rep test def(s) "
              f"for expansion")
    if rep_subflow_snaps:
        dropped_flows.extend(rep_subflow_snaps)
        print(f"[snap] preserved {len(rep_subflow_snaps)} rep sub-flow "
              f"def(s) for expansion")
    if dropped_tests:
        print(f"[trim] dropped {len(dropped_tests)} orphan Test definitions")
        write_tests_bank_csv(md / f"{module}_auto_tests.csv", dropped_tests)
    if dropped_flows:
        print(f"[trim] dropped {len(dropped_flows)} orphan Flow definitions")
        write_tests_bank_csv(md / f"{module}_auto_flows.csv", dropped_flows)

    # Post-pass: symbolize divergent Result bodies inside each rep Flow
    # block so the BP file makes per-port divergence (e.g. UV/OV `Return 0`
    # vs `Return 2` on R2/R4) inline-visible. Allocates fresh `\sM\`
    # numbers above all name-symbol numbers; the per-member body text is
    # written to `_auto_symbols.csv` as multi-line CSV cells. The expander
    # is unaffected (it restores all member bodies verbatim from the
    # group-flows bank).
    body_symbols: dict[str, dict[str, str]] = {}
    if member_bodies:
        new_lines, body_symbols = symbolize_divergent_results(
            new_lines, table, member_bodies)
        if body_symbols:
            print(f"[bp-post] symbolized {len(body_symbols)} divergent "
                  f"Result body(ies) inline")

    out_bp = md / f"{module}_auto_bp.mtpl"
    out_bp.write_text(''.join(new_lines), encoding='utf-8')
    print(f"[out] {out_bp}  ({len(new_lines)} lines, "
          f"saved {len(lines) - len(new_lines)} = "
          f"{(1 - len(new_lines)/len(lines))*100:.1f}%)")

    out_sym = md / f"{module}_auto_symbols.csv"
    write_symbols_csv(out_sym, table, body_symbols)
    print(f"[out] {out_sym}  ({len(table)} name-symbol(s) + "
          f"{len(body_symbols)} body-symbol(s))")

    out_cmp = md / f"{module}_auto_flows_compare.csv"
    write_flows_compare_csv(out_cmp, table, flow_items)
    print(f"[out] {out_cmp}")
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: auto_bp_from_groups.py <module_dir>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
