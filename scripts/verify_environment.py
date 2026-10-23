"""Verify the exact pinned Python environment and record platform provenance."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from tracka_paths import OUT

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    req_path = ROOT / "requirements-foundation.txt"
    expected = {}
    for line in req_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, version = line.split("==", 1)
        expected[name.lower().replace("_", "-")] = version
    installed = {d.metadata["Name"].lower().replace("_", "-"): d.version
                 for d in importlib.metadata.distributions() if d.metadata.get("Name")}
    mismatches = {name: {"expected": version, "installed": installed.get(name)}
                  for name, version in expected.items() if installed.get(name) != version}
    report = {
        "status": "PASS" if not mismatches and sys.version_info[:2] == (3, 12) else "FAIL",
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "is_virtual_environment": sys.prefix != sys.base_prefix,
        "environment_prefix": sys.prefix,
        "requirements_sha256": hashlib.sha256(req_path.read_bytes()).hexdigest(),
        "pinned_package_count": len(expected),
        "versions": {name: installed.get(name) for name in sorted(expected)},
        "mismatches": mismatches,
    }
    out = OUT / "environment_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if mismatches or sys.version_info[:2] != (3, 12):
        raise SystemExit("Python 3.12 and exact pinned package versions are required")


if __name__ == "__main__":
    main()
