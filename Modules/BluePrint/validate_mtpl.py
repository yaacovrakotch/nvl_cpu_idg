"""MTPL file structural validator.

Checks:
1. Balanced curly braces { }
2. FlowItems referencing non-existent Tests/Flows
3. Tests/Flows with no corresponding FlowItem
4. Unmatched backslash (template variable) pairs
5. Port (Result block) termination rules
6. Missing semicolons on statement lines
"""

import argparse
import re
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_comments(line: str) -> str:
    """Strip inline comments from a line.

    - ``##EDC##`` directives are kept (prefix removed, content retained).
    - A bare ``#`` starts an inline comment; everything from it onward is removed.
    - ``#`` inside a quoted string is **not** treated as a comment.
    """
    edc_match = re.match(r'^(\s*)##\w+##\s*', line)
    if edc_match:
        return line[:edc_match.start()] + line[edc_match.end():]

    in_quote = False
    for i, ch in enumerate(line):
        if ch == '"' and (i == 0 or line[i - 1] != '\\'):
            in_quote = not in_quote
        elif ch == '#' and not in_quote:
            return line[:i]
    return line


def strip_quotes(line: str) -> str:
    """Remove content inside double-quoted strings (for brace counting)."""
    return re.sub(r'"[^"]*"', '', line)


# ---------------------------------------------------------------------------
# Check 1
# ---------------------------------------------------------------------------

def check_braces(lines):
    issues = []
    depth = 0
    open_stack = []

    for idx, raw_line in enumerate(lines, start=1):
        line = strip_quotes(raw_line)
        stripped = line.lstrip()
        if stripped.startswith('#') and not stripped.startswith('##'):
            continue
        for ch in line:
            if ch == '{':
                depth += 1
                open_stack.append(idx)
            elif ch == '}':
                if depth <= 0:
                    issues.append(f"  Line {idx}: Closing '}}' with no matching opening '{{'")
                else:
                    depth -= 1
                    open_stack.pop()

    if depth > 0:
        for ln in open_stack:
            issues.append(f"  Line {ln}: Opening '{{' never closed")
    return issues


# ---------------------------------------------------------------------------
# Check 2 & 3
# ---------------------------------------------------------------------------

RE_FLOWITEM = re.compile(
    r'^\s*(?:FlowItem|DUTFlowItem)\s+(\S+)\s+(\S+)')
RE_TEST = re.compile(
    r'^\s*(?:Test|CSharpTest)\s+\S+\s+(\S+)')
RE_MULTITRIAL = re.compile(
    r'^\s*MultiTrialTest\s+(\S+)')
RE_TRIALTEST = re.compile(
    r'^\s*(?:TrialTest|CSharpTrialTest)\s+\S+\s+"([^"]+)"')
RE_FLOW = re.compile(
    r'^\s*(?:Flow|DUTFlow)\s+(\S+)')


def _collect_definitions(lines):
    tests = {}
    flows = {}
    flowitems = []

    for idx, raw_line in enumerate(lines, start=1):
        line = strip_comments(raw_line).rstrip()
        if not line.strip():
            continue

        m = RE_FLOWITEM.match(line)
        if m:
            fi_name = m.group(1)
            test_ref = m.group(2)
            is_placeholder = '#PlaceHolder' in raw_line or '#Placeholder' in raw_line
            flowitems.append((idx, fi_name, test_ref, is_placeholder))
            continue

        m = RE_TEST.match(line)
        if m:
            tests[m.group(1)] = idx
            continue

        m = RE_MULTITRIAL.match(line)
        if m:
            tests[m.group(1)] = idx
            continue

        m = RE_TRIALTEST.match(line)
        if m:
            tests[m.group(1)] = idx
            continue

        m = RE_FLOW.match(line)
        if m:
            flow_name = m.group(1)
            if RE_FLOWITEM.match(line):
                continue
            at_idx = flow_name.find('@')
            if at_idx != -1:
                flow_name = flow_name[:at_idx].rstrip()
            flows[flow_name] = idx
            continue

    return tests, flows, flowitems


def check_flowitems_have_definitions(lines):
    tests, flows, flowitems = _collect_definitions(lines)
    all_defs = set(tests.keys()) | set(flows.keys())
    issues = []
    for line_num, fi_name, test_ref, is_placeholder in flowitems:
        if is_placeholder:
            continue
        clean_ref = test_ref.split('@')[0].rstrip()
        if clean_ref not in all_defs:
            issues.append(
                f"  Line {line_num}: FlowItem '{fi_name}' references "
                f"'{clean_ref}' which has no matching Test or Flow definition")
    return issues


def check_definitions_have_flowitems(lines):
    tests, flows, flowitems = _collect_definitions(lines)
    referenced = set()
    for _, _, test_ref, _ in flowitems:
        clean_ref = test_ref.split('@')[0].rstrip()
        referenced.add(clean_ref)

    issues = []
    for name, line_num in tests.items():
        if name not in referenced:
            issues.append(
                f"  Line {line_num}: Test '{name}' has no FlowItem referencing it")
    for name, line_num in flows.items():
        if name not in referenced:
            issues.append(
                f"  Line {line_num}: Flow '{name}' has no FlowItem referencing it")
    return issues


# ---------------------------------------------------------------------------
# Check 4
# ---------------------------------------------------------------------------

def check_backslash_pairing(lines):
    issues = []
    for idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.lstrip()
        if stripped.startswith('#') and not stripped.startswith('##'):
            continue
        content = strip_comments(raw_line)
        count = content.count('\\')
        if count % 2 != 0:
            issues.append(
                f"  Line {idx}: Odd number of backslashes ({count}): "
                f"{raw_line.rstrip()}")
    return issues


# ---------------------------------------------------------------------------
# Check 5
# ---------------------------------------------------------------------------

RE_RESULT = re.compile(r'^\s*Result\s+(-?\d+)')
RE_RETURN = re.compile(r'^\s*Return\s+', re.IGNORECASE)
RE_GOTO = re.compile(r'^\s*GoTo\s+', re.IGNORECASE)
RE_GOTO_NEXT = re.compile(r'^\s*GoTo\s+<NEXT>', re.IGNORECASE)
RE_GOTO_NEXT_OR_RETURN = re.compile(
    r'^\s*GoTo\s+<NEXT>\s+or\s+Return\s+', re.IGNORECASE)
RE_CHAINBY = re.compile(r'^\s*ChainBy\s+', re.IGNORECASE)


def check_port_termination(lines):
    issues = []

    in_flowitem = False
    flowitem_name = ''
    brace_depth = 0
    fi_brace_depth = 0

    in_result = False
    result_num = ''
    result_line = 0
    result_brace_depth = 0

    has_return = False
    has_goto = False
    has_goto_next = False
    has_chainby = False
    has_goto_next_or_return = False

    for idx, raw_line in enumerate(lines, start=1):
        line = strip_comments(raw_line).rstrip()
        stripped = line.strip()

        content = strip_quotes(line)
        opens = content.count('{')
        closes = content.count('}')

        m_fi = RE_FLOWITEM.match(line)
        if m_fi and not in_flowitem:
            in_flowitem = True
            flowitem_name = m_fi.group(1)
            fi_brace_depth = brace_depth

        m_res = None
        if in_flowitem:
            m_res = RE_RESULT.match(stripped)
            if m_res and not in_result:
                in_result = True
                result_num = m_res.group(1)
                result_line = idx
                result_brace_depth = brace_depth
                has_return = False
                has_goto = False
                has_goto_next = False
                has_chainby = False
                has_goto_next_or_return = False

        brace_depth += opens - closes

        if in_result and not m_res:
            if RE_GOTO_NEXT_OR_RETURN.match(stripped):
                has_goto_next_or_return = True
            elif RE_GOTO_NEXT.match(stripped):
                has_goto_next = True
            elif RE_GOTO.match(stripped):
                has_goto = True
            elif RE_RETURN.match(stripped):
                has_return = True
            elif RE_CHAINBY.match(stripped):
                has_chainby = True

        if in_result and brace_depth <= result_brace_depth:
            terminated = (
                has_return
                or has_goto
                or has_goto_next_or_return
            )
            if not terminated:
                if has_goto_next or has_chainby:
                    issues.append(
                        f"  Line {result_line}: FlowItem '{flowitem_name}' "
                        f"Result {result_num} has only "
                        f"{'GoTo <NEXT>' if has_goto_next else 'ChainBy'} "
                        f"without a Return or GoTo target")
                else:
                    issues.append(
                        f"  Line {result_line}: FlowItem '{flowitem_name}' "
                        f"Result {result_num} has no Return or GoTo")
            in_result = False

        if in_flowitem and brace_depth <= fi_brace_depth:
            in_flowitem = False

    return issues


# ---------------------------------------------------------------------------
# Check 6
# ---------------------------------------------------------------------------

RE_BLOCK_OPENER = re.compile(
    r'^\s*(?:Version|ProgramStyle|TestPlan|Counters|'
    r'(?:CSharpTest|Test|MultiTrialTest|TrialTest|CSharpTrialTest)\s|'
    r'(?:Flow|DUTFlow|FlowItem|DUTFlowItem)\s|'
    r'Result\s|'
    r'TrialVariable\s|TrialVariableExitAction\s|'
    r'TrialParam\s|TrialResult\s|TrialAction\s)')
RE_BRACE_ONLY = re.compile(r'^\s*[{}]\s*$')
RE_BLANK_OR_COMMENT = re.compile(r'^\s*$|^\s*#')
RE_COUNTER_ITEM = re.compile(r'^\s*[pn]\d+_')


def check_missing_semicolons(lines):
    issues = []
    depth = 0
    in_counters = False

    for idx, raw_line in enumerate(lines, start=1):
        stripped_raw = raw_line.strip()

        if stripped_raw == 'Counters' or stripped_raw.startswith('Counters'):
            in_counters = True
        if in_counters and stripped_raw == '}':
            in_counters = False

        content_for_depth = strip_quotes(raw_line)
        opens = content_for_depth.count('{')
        closes = content_for_depth.count('}')

        content = strip_comments(raw_line).rstrip()
        stripped = content.strip()

        if RE_BLANK_OR_COMMENT.match(stripped_raw):
            depth += opens - closes
            continue
        if RE_BRACE_ONLY.match(stripped):
            depth += opens - closes
            continue
        if RE_BLOCK_OPENER.match(stripped):
            depth += opens - closes
            continue
        if in_counters:
            depth += opens - closes
            continue

        if depth > 0 and stripped:
            if stripped.endswith('{') or stripped.endswith('}'):
                depth += opens - closes
                continue
            if not stripped.endswith(';'):
                issues.append(
                    f"  Line {idx}: Missing semicolon: {raw_line.rstrip()}")

        depth += opens - closes

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_mtpl(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    print(f"\n{'='*70}")
    print(f"Validating: {filepath}")
    print(f"{'='*70}")

    total_issues = 0

    checks = [
        ("Check 1: Brace matching", check_braces),
        ("Check 2: FlowItems with no matching Test/Flow",
         check_flowitems_have_definitions),
        ("Check 3: Tests/Flows with no matching FlowItem",
         check_definitions_have_flowitems),
        ("Check 4: Backslash pairing", check_backslash_pairing),
        ("Check 5: Port termination", check_port_termination),
        ("Check 6: Missing semicolons", check_missing_semicolons),
    ]

    for title, check_fn in checks:
        print(f"\n--- {title} ---")
        issues = check_fn(lines)
        if issues:
            total_issues += len(issues)
            for issue in issues:
                print(issue)
            print(f"  [{len(issues)} issue(s)]")
        else:
            print("  PASS")

    print(f"\n{'='*70}")
    print(f"Summary: {total_issues} issue(s) found in {filepath}")
    print(f"{'='*70}\n")
    return total_issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('filepath')
    args = ap.parse_args()
    total = validate_mtpl(args.filepath)
    sys.exit(1 if total > 0 else 0)


if __name__ == '__main__':
    main()
