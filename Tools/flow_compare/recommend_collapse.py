"""recommend_collapse.py — identify candidate flow groups for BP collapse.

Scans a module .mtpl, groups top-level `Flow` definitions that differ by
exactly one underscore-token (e.g. F1/F2/F3, M0/M1/M2/M3, MIN/MAX), measures
their structural similarity, computes hierarchy depth from inter-flow
references, and writes a ranked CSV of candidate groups.

Usage:
    python recommend_collapse.py <module_dir>
        e.g. ..\..\Modules\ARR\ARR_ATOM_CXX

Output:
    <module_dir>/<module>_collapse_candidates.csv
"""
from __future__ import annotations
import csv
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

RE_FLOW_DEF = re.compile(r'^\s*(?:Flow|DUTFlow)\s+(\S+)')
RE_FLOWITEM = re.compile(r'^\s*(?:FlowItem|DUTFlowItem)\s+(\S+)\s+(\S+)')


def find_flow_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """Return list of (flow_name, body_start_idx, body_end_idx) — 0-based,
    body excludes the opening line. End is exclusive (line of matching '}')."""
    flows = []
    i = 0
    n = len(lines)
    while i < n:
        m = RE_FLOW_DEF.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group(1).rstrip('{').strip()
        # Find the opening brace (same line or following lines)
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
            flows.append((name, i + 1, j))
            i = j + 1
        else:
            i += 1
    return flows


def _strip_quotes(s: str) -> str:
    return re.sub(r'"[^"]*"', '', s)


def flowitems_in(lines: list[str], start: int, end: int) -> list[tuple[str, int]]:
    """Return list of (flowitem_name, line_no_1based) for FlowItems inside body."""
    items = []
    for i in range(start, end):
        m = RE_FLOWITEM.match(lines[i])
        if m:
            items.append((m.group(1), i + 1))
    return items


def diff_token_index(names: list[str]) -> int | None:
    """If all names split by '_' have the same number of tokens and differ in
    exactly one position, return that index; else None."""
    parts = [n.split('_') for n in names]
    if len(set(len(p) for p in parts)) != 1:
        return None
    L = len(parts[0])
    diff_positions = [k for k in range(L) if len({p[k] for p in parts}) > 1]
    if len(diff_positions) == 1:
        return diff_positions[0]
    return None


def template_for(name: str, idx: int, placeholder: str = '<X>') -> str:
    parts = name.split('_')
    parts[idx] = placeholder
    return '_'.join(parts)


def _common_affix(values: list[str]) -> tuple[str, str]:
    """Return (longest common prefix, longest common suffix) across values."""
    if not values:
        return '', ''
    pre = values[0]
    for v in values[1:]:
        i = 0
        while i < len(pre) and i < len(v) and pre[i] == v[i]:
            i += 1
        pre = pre[:i]
    suf = values[0]
    for v in values[1:]:
        i = 0
        while i < len(suf) and i < len(v) and suf[-1 - i] == v[-1 - i]:
            i += 1
        suf = suf[len(suf) - i:] if i else ''
    return pre, suf


def symbolize_item(item: str, this_value: str, all_values: list[str]) -> str:
    """Replace occurrences of `this_value` (and any cross-token "core" share)
    in `item` with <X>.

    The diff tokens often share a prefix/suffix (e.g. F1/F2/F3 share '' / '';
    F1XAT/F2XAT/F3XAT share 'F'/'XAT'; M0/M1/M2/M3 share 'M'/''). We replace
    occurrences of the full token AND occurrences of just the varying core
    (digit/letters between the common affixes) when surrounded by the same
    affixes, so embedded forms also collapse.
    """
    pre, suf = _common_affix(all_values)
    cores = [v[len(pre):len(v) - len(suf) if suf else len(v)] for v in all_values]
    this_core = this_value[len(pre):len(this_value) - len(suf) if suf else len(this_value)]
    out = item
    # 1) Replace the full token with <X> (word-bounded)
    out = re.sub(rf'(?<![A-Za-z0-9]){re.escape(this_value)}(?![A-Za-z0-9])',
                 '<X>', out)
    # 2) Cores often appear embedded with only one of (pre,suf) attached.
    #    Replace `pre+core` (word-left, then `pre` consumes the inner boundary)
    #    and `core+suf` (word-right) variants. This handles e.g. token
    #    F1XAT (pre=F, suf=XAT, core=1) embedded as `_F1_` in items.
    if this_core and all(c.isdigit() or (len(c) <= 2 and c.isalnum()) for c in cores):
        if pre:
            out = re.sub(
                rf'(?<![A-Za-z0-9]){re.escape(pre + this_core)}(?![A-Za-z0-9])',
                pre + '<X>', out)
        if suf:
            out = re.sub(
                rf'(?<![A-Za-z0-9]){re.escape(this_core + suf)}(?![A-Za-z0-9])',
                '<X>' + suf, out)
        # 3) Standalone bare core (no affix attached)
        out = re.sub(rf'(?<![A-Za-z0-9]){re.escape(this_core)}(?![A-Za-z0-9])',
                     '<X>', out)
    return out


def similarity(group_items: dict[str, list[str]],
               token_values: dict[str, str]) -> tuple[float, int, int]:
    """Return (ok_ratio, ok_count, total_count).

    Aligns FlowItems by position. An item is OK if symbolizing the differing
    token in each flow's items yields the same string across all flows at that
    position. Length mismatch counted as misalignment for the tail."""
    flows = list(group_items.keys())
    item_lists = [group_items[f] for f in flows]
    max_len = max(len(lst) for lst in item_lists)
    min_len = min(len(lst) for lst in item_lists)
    all_values = list({token_values[f] for f in flows})
    ok = 0
    for i in range(min_len):
        symbolized = set()
        for f in flows:
            symbolized.add(symbolize_item(group_items[f][i],
                                          token_values[f], all_values))
        if len(symbolized) == 1:
            ok += 1
    return (ok / max_len if max_len else 0.0, ok, max_len)


def build_call_graph(flows: list[tuple[str, int, int]],
                     lines: list[str]) -> dict[str, set[str]]:
    """Edge name -> set of called sub-flow names (only flows that exist in
    this module's flow-name set)."""
    flow_names = {n for n, _, _ in flows}
    graph = defaultdict(set)
    for name, s, e in flows:
        for i in range(s, e):
            m = RE_FLOWITEM.match(lines[i])
            if not m:
                continue
            ref = m.group(2)
            # Strip module-qualified prefix, take last segment after '.'
            tail = ref.split('::')[-1]
            head = tail.split('.')[0]
            if head in flow_names and head != name:
                graph[name].add(head)
    return graph


def hierarchy_depth(name: str,
                    graph: dict[str, set[str]],
                    memo: dict[str, int]) -> int:
    """Max depth of sub-flow chain rooted at `name` (leaves = 0). Detects
    cycles by treating revisits as 0."""
    if name in memo:
        return memo[name]
    memo[name] = 0  # cycle guard
    children = graph.get(name, set())
    d = 0 if not children else 1 + max(hierarchy_depth(c, graph, memo) for c in children)
    memo[name] = d
    return d


def in_degree(graph: dict[str, set[str]], all_names: set[str]) -> dict[str, int]:
    """How many other flows reference this flow."""
    deg = {n: 0 for n in all_names}
    for parent, kids in graph.items():
        for k in kids:
            if k in deg:
                deg[k] += 1
    return deg


def _shape(s: str) -> str:
    """Canonical shape: digits->D, lowercase->a, uppercase->A, other->kept."""
    out = []
    for ch in s:
        if ch.isdigit():
            out.append('D')
        elif ch.isupper():
            out.append('A')
        elif ch.islower():
            out.append('a')
        else:
            out.append(ch)
    return ''.join(out)


def cluster_token_values(values: list[str]) -> list[list[str]]:
    """Cluster token values into subsets sharing the same canonical shape.
    Singleton clusters are dropped."""
    buckets: dict[str, list[str]] = defaultdict(list)
    for v in values:
        buckets[_shape(v)].append(v)
    return [sorted(b) for b in buckets.values() if len(b) >= 2]


def main(module_dir: str, ok_thresh: float = 0.70,
         size_thresh: int = 2) -> int:
    md = Path(module_dir).resolve()
    if not md.is_dir():
        print(f"[ERR] not a directory: {md}")
        return 2
    module = md.name
    # Prefer _orig.mtpl (clean snapshot) if present, else <module>.mtpl
    src = md / f"{module}_orig.mtpl"
    if not src.exists():
        src = md / f"{module}.mtpl"
    if not src.exists():
        print(f"[ERR] mtpl not found in {md}")
        return 2
    print(f"[scan] {src}")
    lines = src.read_text(encoding='utf-8', errors='replace').splitlines()
    flows = find_flow_blocks(lines)
    print(f"[scan] flow definitions: {len(flows)}")

    # Per-flow FlowItem list (just names, in order)
    flow_items: dict[str, list[str]] = {}
    flow_first_line: dict[str, int] = {}
    for name, s, e in flows:
        items = flowitems_in(lines, s, e)
        flow_items[name] = [it[0] for it in items]
        flow_first_line[name] = s  # body start

    # Build call graph (intra-module flow->subflow edges)
    graph = build_call_graph(flows, lines)
    depth_memo: dict[str, int] = {}
    depths = {n: hierarchy_depth(n, graph, depth_memo) for n, _, _ in flows}
    indeg = in_degree(graph, set(flow_items.keys()))

    # Group by single-token-diff template, then sub-cluster by token shape.
    candidate_groups: list[tuple[str, int, list[str]]] = []
    by_len: dict[int, list[str]] = defaultdict(list)
    for n in flow_items:
        by_len[len(n.split('_'))].append(n)

    seen_keys: set[tuple[str, int, tuple[str, ...]]] = set()
    for L, names in by_len.items():
        for pos in range(L):
            tmpl_buckets: dict[str, list[str]] = defaultdict(list)
            for n in names:
                parts = n.split('_')
                key = '_'.join(parts[:pos] + ['<X>'] + parts[pos + 1:])
                tmpl_buckets[key].append(n)
            for tmpl, group in tmpl_buckets.items():
                if len(group) < 2:
                    continue
                # Sub-cluster by token-value shape so heterogeneous buckets
                # (e.g. INIT/F1XAT/BEGINCPUNOM) split into homogeneous subsets
                # (e.g. {F1XAT,F2XAT,F3XAT,F4XAT,F5XAT}).
                tok_for = {n: n.split('_')[pos] for n in group}
                clusters = cluster_token_values(list(tok_for.values()))
                # Always include the full bucket as one candidate too (covers
                # cases where shape clustering would over-split a clean group).
                full_vals = sorted({tok_for[n] for n in group})
                if full_vals not in clusters:
                    clusters.append(full_vals)
                for cluster_vals in clusters:
                    cv_set = set(cluster_vals)
                    base_sub = sorted([n for n in group if tok_for[n] in cv_set])
                    # Further sub-cluster by FlowItem count: flows with very
                    # different item counts cannot fully collapse together.
                    by_count: dict[int, list[str]] = defaultdict(list)
                    for n in base_sub:
                        by_count[len(flow_items[n])].append(n)
                    # Emit (a) the full cluster, (b) each same-count subset of
                    # size >=2 (so the recommender surfaces both maximal and
                    # high-quality subsets).
                    sub_variants = [base_sub]
                    for cnt, members in by_count.items():
                        if len(members) >= 2 and len(members) < len(base_sub):
                            sub_variants.append(sorted(members))
                    for sub_group in sub_variants:
                        if len(sub_group) < 2:
                            continue
                        token_vals_t = tuple(sorted({tok_for[n] for n in sub_group}))
                        k = (tmpl, pos, token_vals_t)
                        if k in seen_keys:
                            continue
                        seen_keys.add(k)
                        candidate_groups.append((tmpl, pos, sub_group))

    # Score candidates
    rows = []
    for tmpl, pos, group in candidate_groups:
        token_vals = {n: n.split('_')[pos] for n in group}
        items_map = {n: flow_items[n] for n in group}
        # Skip empty-bodied groups (no FlowItems at all)
        if all(len(v) == 0 for v in items_map.values()):
            continue
        ok_ratio, ok_n, tot_n = similarity(items_map, token_vals)
        max_depth = max(depths[n] for n in group)
        max_indeg = max(indeg.get(n, 0) for n in group)
        sizes = [len(items_map[n]) for n in group]
        # "Top-level-ness": prefer groups whose members are NOT referenced by
        # any flow in the group themselves (i.e. true entry points within the
        # subset). Also prefer high depth + low indeg from outside group.
        rows.append({
            'Template': tmpl,
            'DiffTokenPos': pos,
            'GroupSize': len(group),
            'Members': '; '.join(group),
            'TokenValues': '; '.join(sorted({token_vals[n] for n in group})),
            'FlowItemsMin': min(sizes),
            'FlowItemsMax': max(sizes),
            'OK_Items': ok_n,
            'Total_Items': tot_n,
            'OK_Ratio': round(ok_ratio, 4),
            'EntryPoint': 1 if all(indeg.get(n, 0) == 0 for n in group) else 0,
            'MaxDepth': max_depth,
            'MaxInDegree': max_indeg,
            'FirstLines': '; '.join(str(flow_first_line[n]) for n in group),
        })

    # Rank: entry-point groups first (top of hierarchy), then deeper call
    # chains, then bigger groups, then better similarity, then more items.
    rows.sort(key=lambda r: (-r['EntryPoint'], -r['MaxDepth'],
                             -r['GroupSize'], -r['OK_Ratio'],
                             -r['Total_Items']))

    # Independence post-filter: precompute transitive descendants for every
    # flow, then greedily accept groups in priority order. A group is
    # Independent if none of its members lies in the descendant-closure of an
    # already-accepted group. Only groups passing the recommendation
    # thresholds participate (low-quality high-priority groups must not
    # block deeper, useful candidates).
    descendants_memo: dict[str, set[str]] = {}

    def descendants(name: str) -> set[str]:
        if name in descendants_memo:
            return descendants_memo[name]
        # cycle guard
        descendants_memo[name] = set()
        acc: set[str] = set()
        for c in graph.get(name, set()):
            acc.add(c)
            acc |= descendants(c)
        descendants_memo[name] = acc
        return acc

    THRESH_OK = ok_thresh
    THRESH_SIZE = size_thresh
    blocked: set[str] = set()
    for r in rows:
        members = r['Members'].split('; ')
        eligible = (r['OK_Ratio'] >= THRESH_OK
                    and r['GroupSize'] >= THRESH_SIZE)
        if not eligible:
            r['Independent'] = 0
            continue
        # Conflict if any member is a descendant of an already-accepted group
        # (i.e. lies in `blocked`), OR any accepted member lies under this
        # group (would mean we picked a child before its parent — shouldn't
        # happen due to depth-desc sort, but check to be safe).
        if any(m in blocked for m in members):
            r['Independent'] = 0
            continue
        r['Independent'] = 1
        # Block this group's members AND all their transitive descendants.
        for m in members:
            blocked.add(m)
            blocked |= descendants(m)

    out = md / f"{module}_collapse_candidates.csv"
    if rows:
        with out.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"[out] {out}  ({len(rows)} candidate groups)")
    else:
        print("[out] no candidate groups found")
        return 0

    # Console: top recommendations meeting threshold
    print()
    print("=" * 90)
    print(f"Top recommendations  (OK_Ratio >= {THRESH_OK}, GroupSize >= {THRESH_SIZE})")
    print("=" * 90)
    print(f"{'EP':>2} {'Depth':>5} {'Sz':>3} {'OK%':>5} {'Items':>6}  Template")
    print('-' * 90)
    shown = 0
    for r in rows:
        if r['OK_Ratio'] < THRESH_OK or r['GroupSize'] < THRESH_SIZE:
            continue
        print(f"{r['EntryPoint']:>2} {r['MaxDepth']:>5} {r['GroupSize']:>3} "
              f"{r['OK_Ratio']*100:>4.0f}% {r['Total_Items']:>6}  "
              f"{r['Template']}")
        print(f"        members: {r['Members']}")
        shown += 1
        if shown >= 25:
            print("  ... (truncated, see CSV for full list)")
            break
    if shown == 0:
        print("  (no group passed threshold)")
    return 0


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('module_dir')
    ap.add_argument('--ok-thresh', type=float, default=0.70,
                    help='Minimum OK_Ratio for Independent=1 (default 0.70)')
    ap.add_argument('--size-thresh', type=int, default=2,
                    help='Minimum GroupSize for Independent=1 (default 2)')
    args = ap.parse_args()
    sys.exit(main(args.module_dir, ok_thresh=args.ok_thresh,
                  size_thresh=args.size_thresh))
