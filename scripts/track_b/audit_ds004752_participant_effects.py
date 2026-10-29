"""Post-hoc sensitivity audit of saved ds004752 participant-level effects.

This reads only the derived participant effect CSV and summary JSON. It never
opens EEG/iEEG recordings, features, or trial predictions.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import tempfile

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT.parent / "experiment_v2/real_results"
DEFAULT_OUTPUT = ROOT / "outputs/track_b/20261029T_ds004752_effect_sensitivity_002"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_sign_flip_pvalue(values: np.ndarray) -> float:
    """Two-sided exact participant-level sign-flip p-value for the mean."""
    observed = abs(float(np.mean(values)))
    tolerance = 16 * np.finfo(np.float64).eps * max(1.0, observed)
    extreme = 0
    total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        statistic = abs(float(np.mean(values * np.asarray(signs))))
        extreme += statistic + tolerance >= observed
        total += 1
    return extreme / total


def exact_sign_test_pvalue(positive: int, n: int) -> float:
    """Two-sided exact binomial sign test, with ties excluded from n."""
    negative = n - positive
    tail = min(positive, negative)
    numerator = sum(math.comb(n, k) for k in range(tail + 1))
    return min(1.0, 2.0 * numerator / (2 ** n))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    results_dir = args.results_dir.resolve()
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing result: {output}")
    effects_path = results_dir / "primary_effects.csv"
    summary_path = results_dir / "summary.json"
    if not effects_path.is_file() or not summary_path.is_file():
        raise FileNotFoundError("expected primary_effects.csv and summary.json")

    with effects_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not {"subject", "global_minus_cross_spectrum_nmae"}.issubset(rows[0]):
        raise ValueError("participant effect CSV does not match the expected schema")
    subjects = [row["subject"] for row in rows]
    values = np.asarray([float(row["global_minus_cross_spectrum_nmae"]) for row in rows], dtype=np.float64)
    if len(set(subjects)) != len(subjects) or not np.isfinite(values).all():
        raise ValueError("subject IDs must be unique and all effects finite")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    positive = int(np.count_nonzero(values > 0))
    negative = int(np.count_nonzero(values < 0))
    zero = int(np.count_nonzero(values == 0))
    loo_means = np.asarray([np.mean(np.delete(values, index)) for index in range(len(values))]) if len(values) > 1 else np.array([])
    mean = float(values.mean())
    checks = {
        "participant_count_matches_summary": bool(len(values) == summary.get("participants")),
        "mean_matches_saved_primary_effect": bool(np.isclose(mean, summary.get("primary_mean_nmae_improvement", np.nan), rtol=0, atol=1e-12)),
        "positive_count_matches_saved_summary": bool(positive == summary.get("participants_improved")),
        "saved_scope_is_prediction_not_source_localization": bool("not source-localization" in summary.get("scope", "")),
        "synthetic_neural_data_not_used_in_original_benchmark": bool(summary.get("synthetic_neural_data_used") is False),
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_type": "post-hoc exploratory sensitivity audit of participant-level saved effects",
        "input_files": {
            "primary_effects_csv": {"sha256": sha256(effects_path), "path": str(effects_path)},
            "summary_json": {"sha256": sha256(summary_path), "path": str(summary_path)},
        },
        "signal_array_accessed": False,
        "unit_of_analysis": "participant",
        "effect_definition": "global-baseline NMAE minus cross-spectrum-model NMAE; positive favors the cross-spectrum model",
        "n_participants": len(values),
        "n_positive": positive,
        "n_negative": negative,
        "n_zero": zero,
        "mean_effect": mean,
        "median_effect": float(np.median(values)),
        "exact_two_sided_sign_flip_pvalue_for_mean": exact_sign_flip_pvalue(values),
        "exact_two_sided_sign_test_pvalue": exact_sign_test_pvalue(positive, positive + negative),
        "leave_one_participant_out_mean_range": [float(loo_means.min()), float(loo_means.max())] if loo_means.size else None,
        "participant_effects": [{"subject": subject, "effect": float(value)} for subject, value in zip(subjects, values)],
        "consistency_checks": checks,
        "interpretation": (
            "The saved mean effect is small and uncertain. These post-hoc participant-level tests are sensitivity summaries, "
            "not confirmatory inference, do not address all modeling uncertainty, and do not validate source localization."
        ),
        "limits": [
            "Reads only derived participant-level metrics and summary metadata; no EEG/iEEG samples, features, or predictions are opened.",
            "The underlying benchmark is exploratory and predicts an intracranial contact-pair signal from scalp features; it is not GBF source-map recovery.",
            "The exact sign-flip test assumes sign exchangeability under its null; the sign test discards effect magnitudes. Both are post hoc.",
        ],
    }
    if not all(checks.values()):
        raise ValueError("saved summary and participant effects failed consistency checks")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    lines = [
        "# ds004752 participant-effect sensitivity audit",
        "",
        "**Status:** exploratory post-hoc sensitivity analysis; no EEG/iEEG samples were read.",
        "",
        f"The saved primary effect is {mean:.6f} normalized-MAE units (median {np.median(values):.6f}); {positive}/{len(values)} participants favor the cross-spectrum model.",
        f"The exact two-sided participant sign-flip test for the mean gives p={report['exact_two_sided_sign_flip_pvalue_for_mean']:.4f}; the exact sign test gives p={report['exact_two_sided_sign_test_pvalue']:.4f}.",
        f"The leave-one-participant-out mean ranges from {loo_means.min():.6f} to {loo_means.max():.6f}.",
        "",
        "These post-hoc summaries do not change the original benchmark's exploratory status. They do not support a confirmatory effect, GBF source-map validation, or a novel method claim. The bootstrap interval in the original summary includes zero.",
        "",
        "Machine-readable values and input hashes are in `sensitivity.json`.",
    ]
    try:
        (stage / "sensitivity.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (stage / "SENSITIVITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        if os.path.lexists(output):
            raise FileExistsError(f"refusing to overwrite result: {output}")
        os.rename(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(json.dumps({key: report[key] for key in (
        "status", "n_participants", "mean_effect", "median_effect",
        "exact_two_sided_sign_flip_pvalue_for_mean", "exact_two_sided_sign_test_pvalue",
        "leave_one_participant_out_mean_range", "signal_array_accessed")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
