"""Integrity checks before displaying a completed distinguish run in the browser."""
from __future__ import annotations

import json
from pathlib import Path

from .cli import sha256


EXPECTED_OUTPUTS = frozenset({"scores.npz", "ranked_pairs.csv", "summary.json", "npz_key_access.jsonl"})


def verify_completed_run(directory: Path) -> dict:
    """Check the package's own manifest, not independent scientific validity."""
    manifest_path = directory / "run_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("run_manifest.json is missing; this is not a complete distinguish run")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hashes = manifest.get("output_sha256")
    if manifest.get("command") != "observable-geometry distinguish" or not isinstance(hashes, dict):
        raise ValueError("run manifest does not describe a distinguish result")
    if set(hashes) != EXPECTED_OUTPUTS:
        raise ValueError("run manifest has missing or unexpected output hashes")
    for name in sorted(EXPECTED_OUTPUTS):
        path = directory / name
        if not path.is_file() or sha256(path) != hashes[name]:
            raise ValueError(f"run output is missing or differs from its manifest: {name}")
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    if summary.get("status") != "COMPLETED_NOMINAL_MODEL_DIAGNOSTIC":
        raise ValueError("run summary does not report a completed nominal diagnostic")
    return summary
