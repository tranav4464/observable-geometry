"""Verify B4's saved 224-channel descriptive rerun against sealed Track A outputs.

This verifier reads only saved derived JSON/CSV artifacts. It does not open
recording samples, fit a model, or access held-out participant data.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "outputs" / "20261023T192900Z_b4_matched_224_reproduction"
SEALED = ROOT / "outputs" / "tracka_release_20261022_v2"
OUT = RUN / "b4_reproduction_audit.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    fresh_csv = RUN / "predicted_observed_similarity.csv"
    sealed_csv = SEALED / "predicted_observed_similarity.csv"
    fresh_report_path = RUN / "empirical_evaluation_report.json"
    sealed_report_path = SEALED / "empirical_evaluation_report.json"
    fresh = json.loads(fresh_report_path.read_text(encoding="utf-8"))
    sealed = json.loads(sealed_report_path.read_text(encoding="utf-8"))
    fresh_rows, sealed_rows = csv_rows(fresh_csv), csv_rows(sealed_csv)
    exact_csv = fresh_csv.read_bytes() == sealed_csv.read_bytes()
    report = {
        "status": "PASS_DERIVED_OUTPUT_REPRODUCTION_ONLY" if exact_csv else "FAIL",
        "scope": "saved derived outputs; no recording samples opened by this verifier",
        "fresh_run_id": "20261023T192900Z_b4_matched_224_reproduction",
        "sealed_run_id": "tracka_release_20261022_v2",
        "participant": fresh.get("participant"),
        "n_common_good_channels": fresh.get("n_common_good_channels"),
        "observation_window_s": fresh.get("observation_window_s"),
        "fresh_rows": len(fresh_rows),
        "sealed_rows": len(sealed_rows),
        "csv_byte_identical": exact_csv,
        "rows_equal": fresh_rows == sealed_rows,
        "fresh_csv_sha256": sha256(fresh_csv),
        "sealed_csv_sha256": sha256(sealed_csv),
        "fresh_report_sha256": sha256(fresh_report_path),
        "sealed_report_sha256": sha256(sealed_report_path),
        "fresh_summary_error_mm": fresh.get("summary_error_mm"),
        "fresh_pair_similarity": fresh.get("predicted_vs_observed_pair_similarity"),
        "limitations": [
            "This is a reproduction check for a previously exposed single-participant development analysis.",
            "The endpoint is the intracranial stimulation pulse artifact, not endogenous neural activity.",
            "This does not compare the B2 score directly with a matched 224-channel MNE PSF/CTF.",
            "This does not establish physiological source recovery, method superiority, novelty, or generalization.",
        ],
    }
    if fresh.get("n_common_good_channels") != 224:
        report["status"] = "FAIL"
    if len(fresh_rows) != 15 or len(sealed_rows) != 15:
        report["status"] = "FAIL"
    if fresh.get("observation_window_s") != [-0.002, 0.002]:
        report["status"] = "FAIL"
    if fresh.get("participant") != "sub-01":
        report["status"] = "FAIL"
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS_DERIVED_OUTPUT_REPRODUCTION_ONLY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
