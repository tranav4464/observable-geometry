"""Fail-closed validation for the Track B gate register."""
from __future__ import annotations

from pathlib import Path
from typing import Any


VALID_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "PASS", "FAIL", "PIVOT"}
CONTRACT_FIELDS = {
    "objective": str,
    "exit_criteria": list,
    "verification": list,
    "falsification_check": str,
    "failure_route": str,
    "independent_review": str,
    "verification_evidence": list,
}


def validate_gate_register(register: dict[str, Any], root: Path) -> list[str]:
    """Return all gate-register inconsistencies without modifying any files.

    `blocking` lists downstream gate IDs that must not advance before the
    current gate passes. FAIL/PIVOT remain valid terminal research decisions.
    """
    errors: list[str] = []
    contract_enabled = register.get("stage_contract_version") == 1
    if register.get("stage_contract_version") not in (None, 1):
        errors.append("unsupported stage_contract_version")
    authority = register.get("authority")
    if authority is not None:
        if not isinstance(authority, str) or not authority.strip():
            errors.append("authority must be a nonempty repository-relative path")
        elif not (root / authority).is_file():
            errors.append(f"missing authority document {authority}")
    gates = register.get("gates")
    if not isinstance(gates, list) or not gates:
        return ["register must contain a nonempty gates list"]
    ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
    if len(ids) != len(gates) or any(not isinstance(key, str) or not key for key in ids):
        return ["every gate must be an object with a nonempty string id"]
    if len(set(ids)) != len(ids):
        errors.append("gate IDs must be unique")
    by_id = {gate["id"]: gate for gate in gates}
    prerequisites: dict[str, set[str]] = {key: set() for key in ids}
    graph: dict[str, list[str]] = {key: [] for key in ids}

    for gate in gates:
        key = gate["id"]
        status = gate.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"{key}: unknown status {status!r}")
            continue
        evidence = gate.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{key}: evidence must be a list")
            evidence = []
        if status in {"IN_PROGRESS", "PASS", "FAIL", "PIVOT"}:
            if status == "PASS" and not evidence:
                errors.append(f"{key}: PASS requires at least one evidence path")
            for item in evidence:
                if not isinstance(item, str) or not item:
                    errors.append(f"{key}: evidence paths must be nonempty strings")
                elif not (root / item).exists():
                    errors.append(f"{key}: missing evidence path {item}")
        if contract_enabled:
            for field, expected_type in CONTRACT_FIELDS.items():
                value = gate.get(field)
                if not isinstance(value, expected_type):
                    errors.append(f"{key}: {field} must be a {expected_type.__name__}")
                    continue
                if expected_type is str and not value.strip():
                    errors.append(f"{key}: {field} must be nonempty")
                elif expected_type is list and field != "verification_evidence":
                    if not value or any(not isinstance(item, str) or not item.strip() for item in value):
                        errors.append(f"{key}: {field} must contain nonempty strings")
            verification_evidence = gate.get("verification_evidence")
            if isinstance(verification_evidence, list):
                if status == "PASS" and not verification_evidence:
                    errors.append(f"{key}: PASS requires verification_evidence")
                for item in verification_evidence:
                    if not isinstance(item, str) or not item:
                        errors.append(f"{key}: verification_evidence paths must be nonempty strings")
                    elif not (root / item).exists():
                        errors.append(f"{key}: missing verification evidence path {item}")
        blockers = gate.get("blocking")
        if not isinstance(blockers, list):
            errors.append(f"{key}: blocking must be a list")
            blockers = []
        for downstream in blockers:
            if downstream not in by_id:
                errors.append(f"{key}: unknown blocked gate {downstream!r}")
                continue
            if downstream == key:
                errors.append(f"{key}: cannot block itself")
                continue
            graph[key].append(downstream)
            prerequisites[downstream].add(key)

    # A cycle makes the progression policy impossible to satisfy.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"gate dependency graph contains a cycle at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph[node]:
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)

    for gate in gates:
        key = gate["id"]
        status = gate.get("status")
        if status in {"IN_PROGRESS", "PASS", "FAIL"}:
            for prerequisite in sorted(prerequisites[key]):
                prerequisite_status = by_id[prerequisite].get("status")
                if prerequisite_status != "PASS":
                    errors.append(f"{key}: prerequisite {prerequisite} is {prerequisite_status}, not PASS")
    return errors
