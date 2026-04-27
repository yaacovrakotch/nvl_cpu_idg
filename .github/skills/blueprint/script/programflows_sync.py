from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


SERIAL_FLOW_TYPE = "SubFlow"
PARALLEL_FLOW_TYPE = "SubParFlow"
COMMON_PREFIX = "COMMON"

ACTIVE_DIELET_BY_REPO = {
    "nvl.cpu": "CPU",
    "nvl.gcd": "GCD",
    "nvl.hub": "HUB",
    "nvl.pcd": "PCD",
}

DIELET_FILE_INFO = {
    "CPU": {"programflows": "ProgramFlowsCPU.py", "ip_flows": "IPC_FLOWS.py", "ip_code": "CXX"},
    "GCD": {"programflows": "ProgramFlowsGCD.py", "ip_flows": "IPG_FLOWS.py", "ip_code": "GXX"},
    "HUB": {"programflows": "ProgramFlowsHUB.py", "ip_flows": "IPH_FLOWS.py", "ip_code": "HXX"},
    "PCD": {"programflows": "ProgramFlowsPCD.py", "ip_flows": "IPP_FLOWS.py", "ip_code": "PXX"},
}

FSTRING_TEMPLATE_RE = re.compile(
    r"(?P<name>\w+)\s*=\s*f'''(?P<body>.*?)'''",
    re.DOTALL,
)

PRL_DICT_RE = re.compile(
    r"(?P<prefix>prl_dict\s*=\s*\{\n)(?P<body>.*?)(?P<suffix>\})",
    re.DOTALL,
)


@dataclass
class FlowGroup:
    leader: str | None
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def detect_active_dielet(repo_root: Path) -> str | None:
    return ACTIVE_DIELET_BY_REPO.get(repo_root.name.lower())


def is_common_dielet_type(dielet_type: str) -> bool:
    return normalize_text(dielet_type).upper().startswith(COMMON_PREFIX)


def slot_value(slot: dict, field_name: str) -> str:
    payload = slot.get(field_name)
    if isinstance(payload, dict):
        return normalize_text(payload.get("value"))
    return normalize_text(payload)


def slot_matches_dielet(slot: dict, active_dielet: str) -> bool:
    dielet_type = slot_value(slot, "all_dielet_type").upper()
    if not dielet_type or is_common_dielet_type(dielet_type):
        return False
    return active_dielet in dielet_type


def slot_scope_family(slot: dict) -> str:
    return slot_value(slot, "all_scope").upper()


def slot_flow_type(slot: dict) -> str:
    return slot_value(slot, "all_flow_type")


def slot_tp_exec(slot: dict) -> str:
    return slot_value(slot, "tp_exec_flow").upper()


def slot_top_flow(slot: dict) -> str:
    return slot_value(slot, "top_flow").upper()


def slot_flow_name(slot: dict) -> str:
    return normalize_text(slot_value(slot, "all_flow"))


def slot_dielet_flow_name(slot: dict, active_dielet: str) -> str:
    field_name = {
        "CPU": "cpu_flow",
        "GCD": "gcd_flow",
        "HUB": "hub_flow",
        "PCD": "pcd_flow",
    }[active_dielet]
    dielet_flow = normalize_text(slot_value(slot, field_name))
    if dielet_flow:
        return dielet_flow
    return slot_flow_name(slot)


def subflow_symbol(flow_name: str) -> str:
    return f"{flow_name}_SubFlow"


def topflow_symbol(top_flow: str) -> str:
    return f"{top_flow}_TopFlow"


def repo_scope_includes(repo_scope: str, name: str) -> bool:
    if repo_scope == "both":
        return True
    return repo_scope == name


def unique_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def split_groups(body: str) -> list[FlowGroup]:
    groups: list[FlowGroup] = []
    current: list[str] = []
    current_leader: str | None = None
    pending_comments: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == "":
            if current:
                groups.append(FlowGroup(current_leader, current))
                current = []
                current_leader = None
            continue
        if stripped.startswith("#"):
            if current:
                current.append(line)
            else:
                pending_comments.append(line)
            continue

        leader = stripped.split()[0]
        if current and current_leader is not None and leader != current_leader:
            groups.append(FlowGroup(current_leader, current))
            current = pending_comments + [line]
            pending_comments = []
            current_leader = leader
            continue

        if not current:
            current = pending_comments + [line]
            pending_comments = []
            current_leader = leader
            continue

        current.append(line)
    if current:
        groups.append(FlowGroup(current_leader, current))
    return groups


def leader_token(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        return stripped.split()[0]
    return None


def render_groups(groups: list[FlowGroup]) -> str:
    if not groups:
        return "\n"
    return "\n" + "\n\n".join(group.text for group in groups) + "\n"


def get_executable_lines(group: FlowGroup) -> list[str]:
    executable_lines: list[str] = []
    for line in group.lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        executable_lines.append(stripped)
    return executable_lines


def is_single_line_placeholder(group: FlowGroup, scaffold_line: str) -> bool:
    return get_executable_lines(group) == [scaffold_line.strip()]


def parse_topflow_lines(group: FlowGroup) -> dict[str, str]:
    refs: dict[str, str] = {}
    for line in group.lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 3:
            continue
        refs[parts[1]] = " ".join(parts[2:])
    return refs


def format_topflow_line(topflow_name: str, reference: str, ports: str) -> str:
    return f"{topflow_name:<17} {reference:<32} {ports}"


def format_prl_dict_entry(flow_name: str) -> str:
    return f"            '{subflow_symbol(flow_name)}': '{flow_name}%s_SubFlow',"


def replace_fstring_body(text: str, var_name: str, new_body: str) -> str:
    pattern = re.compile(rf"({var_name}\s*=\s*f''')(?P<body>.*?)(?P<close>''')", re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Unable to find f-string body for {var_name}.")
    return text[:match.start("body")] + new_body + text[match.end("body"):]


def targeted_insert_group_after_anchor(
    raw_text: str, var_name: str, scaffold_lines: list[str], anchor_leader: str | None
) -> str:
    """Insert a new flow group into an f-string body without re-rendering any other content.

    The new group is placed immediately after the last line of `anchor_leader`'s group.
    If `anchor_leader` is None the group is inserted at the start of the body.
    No existing lines are moved, reformatted, or re-emitted.
    """
    body_pat = re.compile(
        rf"(?P<open>{re.escape(var_name)}\s*=\s*f''')(?P<body>.*?)(?P<close>''')",
        re.DOTALL,
    )
    m = body_pat.search(raw_text)
    if not m:
        raise ValueError(f"f-string body for '{var_name}' not found.")
    body = m.group("body")
    new_block = "\n" + "\n".join(scaffold_lines) + "\n"
    if anchor_leader is None:
        new_body = new_block + body
    else:
        escaped = re.escape(anchor_leader)
        # Match every contiguous run of lines whose first token is anchor_leader.
        anchor_re = re.compile(rf"(?:[ \t]*{escaped}[ \t][^\n]*\n)+", re.MULTILINE)
        anchor_match = None
        for am in anchor_re.finditer(body):
            anchor_match = am
        if anchor_match is None:
            raise ValueError(
                f"Leader '{anchor_leader}' not found in f-string body of '{var_name}'."
            )
        ins = anchor_match.end()
        new_body = body[:ins] + new_block + body[ins:]
    return raw_text[: m.start("body")] + new_body + raw_text[m.end("body") :]


def extract_fstring_body(text: str, var_name: str) -> str:
    pattern = re.compile(rf"{var_name}\s*=\s*f'''(?P<body>.*?)'''", re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Unable to find f-string body for {var_name}.")
    return match.group("body")


def default_topflow_ports(slot: dict, active_dielet: str) -> str:
    if slot_flow_type(slot) == PARALLEL_FLOW_TYPE:
        return "{parallel_stdports}"
    if is_common_dielet_type(slot_value(slot, "all_dielet_type")):
        return "{pkg_stdports}"
    dielet_type = slot_value(slot, "all_dielet_type").upper()
    for dielet in ["CPU", "GCD", "HUB", "PCD"]:
        if dielet in dielet_type:
            return "{" + dielet.lower() + "pkg_stdports}"
    return "{" + active_dielet.lower() + "pkg_stdports}"


def default_shared_flwflgs_line(flow_name: str) -> str:
    return f"{subflow_symbol(flow_name):<30} TPI_FLWFLGS_XXX      {{flwflgs_stdports}}"


def default_dielet_pkg_flwflgs_line(flow_name: str) -> str:
    return f"{subflow_symbol(flow_name):<30} TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1"


def default_dielet_ip_flwflgs_line(flow_name: str, dielet: str) -> str:
    ip_code = DIELET_FILE_INFO[dielet]["ip_code"]
    stdports_name = f"ip{dielet.lower()}flwflgs_stdports"
    return f"{subflow_symbol(flow_name):<30} TPI_FLWFLGS_{ip_code}        {{{stdports_name}}}"


def managed_shared_main_slots(fullbp_slots: list[dict]) -> list[dict]:
    slots: list[dict] = []
    for slot in fullbp_slots:
        if slot_tp_exec(slot) != "MAIN":
            continue
        scope = slot_scope_family(slot)
        flow_type = slot_flow_type(slot)
        if scope != "PKG":
            continue
        if is_common_dielet_type(slot_value(slot, "all_dielet_type")):
            slots.append(slot)
            continue
        if flow_type == SERIAL_FLOW_TYPE:
            slots.append(slot)
    return slots


def shared_definition_order(fullbp_slots: list[dict]) -> list[str]:
    return unique_preserve([
        slot_flow_name(slot)
        for slot in fullbp_slots
        if slot_tp_exec(slot) == "MAIN"
        and slot_scope_family(slot) == "PKG"
        and is_common_dielet_type(slot_value(slot, "all_dielet_type"))
        and slot_flow_type(slot) == SERIAL_FLOW_TYPE
    ])


def dielet_pkg_definition_order(fullbp_slots: list[dict], active_dielet: str) -> list[str]:
    return unique_preserve([
        slot_dielet_flow_name(slot, active_dielet)
        for slot in fullbp_slots
        if slot_tp_exec(slot) == "MAIN"
        and slot_scope_family(slot) == "PKG"
        and slot_matches_dielet(slot, active_dielet)
        and slot_flow_type(slot) == SERIAL_FLOW_TYPE
    ])


def dielet_ip_wrapper_order(fullbp_slots: list[dict], active_dielet: str) -> list[str]:
    return unique_preserve([
        f"{slot_flow_name(slot)}{active_dielet}"
        for slot in fullbp_slots
        if slot_tp_exec(slot) == "MAIN"
        and slot_scope_family(slot) == "PKG"
        and is_common_dielet_type(slot_value(slot, "all_dielet_type"))
        and slot_flow_type(slot) == PARALLEL_FLOW_TYPE
        and slot_dielet_flow_name(slot, active_dielet)
    ])


def shared_parallel_order(fullbp_slots: list[dict]) -> list[str]:
    return unique_preserve([
        slot_flow_name(slot)
        for slot in fullbp_slots
        if slot_tp_exec(slot) == "MAIN"
        and slot_scope_family(slot) == "PKG"
        and is_common_dielet_type(slot_value(slot, "all_dielet_type"))
        and slot_flow_type(slot) == PARALLEL_FLOW_TYPE
    ])


def topflow_reference_orders(fullbp_slots: list[dict], active_dielet: str) -> dict[str, list[tuple[str, dict]]]:
    orders: dict[str, list[tuple[str, dict]]] = {}
    seen_by_topflow: dict[str, set[str]] = {}
    for slot in managed_shared_main_slots(fullbp_slots):
        top_flow = slot_top_flow(slot)
        if not top_flow:
            continue
        if slot_flow_type(slot) == PARALLEL_FLOW_TYPE:
            reference = "$" + subflow_symbol(slot_flow_name(slot))
        else:
            reference = subflow_symbol(slot_flow_name(slot))
        topflow_name = topflow_symbol(top_flow)
        seen_refs = seen_by_topflow.setdefault(topflow_name, set())
        if reference in seen_refs:
            continue
        seen_refs.add(reference)
        orders.setdefault(topflow_name, []).append((reference, slot))
    return orders


def reorder_managed_groups(
    groups: list[FlowGroup],
    desired_flow_names: list[str],
    scaffold_line_factory=None,
) -> tuple[list[FlowGroup], dict]:
    desired_leaders = [subflow_symbol(flow_name) for flow_name in desired_flow_names]
    desired_set = set(desired_leaders)
    existing = {group.leader: group for group in groups if group.leader in desired_set}
    extra = [group.leader for group in groups if group.leader and group.leader.endswith("_SubFlow") and group.leader not in desired_set]
    ordered: list[FlowGroup] = []
    missing: list[str] = []
    preserved_placeholder_groups: list[str] = []
    preserved_non_placeholder_groups: list[dict[str, object]] = []
    for flow_name in desired_flow_names:
        leader = subflow_symbol(flow_name)
        group = existing.get(leader)
        if group is None:
            missing.append(leader)
            if scaffold_line_factory is not None:
                ordered.append(FlowGroup(leader, [scaffold_line_factory(flow_name)]))
        else:
            if scaffold_line_factory is not None:
                scaffold_line = scaffold_line_factory(flow_name)
                if is_single_line_placeholder(group, scaffold_line):
                    preserved_placeholder_groups.append(leader)
                else:
                    preserved_non_placeholder_groups.append({
                        "leader": leader,
                        "executable_line_count": len(get_executable_lines(group)),
                    })
            ordered.append(group)
    managed_order = set(desired_leaders)
    unmanaged = [group for group in groups if group.leader not in managed_order]
    details = {
        "desired": desired_leaders,
        "existing": [group.leader for group in groups if group.leader],
        "added_managed": [leader for leader in desired_leaders if leader not in existing and scaffold_line_factory is not None],
        "missing_managed": missing,
        "extra_unmanaged": extra,
    }
    if scaffold_line_factory is not None:
        details["preserved_placeholder_groups"] = preserved_placeholder_groups
        details["preserved_non_placeholder_groups"] = preserved_non_placeholder_groups
    return ordered + unmanaged, details


def rebuild_topflow_group(group: FlowGroup, desired_refs: list[tuple[str, dict]], active_dielet: str) -> tuple[FlowGroup, dict]:
    existing_refs = parse_topflow_lines(group)
    new_lines: list[str] = []
    emitted: set[str] = set()
    for reference, slot in desired_refs:
        ports = existing_refs.get(reference, default_topflow_ports(slot, active_dielet))
        new_lines.append(format_topflow_line(group.leader or "", reference, ports))
        emitted.add(reference)
    for reference, ports in existing_refs.items():
        if reference in emitted:
            continue
        new_lines.append(format_topflow_line(group.leader or "", reference, ports))
    return FlowGroup(group.leader, new_lines), {
        "existing_refs": list(existing_refs.keys()),
        "desired_refs": [reference for reference, _ in desired_refs],
    }


def update_prl_dict(text: str, desired_parallel_flows: list[str]) -> tuple[str, dict]:
    match = PRL_DICT_RE.search(text)
    if not match:
        raise ValueError("Unable to find prl_dict block.")
    body_lines = [format_prl_dict_entry(flow_name) for flow_name in desired_parallel_flows]
    replacement = match.group("prefix") + "\n".join(body_lines) + match.group("suffix")
    details = {
        "desired": [subflow_symbol(flow_name) for flow_name in desired_parallel_flows],
    }
    return text[:match.start()] + replacement + text[match.end():], details


def build_sync_plan(repo_root: Path, workbook_context: dict, boms: list[str], repo_scope: str) -> dict:
    active_dielet = detect_active_dielet(repo_root)
    if active_dielet is None:
        raise ValueError("Unable to detect active dielet repo from workspace root.")

    fullbp_slots = workbook_context["fullbp_slots"]
    plan = {
        "status": "ready",
        "repo_root": str(repo_root),
        "active_dielet": active_dielet,
        "repo_scope": repo_scope,
        "boms": boms,
        "files": [],
    }

    shared_main_order = shared_definition_order(fullbp_slots)
    dielet_pkg_order = dielet_pkg_definition_order(fullbp_slots, active_dielet)
    dielet_ip_order = dielet_ip_wrapper_order(fullbp_slots, active_dielet)
    parallel_order = shared_parallel_order(fullbp_slots)
    topflow_orders = topflow_reference_orders(fullbp_slots, active_dielet)

    file_info = DIELET_FILE_INFO[active_dielet]

    for bom in boms:
        if repo_scope_includes(repo_scope, "shared"):
            plan["files"].append(
                plan_shared_pkg_file(repo_root, bom, shared_main_order, topflow_orders, active_dielet)
            )
            plan["files"].append(
                plan_shared_wrapper_file(repo_root, bom, parallel_order)
            )
        if repo_scope_includes(repo_scope, "dielet"):
            plan["files"].append(
                plan_dielet_pkg_file(repo_root, bom, file_info["programflows"], dielet_pkg_order)
            )
            plan["files"].append(
                plan_dielet_ip_file(repo_root, bom, file_info["ip_flows"], dielet_ip_order, active_dielet)
            )

    return plan


def plan_shared_pkg_file(repo_root: Path, bom: str, shared_main_order: list[str], topflow_orders: dict[str, list[tuple[str, dict]]], active_dielet: str) -> dict:
    path = repo_root / "Shared" / "POR_TP" / bom / "ProgramFlowsTestPlan" / "ProgramFlowsSharedPKG.py"
    text = path.read_text(encoding="utf-8")
    body = extract_fstring_body(text, "MAIN_code")
    groups = split_groups(body)

    definition_groups = [group for group in groups if group.leader and group.leader.endswith("_SubFlow") and not group.leader.endswith("_TopFlow") and group.leader != "MAIN" and not group.leader.startswith("{")]
    unmanaged_groups = [group for group in groups if group not in definition_groups and group.leader not in topflow_orders]

    reordered_definitions, definition_details = reorder_managed_groups(
        definition_groups,
        shared_main_order,
        default_shared_flwflgs_line,
    )

    rebuilt_topflows: list[FlowGroup] = []
    topflow_details: dict[str, dict] = {}
    for group in groups:
        if group.leader in topflow_orders:
            rebuilt_group, details = rebuild_topflow_group(group, topflow_orders[group.leader], active_dielet)
            rebuilt_topflows.append(rebuilt_group)
            topflow_details[group.leader] = details

    ordered_groups = reordered_definitions
    placeholder_groups = [group for group in groups if group.leader and group.leader.startswith("{")]
    ordered_groups.extend(placeholder_groups)
    ordered_groups.extend(rebuilt_topflows)
    ordered_groups.extend(group for group in unmanaged_groups if group.leader != "MAIN")
    main_group = next((group for group in groups if group.leader == "MAIN"), None)
    if main_group is not None:
        ordered_groups.append(main_group)

    new_body = render_groups(ordered_groups)
    changed = new_body != body
    return {
        "path": str(path),
        "kind": "shared-main-code",
        "changed": changed,
        "details": {
            "definition_order": definition_details,
            "topflows": topflow_details,
        },
        "updated_text": replace_fstring_body(text, "MAIN_code", new_body) if changed else text,
    }


def plan_shared_wrapper_file(repo_root: Path, bom: str, parallel_order: list[str]) -> dict:
    path = repo_root / "Shared" / "POR_TP" / bom / "ProgramFlowsTestPlan" / "ProgramFlows.py"
    text = path.read_text(encoding="utf-8")
    updated_text, details = update_prl_dict(text, parallel_order)
    changed = updated_text != text
    return {
        "path": str(path),
        "kind": "shared-prl-dict",
        "changed": changed,
        "details": details,
        "updated_text": updated_text,
    }


def plan_dielet_pkg_file(repo_root: Path, bom: str, filename: str, dielet_pkg_order: list[str]) -> dict:
    path = repo_root / "POR_TP" / bom / "ProgramFlowsTestPlan" / filename
    text = path.read_text(encoding="utf-8")
    variable_name = filename.replace(".py", "").replace("ProgramFlows", "").upper() + "DISAGG_SubFlow"
    body = extract_fstring_body(text, variable_name)
    groups = split_groups(body)
    desired_leaders = [subflow_symbol(flow_name) for flow_name in dielet_pkg_order]
    existing_leaders: set[str] = {group.leader for group in groups if group.leader}
    missing = [leader for leader in desired_leaders if leader not in existing_leaders]
    extra = [
        group.leader for group in groups
        if group.leader and group.leader.endswith("_SubFlow") and group.leader not in set(desired_leaders)
    ]
    details = {
        "desired": desired_leaders,
        "existing": [group.leader for group in groups if group.leader],
        "added_managed": missing,
        "missing_managed": missing,
        "extra_unmanaged": extra,
        "preserved_placeholder_groups": [],
        "preserved_non_placeholder_groups": [],
    }
    if not missing:
        return {"path": str(path), "kind": "dielet-pkg", "changed": False, "details": details, "updated_text": text}
    # Targeted inserts only — no re-rendering of existing content.
    updated_text = text
    for leader in missing:
        idx = desired_leaders.index(leader)
        anchor_leader: str | None = None
        for preceding in reversed(desired_leaders[:idx]):
            if preceding in existing_leaders:
                anchor_leader = preceding
                break
        scaffold_line = default_dielet_pkg_flwflgs_line(leader.removesuffix("_SubFlow"))
        updated_text = targeted_insert_group_after_anchor(updated_text, variable_name, [scaffold_line], anchor_leader)
        existing_leaders.add(leader)
    return {"path": str(path), "kind": "dielet-pkg", "changed": True, "details": details, "updated_text": updated_text}


def plan_dielet_ip_file(repo_root: Path, bom: str, filename: str, dielet_ip_order: list[str], active_dielet: str) -> dict:
    path = repo_root / "POR_TP" / bom / "ProgramFlowsTestPlan" / filename
    text = path.read_text(encoding="utf-8")
    body = extract_fstring_body(text, "MAIN_code")
    groups = split_groups(body)
    desired_leaders = [subflow_symbol(flow_name) for flow_name in dielet_ip_order]
    existing_leaders: set[str] = {group.leader for group in groups if group.leader}
    missing = [leader for leader in desired_leaders if leader not in existing_leaders]
    extra = [
        group.leader for group in groups
        if group.leader and group.leader.endswith("_SubFlow") and group.leader not in set(desired_leaders)
    ]
    details = {
        "desired": desired_leaders,
        "existing": [group.leader for group in groups if group.leader],
        "added_managed": missing,
        "missing_managed": missing,
        "extra_unmanaged": extra,
    }
    if not missing:
        return {"path": str(path), "kind": "dielet-ip-main-code", "changed": False, "details": details, "updated_text": text}
    # Targeted inserts only — no re-rendering of existing content.
    updated_text = text
    for leader in missing:
        idx = desired_leaders.index(leader)
        anchor_leader: str | None = None
        for preceding in reversed(desired_leaders[:idx]):
            if preceding in existing_leaders:
                anchor_leader = preceding
                break
        scaffold_line = default_dielet_ip_flwflgs_line(leader.removesuffix("_SubFlow"), active_dielet)
        updated_text = targeted_insert_group_after_anchor(updated_text, "MAIN_code", [scaffold_line], anchor_leader)
        existing_leaders.add(leader)
    return {"path": str(path), "kind": "dielet-ip-main-code", "changed": True, "details": details, "updated_text": updated_text}


def apply_sync_plan(plan: dict) -> dict:
    changed_files: list[str] = []
    for file_plan in plan.get("files", []):
        if not file_plan.get("changed"):
            continue
        path = Path(file_plan["path"])
        path.write_text(file_plan["updated_text"], encoding="utf-8")
        changed_files.append(str(path))
    result = dict(plan)
    result["status"] = "applied"
    result["changed_files"] = changed_files
    return result


def serialize_plan(plan: dict) -> str:
    redacted = dict(plan)
    files = []
    for file_plan in redacted.get("files", []):
        item = dict(file_plan)
        item.pop("updated_text", None)
        files.append(item)
    redacted["files"] = files
    return json.dumps(redacted, indent=2)