"""Static and dummy-archive runtime audit for the B2 v11 NPZ key guard.

No project archives are opened by this audit. A temporary synthetic NPZ is used
to prove that a forbidden ``data`` key is rejected before the payload is read.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "scripts" / "track_b" / "recompute_b2_gbf_cpu64_v11.py"
STATIC_AUDITOR = ROOT / "scripts" / "track_b" / "audit_b2_signal_access_boundary.py"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def audit() -> dict:
    source = VERIFIER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(VERIFIER))
    static = import_module(STATIC_AUDITOR, "b2_static_access_auditor")
    prepared_keys = static.prepared_bundle_keys_read_by_verifier(tree)
    if prepared_keys != {"leadfield", "noise_cov"}:
        raise AssertionError(f"unexpected prepared-bundle access keys: {sorted(prepared_keys)}")

    class LoadCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.method = None
            self.calls = []

        def visit_FunctionDef(self, node):
            previous = self.method
            self.method = node.name
            self.generic_visit(node)
            self.method = previous

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "np" and node.func.attr == "load":
                self.calls.append(self.method)
            self.generic_visit(node)

    calls = LoadCallVisitor()
    calls.visit(tree)
    if calls.calls != ["__enter__"]:
        raise AssertionError(f"NumPy NPZ loads must occur only inside GuardedNPZ.__enter__; found {calls.calls}")

    module = import_module(VERIFIER, "b2_v11_access_audit")
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        dummy = temp / "dummy.npz"
        log = temp / "access.jsonl"
        np.savez(dummy, leadfield=np.ones((2, 2)), noise_cov=np.eye(2), data=np.arange(64))
        with module.guarded_npz(dummy, {"leadfield", "noise_cov"}, log, "dummy-access-audit") as archive:
            np.testing.assert_array_equal(archive["leadfield"], np.ones((2, 2)))
            np.testing.assert_array_equal(archive["noise_cov"], np.eye(2))
            try:
                archive["data"]
            except PermissionError:
                denied_before_read = True
            else:
                denied_before_read = False
        events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    if not denied_before_read or [e["decision"] for e in events] != ["allow", "allow", "deny"]:
        raise AssertionError("dummy archive did not demonstrate the expected runtime allow/deny log")
    if events[-1]["key"] != "data":
        raise AssertionError("runtime guard log did not record the denied data-key attempt")

    return {
        "status": "PASS",
        "audit_type": "static allowlist plus synthetic runtime archive test; no project arrays accessed",
        "verifier_path": str(VERIFIER.relative_to(ROOT)),
        "verifier_sha256": sha256(VERIFIER),
        "prepared_bundle_literal_keys": sorted(prepared_keys),
        "np_load_call_sites": calls.calls,
        "dummy_archive_contains_data_key": True,
        "dummy_data_key_denied_before_numpy_member_read": denied_before_read,
        "dummy_access_events": events,
        "project_npz_archives_opened": False,
        "limitations": "This tests the project process-level wrapper and source structure; it is not an OS sandbox or a tamper-proof log.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new JSON report outside the sealed Track A release")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    sealed = ROOT / "outputs" / "tracka_release_20261022_v2"
    if output == sealed or sealed in output.parents:
        raise SystemExit("Refusing to write inside the sealed Track A release")
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing audit report: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = audit()
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output), "sha256": sha256(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
