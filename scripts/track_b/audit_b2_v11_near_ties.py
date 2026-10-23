"""Supplemental descriptive near-tie report for a completed B2 v11 run.

Reads the generated float64 result and only named comparison/geometry arrays
from the sealed signature library through v11's runtime key guard. Never reads
the prepared EEG ``data`` member or performs model fitting.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "outputs" / "tracka_release_20261022_v2"
VERIFIER_PATH = ROOT / "scripts" / "track_b" / "recompute_b2_gbf_cpu64_v11.py"
SPEC_SHA256 = "1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_verifier():
    spec = importlib.util.spec_from_file_location("b2_v11_near_tie_guard", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v11 guard implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    run_dir = run_dir.resolve()
    primary_report_path = run_dir / "independent_recompute_report.json"
    arrays_path = run_dir / "independent_pairwise_top5_float64.npz"
    report_path = run_dir / "near_tie_diagnostics.json"
    access_log = run_dir / "near_tie_access_log.jsonl"
    if not primary_report_path.is_file() or not arrays_path.is_file():
        raise SystemExit("run directory lacks the registered v11 report or result arrays")
    if report_path.exists() or access_log.exists():
        raise SystemExit("refusing to overwrite supplemental diagnostic outputs")
    primary = json.loads(primary_report_path.read_text(encoding="utf-8"))
    if primary.get("spec_sha256") != SPEC_SHA256 or primary.get("verifier_sha256") != sha256(VERIFIER_PATH):
        raise SystemExit("run report does not match the frozen specification and current v11 verifier")
    if not all(primary.get("comparison_to_sealed_track_a", {}).get(k) is True for k in (
        "ranking_exact_match", "valid_mask_exact_match", "candidate_counts_exact_match"
    )):
        raise SystemExit("registered exact-match checks did not pass")
    signature_rel = "outputs/tracka_release_20261022_v2/nominal_signature_library.npz"
    if primary.get("input_sha256", {}).get(signature_rel) != sha256(ROOT / signature_rel):
        raise SystemExit("sealed signature library hash differs from registered run")

    with np.load(arrays_path, allow_pickle=False) as z:
        indices = np.asarray(z["candidate_indices"])
        scores = np.asarray(z["absolute_cosine"])
        valid = np.asarray(z["valid_source"])
        counts = np.asarray(z["distant_candidate_count"])
        norms = np.asarray(z["whitened_norm"])
    if indices.dtype != np.int64 or scores.dtype != np.float64:
        raise AssertionError("v11 output index/score storage dtypes differ from contract")

    v11 = load_verifier()
    run_id = primary["run_id"] + "_near_tie_diagnostic"
    with v11.guarded_npz(ROOT / signature_rel, v11.SIGNATURE_ALLOWED_KEYS, access_log, run_id) as archive:
        ref_indices = np.asarray(archive["candidate_indices"])
        ref_scores = np.asarray(archive["absolute_cosine"])
        ref_valid = np.asarray(archive["valid_source"])
        ref_counts = np.asarray(archive["distant_candidate_count"])
        ref_norms = np.asarray(archive["whitened_norm"])
        vertex_ids = np.asarray(archive["vertex_ids"])

    if not np.array_equal(indices, ref_indices):
        raise AssertionError("supplemental audit found a ranking mismatch")
    if not np.array_equal(valid, ref_valid) or not np.array_equal(counts, ref_counts):
        raise AssertionError("supplemental audit found a validity/count mismatch")
    if not np.array_equal(np.isfinite(scores), np.isfinite(ref_scores)):
        raise AssertionError("supplemental audit found a score finite-mask mismatch")

    eligible = valid & (counts >= 2) & (indices[:, 1] >= 0)
    gaps = scores[eligible, 0] - scores[eligible, 1]
    if np.any(gaps < 0):
        raise AssertionError("top-two scores are not in descending order")
    order = np.argsort(gaps, kind="stable")
    close = []
    rows = np.flatnonzero(eligible)
    for position in order[: min(20, len(order))]:
        row = int(rows[position])
        close.append({
            "source_row": row,
            "source_vertex_id": int(vertex_ids[row]),
            "best_candidate_index": int(indices[row, 0]),
            "best_candidate_vertex_id": int(vertex_ids[indices[row, 0]]),
            "second_candidate_index": int(indices[row, 1]),
            "second_candidate_vertex_id": int(vertex_ids[indices[row, 1]]),
            "best_score": float(scores[row, 0]),
            "second_score": float(scores[row, 1]),
            "top_two_margin": float(gaps[position]),
        })

    norm_delta = np.abs(norms - ref_norms)
    norm_scale = np.maximum(np.abs(ref_norms), np.finfo(np.float64).tiny)
    relative = norm_delta / norm_scale
    primary_comparison = primary["comparison_to_sealed_track_a"]
    report = {
        "status": "PASS",
        "audit_type": "supplemental descriptive near-tie and norm-tolerance report",
        "run_id": run_id,
        "parent_registered_run_id": primary["run_id"],
        "spec_sha256": SPEC_SHA256,
        "verifier_sha256": sha256(VERIFIER_PATH),
        "registered_report_sha256": sha256(primary_report_path),
        "registered_result_arrays_sha256": sha256(arrays_path),
        "sealed_signature_library_sha256": sha256(ROOT / signature_rel),
        "registered_exact_matches_reconfirmed": {
            "ranking": True,
            "valid_mask": True,
            "candidate_counts": True,
        },
        "top_two_margin": {
            "definition": "best eligible absolute-cosine score minus second-best eligible absolute-cosine score for each source row; descriptive only, no inferential threshold",
            "source_rows_with_two_or_more_candidates": int(len(gaps)),
            "exact_zero_margin_count": int(np.count_nonzero(gaps == 0.0)),
            "minimum": float(np.min(gaps)) if len(gaps) else None,
            "quantiles": {str(q): float(np.quantile(gaps, q)) for q in (0.01, 0.05, 0.5, 0.95, 0.99)} if len(gaps) else {},
            "twenty_smallest_margins": close,
        },
        "whitened_norm_check": {
            "comparison": "np.allclose(recomputed_float64, sealed_float64, rtol=1e-8, atol=1e-15)",
            "passed": bool(np.allclose(norms, ref_norms, rtol=1e-8, atol=1e-15)),
            "max_absolute_difference": float(norm_delta.max(initial=0.0)),
            "max_relative_difference": float(relative.max(initial=0.0)),
            "registered_max_absolute_difference": primary_comparison["whitened_norm_max_abs_difference"],
            "rtol": 1e-8,
            "atol": 1e-15,
        },
        "sealed_access": {
            "archive": Path(signature_rel).name,
            "keys_read": ["candidate_indices", "absolute_cosine", "valid_source", "distant_candidate_count", "whitened_norm", "vertex_ids"],
            "recorded_eeg_data_key_accessed": False,
            "access_log": access_log.name,
            "access_log_sha256": sha256(access_log),
            "limitation": "guarded Python access only; not an OS sandbox",
        },
        "limitations": [
            "Margins are descriptive for the declared single forward model and covariance.",
            "Small margins indicate near ties among modeled candidate signatures; they are not probabilities of source confusion.",
            "This diagnostic makes no physiological localization or generalization claim.",
        ],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    if not report["whitened_norm_check"]["passed"]:
        report["status"] = "FAIL"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "near_tie_report": str(report_path),
        "source_rows": report["top_two_margin"]["source_rows_with_two_or_more_candidates"],
        "exact_ties": report["top_two_margin"]["exact_zero_margin_count"],
        "minimum_margin": report["top_two_margin"]["minimum"],
        "norm_allclose": report["whitened_norm_check"]["passed"],
        "max_norm_relative_difference": report["whitened_norm_check"]["max_relative_difference"],
    }, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
