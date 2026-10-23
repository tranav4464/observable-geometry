"""Verify a repeat of the B3 montage audit against its registered run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "outputs/track_b/20261024_b3_montage_sensitivity"
REPEAT = ROOT / "outputs/track_b/20261024_b3_montage_sensitivity_reproduction_01"
OUTPUT = REPEAT / "reproduction_check.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite existing verification: {OUTPUT}")

    primary_report = read_json(PRIMARY / "sensitivity_report.json")
    repeat_report = read_json(REPEAT / "sensitivity_report.json")
    primary_manifest = read_json(PRIMARY / "run_manifest.json")
    repeat_manifest = read_json(REPEAT / "run_manifest.json")
    primary_log = PRIMARY / "run_access_log.json"
    repeat_log = REPEAT / "run_access_log.json"

    primary_semantics = {key: value for key, value in primary_report.items() if key != "created_utc"}
    repeat_semantics = {key: value for key, value in repeat_report.items() if key != "created_utc"}
    exact_report_match = primary_semantics == repeat_semantics
    exact_inputs_match = primary_manifest["inputs_sha256"] == repeat_manifest["inputs_sha256"]
    exact_access_match = primary_log.read_bytes() == repeat_log.read_bytes()
    both_guarded = all(
        manifest.get("recorded_eeg_data_key_accessed") is False
        for manifest in (primary_manifest, repeat_manifest)
    )
    checks = {
        "semantic_report_match_ignoring_creation_time": exact_report_match,
        "input_hashes_match": exact_inputs_match,
        "access_logs_byte_identical": exact_access_match,
        "both_runs_report_no_eeg_data_key_access": both_guarded,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "primary_run": PRIMARY.relative_to(ROOT).as_posix(),
        "repeat_run": REPEAT.relative_to(ROOT).as_posix(),
        "checks": checks,
        "primary_report_sha256": sha256(PRIMARY / "sensitivity_report.json"),
        "repeat_report_sha256": sha256(REPEAT / "sensitivity_report.json"),
        "primary_manifest_sha256": sha256(PRIMARY / "run_manifest.json"),
        "repeat_manifest_sha256": sha256(REPEAT / "run_manifest.json"),
        "source_claim_boundary": "Repeatability of one model-only descriptive calculation; not empirical source validation or an independent sample.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
