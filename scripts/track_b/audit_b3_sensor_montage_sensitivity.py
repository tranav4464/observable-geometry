"""Compare B3 nominal geometry under the full and observed common sensor sets.

Only sealed leadfield/covariance and signature-reference arrays are loaded.
The 224-channel subset is selected from already-recorded channel metadata.
No EEG sample array is requested or materialized.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "track_b"))
from observable_geometry.track_b.distinguishability import compute_distinguishability, summarize  # noqa: E402
from montage_sensitivity import average_reference_subset  # noqa: E402

TRACK_A = ROOT / "outputs/tracka_release_20261022_v2"
EMPIRICAL_REPORT = ROOT / "outputs/20261023T192900Z_b4_matched_224_reproduction/empirical_evaluation_report.json"
PREPARED_ALLOWED = frozenset({"leadfield", "noise_cov"})
SIGNATURE_ALLOWED = frozenset({
    "source_coordinates", "vertex_ids", "candidate_indices", "absolute_cosine",
    "valid_source", "whitened_norm", "distant_candidate_count",
})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_npz_keys(path: Path, allowed: frozenset[str], selected: tuple[str, ...], log: list[dict]) -> dict[str, np.ndarray]:
    values: dict[str, np.ndarray] = {}
    with np.load(path, allow_pickle=False) as archive:
        available = set(archive.files)
        if not set(selected) <= allowed or not set(selected) <= available:
            raise ValueError(f"requested NPZ keys are not permitted or present: {selected}")
        for key in selected:
            log.append({"archive": path.name, "key": key, "decision": "allow"})
            values[key] = np.asarray(archive[key])
    return values


def build_report(out: Path) -> dict:
    manifest_path = TRACK_A / "run_manifest.json"
    track_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    prepared_path = TRACK_A / "prepared_bundle.npz"
    library_path = TRACK_A / "nominal_signature_library.npz"
    relative_prepared = "outputs/tracka_release_20261022_v2/prepared_bundle.npz"
    relative_library = "outputs/tracka_release_20261022_v2/nominal_signature_library.npz"
    expected_hashes = track_manifest["artifact_files_sha256"]
    input_hashes = {
        relative_prepared: sha256(prepared_path),
        relative_library: sha256(library_path),
        "outputs/tracka_release_20261022_v2/run_manifest.json": sha256(manifest_path),
        "outputs/tracka_release_20261022_v2/prepared_bundle.json": sha256(TRACK_A / "prepared_bundle.json"),
        "outputs/20261023T192900Z_b4_matched_224_reproduction/empirical_evaluation_report.json": sha256(EMPIRICAL_REPORT),
    }
    for relative in (relative_prepared, relative_library):
        if input_hashes[relative] != expected_hashes[relative]:
            raise RuntimeError(f"sealed input checksum mismatch: {relative}")

    access_log: list[dict] = []
    prepared = read_npz_keys(prepared_path, PREPARED_ALLOWED, ("leadfield", "noise_cov"), access_log)
    library = read_npz_keys(library_path, SIGNATURE_ALLOWED, (
        "source_coordinates", "vertex_ids", "candidate_indices", "absolute_cosine",
        "valid_source", "whitened_norm", "distant_candidate_count",
    ), access_log)
    gain = np.asarray(prepared["leadfield"], dtype=np.float64)
    covariance = np.asarray(prepared["noise_cov"], dtype=np.float64)
    coords = np.asarray(library["source_coordinates"], dtype=np.float64)
    vertex_ids = np.asarray(library["vertex_ids"], dtype=np.int64)
    if gain.shape != (len(json.loads((TRACK_A / "prepared_bundle.json").read_text(encoding="utf-8"))["channel_names"]), len(vertex_ids)):
        raise ValueError("sealed channel names, leadfield, and vertex IDs do not align")

    channel_names = json.loads((TRACK_A / "prepared_bundle.json").read_text(encoding="utf-8"))["channel_names"]
    empirical = json.loads(EMPIRICAL_REPORT.read_text(encoding="utf-8"))
    common_names = empirical["common_good_channels"]
    if len(channel_names) != 236 or len(common_names) != 224 or len(set(common_names)) != 224:
        raise ValueError("expected the audited 236-channel model and 224 unique common channels")
    common_set = set(common_names)
    if not common_set <= set(channel_names):
        raise ValueError("the 224-channel common set is not contained in the sealed model channels")
    indices = np.asarray([index for index, name in enumerate(channel_names) if name in common_set], dtype=np.int64)
    if [channel_names[index] for index in indices] != [name for name in channel_names if name in common_set]:
        raise AssertionError("channel-order selection failed")

    full = compute_distinguishability(gain, covariance, coords, minimum_distance_mm=20.0, top_k=5)
    subset_gain, subset_cov = average_reference_subset(gain, covariance, indices)
    subset = compute_distinguishability(subset_gain, subset_cov, coords, minimum_distance_mm=20.0, top_k=5)

    reference_indices = np.asarray(library["candidate_indices"], dtype=np.int64)
    reference_scores = np.asarray(library["absolute_cosine"], dtype=np.float64)
    reference_valid = np.asarray(library["valid_source"], dtype=bool)
    reference_norms = np.asarray(library["whitened_norm"], dtype=np.float64)
    reference_counts = np.asarray(library["distant_candidate_count"], dtype=np.int64)
    occupied = full.candidate_indices >= 0
    if not np.array_equal(full.candidate_indices, reference_indices):
        raise AssertionError("236-channel recomputation does not reproduce the sealed ranking")
    if not np.array_equal(full.valid_source, reference_valid) or not np.array_equal(full.candidate_count, reference_counts):
        raise AssertionError("236-channel validity or candidate counts differ from sealed reference")
    score_delta = np.abs(full.absolute_cosine[occupied] - reference_scores[occupied])
    if score_delta.max(initial=0.0) > 1e-7 or not np.allclose(full.whitened_norm, reference_norms, rtol=1e-8, atol=1e-15):
        raise AssertionError("236-channel baseline fails the registered B3 parity tolerances")

    usable = full.valid_source & subset.valid_source & (full.candidate_count > 0) & (subset.candidate_count > 0)
    full_best = full.absolute_cosine[usable, 0]
    subset_best = subset.absolute_cosine[usable, 0]
    full_top = full.candidate_indices[usable]
    subset_top = subset.candidate_indices[usable]
    top1_same = full_top[:, 0] == subset_top[:, 0]
    top5_jaccard = np.asarray([
        len(set(a[a >= 0]) & set(b[b >= 0])) / max(1, len(set(a[a >= 0]) | set(b[b >= 0])))
        for a, b in zip(full_top, subset_top)
    ], dtype=np.float64)
    rho = float(spearmanr(full_best, subset_best).statistic)
    difference = subset_best - full_best
    subset_summary = summarize(subset, 20.0)
    full_summary = summarize(full, 20.0)
    removed = [name for name in channel_names if name not in common_set]
    return {
        "status": "PASS_DESCRIPTIVE_MODEL_ONLY_MONTAGE_SENSITIVITY",
        "scope": "One deterministic comparison of the sealed 236-channel participant-specific model with the actual 224-channel all-run common subset, after applying the corresponding common-average projection to both leadfield and covariance.",
        "data_boundary": "Only leadfield, noise covariance, source coordinates/IDs, sealed B3 comparison arrays, and the already-recorded common-channel metadata were read. No EEG sample array or participant outcome was requested.",
        "source_count": int(len(vertex_ids)),
        "source_vertex_ids_sha256": hashlib.sha256(vertex_ids.tobytes()).hexdigest(),
        "channel_counts": {"full": len(channel_names), "subset": len(indices), "removed": len(removed)},
        "removed_channels": removed,
        "covariance_ranks": {"full": full.covariance_rank, "subset": subset.covariance_rank},
        "full_model_summary": full_summary,
        "subset_model_summary": subset_summary,
        "paired_source_stability": {
            "n_sources": int(usable.sum()),
            "spearman_rho_of_per_source_best_similarity": rho,
            "top_candidate_retained_fraction": float(np.mean(top1_same)),
            "top_five_candidate_jaccard_mean": float(np.mean(top5_jaccard)),
            "top_five_candidate_jaccard_median": float(np.median(top5_jaccard)),
            "best_similarity_difference_subset_minus_full": {
                "median": float(np.median(difference)),
                "p05": float(np.quantile(difference, 0.05)),
                "p95": float(np.quantile(difference, 0.95)),
                "fraction_increased": float(np.mean(difference > 0)),
            },
            "interpretation": "Descriptive spatially dependent source-row summaries; no p-value or population inference is reported.",
        },
        "baseline_parity": {
            "ranking_exact": True,
            "validity_mask_exact": True,
            "eligible_counts_exact": True,
            "max_abs_score_difference_vs_sealed_float32": float(score_delta.max(initial=0.0)),
            "score_tolerance": 1e-7,
            "whitened_norms_allclose": True,
            "norm_rtol": 1e-8,
            "norm_atol": 1e-15,
        },
        "input_sha256": input_hashes,
        "runtime_access_log": access_log,
        "limitations": [
            "This compares one model and one metadata-defined channel subset; it is not a population robustness estimate.",
            "The subset follows an all-run channel-quality intersection and does not represent a conventional reduced EEG montage.",
            "It tests nominal model-conditional geometry only; it does not validate neural source recovery, artifact localization, or analyst decision utility.",
            "This is a descriptive robustness supplement and does not reopen B4-B7 or establish a novel method.",
        ],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="20261024_b3_montage_sensitivity")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs/track_b")
    args = parser.parse_args()
    out = (args.output_root / args.run_id).resolve()
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing run directory: {out}")
    if TRACK_A.resolve() == out or TRACK_A.resolve() in out.parents:
        raise SystemExit("Refusing to write inside sealed Track A")
    out.mkdir(parents=True)
    try:
        report = build_report(out)
        (out / "run_access_log.json").write_text(json.dumps(report.pop("runtime_access_log"), indent=2) + "\n", encoding="utf-8")
        report["runtime_access_log_path"] = "run_access_log.json"
        report_path = out / "sensitivity_report.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        files = [report_path, out / "run_access_log.json"]
        output_hashes = {item.name: sha256(item) for item in files}
        manifest = {
            "schema_version": 1,
            "run_id": args.run_id,
            "command": f"python scripts/track_b/audit_b3_sensor_montage_sensitivity.py --run-id {args.run_id}",
            "algorithm": "B3 nominal pairwise whitened absolute-cosine diagnostic under two sensor/reference contracts",
            "parameters": {"minimum_distance_mm": 20.0, "top_k": 5, "full_channels": 236, "common_subset_channels": 224, "subset_reference": "common average over retained sensors"},
            "inputs_sha256": report["input_sha256"],
            "output_sha256": output_hashes,
            "recorded_eeg_data_key_accessed": False,
            "result": report["paired_source_stability"],
            "claim_boundary": "Model-only descriptive sensor-montage sensitivity. No empirical neural validation, source recovery, decision utility, population inference, or novelty claim.",
        }
        manifest_path = out / "run_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "output": str(out), "report": report_path.as_posix(), "manifest": manifest_path.as_posix(), "summary": report["paired_source_stability"]}, indent=2))
        return 0
    except Exception as exc:
        (out / "failure.json").write_text(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
