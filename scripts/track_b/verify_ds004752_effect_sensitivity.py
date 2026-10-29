"""Independently replay the ds004752 participant-effect sensitivity summary."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT.parent / "experiment_v2/real_results"
DEFAULT_AUDIT = ROOT / "outputs/track_b/20261029T_ds004752_effect_sensitivity_002/sensitivity.json"
DEFAULT_OUTPUT = ROOT / "outputs/track_b/20261029T_ds004752_effect_sensitivity_002/independent_check_001.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    results_dir, audit_path, output = args.results_dir.resolve(), args.audit.resolve(), args.output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"refusing to overwrite report: {output}")
    effects_path = results_dir / "primary_effects.csv"
    summary_path = results_dir / "summary.json"
    with effects_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    x = np.asarray([float(r["global_minus_cross_spectrum_nmae"]) for r in rows], dtype=np.float64)
    observed = abs(float(x.mean()))
    sign_matrix = np.asarray(list(itertools.product((-1.0, 1.0), repeat=len(x))), dtype=np.float64)
    permuted = np.abs((sign_matrix * x).mean(axis=1))
    flip_p = float(np.mean(permuted >= observed - 16 * np.finfo(float).eps * max(1.0, observed)))
    positive = int(np.count_nonzero(x > 0))
    negative = int(np.count_nonzero(x < 0))
    sign_p = float(binomtest(positive, positive + negative, p=0.5, alternative="two-sided").pvalue)
    loo = np.asarray([np.delete(x, i).mean() for i in range(len(x))])
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    checks = {
        "input_effect_hash_matches_audit": digest(effects_path) == audit["input_files"]["primary_effects_csv"]["sha256"],
        "input_summary_hash_matches_audit": digest(summary_path) == audit["input_files"]["summary_json"]["sha256"],
        "mean_matches": np.isclose(x.mean(), audit["mean_effect"], rtol=0, atol=1e-14),
        "median_matches": np.isclose(np.median(x), audit["median_effect"], rtol=0, atol=1e-14),
        "sign_flip_p_matches": np.isclose(flip_p, audit["exact_two_sided_sign_flip_pvalue_for_mean"], rtol=0, atol=1e-14),
        "sign_test_p_matches": np.isclose(sign_p, audit["exact_two_sided_sign_test_pvalue"], rtol=0, atol=1e-14),
        "leave_one_out_range_matches": np.allclose([loo.min(), loo.max()], audit["leave_one_participant_out_mean_range"], rtol=0, atol=1e-14),
        "participant_sign_counts_match": positive == audit["n_positive"] and negative == audit["n_negative"],
        "source_summary_count_matches": len(x) == summary.get("participants"),
        "source_summary_mean_matches": np.isclose(x.mean(), summary.get("primary_mean_nmae_improvement", np.nan), rtol=0, atol=1e-12),
        "source_summary_positive_count_matches": positive == summary.get("participants_improved"),
        "source_summary_scope_is_prediction_only": "not source-localization" in summary.get("scope", ""),
        "source_summary_reports_no_synthetic_neural_data": summary.get("synthetic_neural_data_used") is False,
        "no_signal_data_claimed": audit["signal_array_accessed"] is False,
    }
    report = {
        "status": "PASS" if all(bool(v) for v in checks.values()) else "FAIL",
        "verification_scope": "Independent replay from the derived participant effect CSV using vectorized enumeration and scipy.stats.binomtest; no EEG/iEEG samples accessed.",
        "checks": {key: bool(value) for key, value in checks.items()},
        "n_sign_assignments": int(len(sign_matrix)),
        "n_participants": int(len(x)),
        "mean_effect": float(x.mean()),
        "exact_sign_flip_p": flip_p,
        "exact_binomial_sign_test_p": sign_p,
        "leave_one_out_mean_range": [float(loo.min()), float(loo.max())],
        "input_sha256": digest(effects_path),
        "summary_sha256": digest(summary_path),
        "audit_sha256": digest(audit_path),
        "limits": ["This verifies summary arithmetic only; it does not re-run the measured-data model or validate source localization."],
    }
    if report["status"] != "PASS":
        raise SystemExit("independent sensitivity replay failed: " + json.dumps(report["checks"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
