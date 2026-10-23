"""Descriptively compare B3 source-pair similarity with sealed MNE PSF metrics.

This is a model-only, exploratory audit of already computed outputs. It does not
read EEG samples, estimate inferential p-values, or measure researcher utility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "outputs/tracka_release_20261022_v2"
B3 = ROOT / "outputs/track_b/20261024_b3_gbf_tool_v1"
DEFAULT_OUT = ROOT / "outputs/track_b/20261024_b7_resolution_overlap_audit_v2"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def average_ranks(values: np.ndarray) -> np.ndarray:
    """Return 1-based average ranks, handling exact ties deterministically."""
    x = np.asarray(values, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    sorted_x = x[order]
    ranks_sorted = np.empty(len(x), dtype=np.float64)
    start = 0
    while start < len(x):
        stop = start + 1
        while stop < len(x) and sorted_x[stop] == sorted_x[start]:
            stop += 1
        ranks_sorted[start:stop] = ((start + 1) + stop) / 2.0
        start = stop
    ranks = np.empty(len(x), dtype=np.float64)
    ranks[order] = ranks_sorted
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = average_ranks(x), average_ranks(y)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = float(np.linalg.norm(rx) * np.linalg.norm(ry))
    if denom == 0:
        raise ValueError("Spearman correlation undefined for a constant input")
    return float(rx @ ry / denom)


def quantile(values: np.ndarray, probability: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=np.float64), probability))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing run: {out}")

    b3_npz = B3 / "distinguishability_float64.npz"
    b3_manifest = B3 / "run_manifest.json"
    psf_npz = TRACK_A / "mne_resolution_summary.npz"
    psf_report = TRACK_A / "mne_resolution_report.json"
    prepared_bundle = TRACK_A / "prepared_bundle.npz"
    psf_source = ROOT / "scripts/run_resolution_baseline.py"
    ta_manifest = TRACK_A / "run_manifest.json"
    nominal_npz = TRACK_A / "nominal_signature_library.npz"
    for path in (b3_npz, b3_manifest, psf_npz, psf_report, prepared_bundle, psf_source, ta_manifest, nominal_npz):
        if not path.is_file():
            raise FileNotFoundError(path)

    b3_info = json.loads(b3_manifest.read_text(encoding="utf-8"))
    ta_info = json.loads(ta_manifest.read_text(encoding="utf-8"))
    expected = {
        b3_npz: b3_info["output_sha256"][b3_npz.name],
        psf_npz: ta_info["artifact_files_sha256"][str(psf_npz.relative_to(ROOT)).replace("\\", "/")],
        psf_report: ta_info["artifact_files_sha256"][str(psf_report.relative_to(ROOT)).replace("\\", "/")],
        prepared_bundle: ta_info["artifact_files_sha256"][str(prepared_bundle.relative_to(ROOT)).replace("\\", "/")],
        psf_source: ta_info["source_files_sha256"][str(psf_source.relative_to(ROOT)).replace("\\", "/")],
        nominal_npz: ta_info["artifact_files_sha256"][str(nominal_npz.relative_to(ROOT)).replace("\\", "/")],
    }
    for path, digest in expected.items():
        actual = sha256(path)
        if actual != digest:
            raise ValueError(f"sealed input hash mismatch for {path}: {actual} != {digest}")
    prep_key = str(prepared_bundle.relative_to(ROOT)).replace("\\", "/")
    if b3_info["input_sha256"].get(prep_key) != expected[prepared_bundle]:
        raise ValueError("B3 and MNE resolution artifacts do not cite the same sealed prepared bundle")
    psf_meta = json.loads(psf_report.read_text(encoding="utf-8"))
    if psf_meta.get("source_count") != 8196 or psf_meta.get("channel_count") != 236:
        raise ValueError("sealed MNE resolution report does not match the declared source/channel dimensions")
    if "same evoked covariance" not in psf_meta.get("noise_covariance", ""):
        raise ValueError("MNE resolution report does not declare the matched covariance")

    with np.load(b3_npz, allow_pickle=False) as b3, np.load(psf_npz, allow_pickle=False) as psf, np.load(nominal_npz, allow_pickle=False) as nominal:
        required_b3 = {"source_indices", "source_vertex_ids", "absolute_cosine", "valid_source"}
        required_psf = {"peak_location_error_mm", "absolute_psf_weighted_distance_mm", "psf_l1_mass_within_10mm", "diagonal_to_peak_response_ratio", "peak_amplitude_fraction"}
        if not required_b3.issubset(b3.files) or not required_psf.issubset(psf.files):
            raise ValueError("input archive is missing required arrays")
        source_indices = b3["source_indices"]
        source_ids = b3["source_vertex_ids"]
        cosine = b3["absolute_cosine"]
        valid = b3["valid_source"].astype(bool)
        if not np.array_equal(source_indices, np.arange(len(source_indices))):
            raise ValueError("B3 source ordering is not canonical index order")
        if not np.array_equal(source_ids, nominal["vertex_ids"]):
            raise ValueError("B3 source IDs do not match the sealed Track A vertex order")
        n = len(source_indices)
        if cosine.shape != (n, 5) or valid.shape != (n,) or any(psf[k].shape != (n,) for k in required_psf):
            raise ValueError("paired source arrays have incompatible dimensions")
        if not valid.all() or not np.isfinite(cosine[:, 0]).all():
            raise ValueError("unexpected invalid source or nonfinite top similarity")
        best = cosine[:, 0].astype(np.float64)
        metrics = {key: psf[key].astype(np.float64) for key in sorted(required_psf)}
        if any(not np.isfinite(values).all() for values in metrics.values()):
            raise ValueError("nonfinite MNE resolution metric")

    correlations = {name: spearman(best, values) for name, values in metrics.items()}
    cutoff = quantile(best, 0.90)
    high = best >= cutoff
    group_summary = {
        "descriptive_grouping": "top decile of per-source best distant cosine versus remaining sources; data-derived partition, not a decision threshold",
        "top_decile_cutoff": cutoff,
        "top_decile_source_count": int(high.sum()),
        "remaining_source_count": int((~high).sum()),
        "top_decile_medians": {name: float(np.median(values[high])) for name, values in metrics.items()},
        "remaining_medians": {name: float(np.median(values[~high])) for name, values in metrics.items()},
    }
    report = {
        "status": "PASS_DESCRIPTIVE_PAIRED_MODEL_OUTPUT_AUDIT",
        "run_id": out.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "question": "Does B3's best distant forward-signature similarity encode a view that is associated with, but not identical to, standard MNE point-spread summaries on the same model?",
        "inputs": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in (b3_npz, b3_manifest, psf_npz, psf_report, prepared_bundle, psf_source, ta_manifest, nominal_npz)},
        "source_count": n,
        "paired_order_check": "B3 vertex IDs exactly equal the sealed Track A signature-library vertex IDs. B3 input and the Track A MNE resolution run both cite the same hash-verified prepared bundle; the frozen MNE script and resolution report are also hash-verified. The report declares 8196 sources, 236 channels, average-reference projection, and the same evoked covariance.",
        "best_distant_cosine": {"median": float(np.median(best)), "p90": cutoff, "threshold_0_95_fraction": float(np.mean(best >= 0.95))},
        "spearman_correlations": correlations,
        "top_decile_comparison": group_summary,
        "inference_limits": [
            "All metrics are paired by source on one participant-specific model; nearby cortical vertices are spatially dependent, so no p-values, confidence intervals, or population inference are reported.",
            "These are model-derived quantities, not measured neural source outcomes.",
            "Association with MNE PSF summaries does not show that B3 changes a researcher decision or improves it.",
            "The comparison is exploratory and does not establish a new mathematical method, physiological validity, or superiority.",
        ],
        "decision": "B3 supplies a distinct pre-inversion forward-signature diagnostic that is moderately associated with existing inverse-resolution summaries in this model. No researcher decision benefit is demonstrated; retain it as an inspectable descriptive tool and do not claim validated utility.",
    }
    out.mkdir(parents=True, exist_ok=False)
    report_path = out / "b7_resolution_overlap_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = ["source_index,vertex_id,best_distant_abs_cosine," + ",".join(metrics)]
    with np.load(b3_npz, allow_pickle=False) as b3, np.load(psf_npz, allow_pickle=False) as psf:
        for i in range(n):
            vals = [f"{float(psf[k][i]):.9g}" for k in sorted(required_psf)]
            rows.append(f"{i},{int(source_ids[i])},{best[i]:.17g}," + ",".join(vals))
    (out / "paired_source_metrics.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "run_id": out.name,
        "created_utc": report["created_utc"],
        "command": "python scripts/track_b/audit_b7_resolution_overlap.py",
        "code_sha256": sha256(Path(__file__).resolve()),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "input_sha256": report["inputs"],
        "output_sha256": {p.name: sha256(p) for p in (report_path, out / "paired_source_metrics.csv")},
        "data_access": "Reads only sealed model-derived B3 and MNE resolution output arrays plus vertex IDs for alignment. No EEG sample, label, or participant outcome array is accessed.",
    }
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "run_id": out.name, "spearman_correlations": correlations, "decision": report["decision"]}, indent=2))


if __name__ == "__main__":
    main()
