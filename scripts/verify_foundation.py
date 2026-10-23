"""Validate and optionally seal a complete Track A run directory."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import zipfile

import mne
import numpy as np
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[1]
from tracka_paths import OUT, RUN_ID
from geometry_basis_cache import load_or_compute, sha256_file
from observable_geometry.nominal import nearest_distant_signatures


def strict_json(path: Path):
    def reject(value):
        raise ValueError(f"Non-standard/nonfinite JSON number {value} in {path}")
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)


def validate_empirical_rows(rows: list[dict], summary: dict) -> None:
    """Reject nonfinite site errors and summaries that do not derive from rows."""
    if len(rows) != 6:
        raise ValueError("Expected exactly six frozen primary sites")
    gbfs = np.asarray([r["GBFs_peak_error_mm"] for r in rows], dtype=float)
    mne_errors = np.asarray([r["MNE_peak_error_mm"] for r in rows], dtype=float)
    if not np.isfinite(gbfs).all() or not np.isfinite(mne_errors).all():
        raise ValueError("Empirical site-level localization errors must all be finite")
    if (gbfs < 0).any() or (mne_errors < 0).any():
        raise ValueError("Empirical site-level localization errors must be nonnegative")
    identities = [r.get("condition") for r in rows]
    if all(identity is not None for identity in identities) and len(set(identities)) != len(identities):
        raise ValueError("Empirical primary site identities must be unique")
    for key, values in (("GBFs", gbfs), ("MNE", mne_errors)):
        for statistic, actual in (("median", float(np.median(values))), ("mean", float(np.mean(values)))):
            reported = float(summary[f"{key}_{statistic}"])
            if not np.isfinite(reported) or not np.isclose(reported, actual, rtol=1e-10, atol=1e-10):
                raise ValueError(f"{key} {statistic} does not match site-level errors")


def validate_signature_arrays(z, threshold_z, expected_count=8196) -> None:
    n = len(z["source_coordinates"])
    if n != expected_count:
        raise ValueError(f"Expected {expected_count} source vertices; got {n}")
    for prefix in ("", "raw_"):
        ids = z[prefix + "candidate_indices"]
        scores = z[prefix + "absolute_cosine"]
        if ids.shape != (n, 5) or scores.shape != (n, 5):
            raise ValueError(f"{prefix}signature arrays must have shape (N, 5)")
        if ((ids < -1) | (ids >= n)).any():
            raise ValueError("Candidate index outside valid source range")
        if np.any((ids == -1) != np.isnan(scores)):
            raise ValueError("Missing candidate IDs and missing scores must use -1/NaN together")
        valid = z["valid_source"].astype(bool)
        if np.isfinite(scores[~valid]).any():
            raise ValueError("Invalid query source was assigned a plausible-looking similarity")
        finite = np.isfinite(scores)
        if not np.isfinite(scores[finite]).all() or ((scores[finite] < -1e-7) | (scores[finite] > 1.000001)).any():
            raise ValueError("Signature cosine is nonfinite or outside [0, 1]")
        if prefix == "":
            residual = z["profiled_residual_at_unit_snr"]
            if residual.shape != scores.shape or np.any(np.isfinite(residual) != finite):
                raise ValueError("Residual validity mask does not match candidate scores")
            expected_residual = np.sqrt(np.maximum(0, 1 - scores[finite] ** 2))
            if not np.allclose(residual[finite], expected_residual, rtol=1e-6, atol=1e-7):
                raise ValueError("Profiled residual does not match the reported cosine")
            coordinates = z["source_coordinates"]
            for i in range(n):
                row_ids = ids[i, ids[i] >= 0]
                row_scores = scores[i, np.isfinite(scores[i])]
                if len(row_ids) != len(np.unique(row_ids)) or np.any(row_ids == i):
                    raise ValueError("Top-k candidates contain a duplicate or self-match")
                if len(row_ids) > 1 and np.any(np.diff(row_scores) > 1e-6):
                    raise ValueError("Top-k candidates are not sorted by descending similarity")
                if len(row_ids) and np.any(np.linalg.norm(coordinates[row_ids] - coordinates[i], axis=1) < .020 - 1e-7):
                    raise ValueError("Top-k candidates violate the 20 mm exclusion")
    indptr, indices, scores = (threshold_z[k] for k in ("indptr", "indices", "absolute_cosine"))
    if (indptr.shape != (n + 1,) or indptr[0] != 0 or indptr[-1] != len(indices) or
            len(indices) != len(scores) or np.any(np.diff(indptr) < 0)):
        raise ValueError("Threshold ambiguity set has invalid CSR structure")
    if ((indices < 0) | (indices >= n)).any() or not np.isfinite(scores).all():
        raise ValueError("Threshold ambiguity set contains invalid candidates or scores")
    threshold = float(threshold_z["threshold"].item())
    if not np.isclose(threshold, .95, rtol=0, atol=1e-12) or (scores < threshold - 1e-6).any():
        raise ValueError("Threshold ambiguity set includes a below-threshold score")
    coords = z["source_coordinates"]
    for i in range(n):
        lo, hi = int(indptr[i]), int(indptr[i + 1])
        row_ids = indices[lo:hi]
        row_scores = scores[lo:hi]
        if not z["valid_source"][i] and len(row_ids):
            raise ValueError("Invalid source has a threshold ambiguity set")
        if np.any(row_ids == i) or len(np.unique(row_ids)) != len(row_ids):
            raise ValueError("Threshold ambiguity row contains self-match or duplicate")
        if len(row_ids) > 1 and np.any(np.diff(row_scores) > 1e-6):
            raise ValueError("Threshold ambiguity row is not sorted by descending similarity")
        if len(row_ids) and np.any(np.linalg.norm(coords[row_ids] - coords[i], axis=1) < .020 - 1e-7):
            raise ValueError("Threshold ambiguity set contains a source inside the 20 mm exclusion")


def _hashes(paths):
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path) for path in paths}


def _source_files():
    roots = [ROOT / "src", ROOT / "scripts", ROOT / "tests", ROOT / "docs"]
    files = [p for directory in roots for p in directory.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    files += [ROOT / name for name in ("README.md", "requirements-foundation.txt", "pyproject.toml", "REVIEW.html")]
    return sorted(set(files), key=lambda p: str(p).lower())


def _build_source_snapshot(path: Path):
    files = _source_files()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for item in files:
            info = zipfile.ZipInfo(item.relative_to(ROOT).as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, item.read_bytes())
    return files


def verify_source_snapshot(path: Path, expected_hashes: dict[str, str]) -> None:
    """Verify sealed archive contents against its manifest, independent of the live tree."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected_hashes):
            raise ValueError("Source snapshot inventory disagrees with manifest")
        if not any(name.startswith("tests/") and name.endswith(".py") for name in names):
            raise ValueError("Source snapshot omits executable test sources")
        for name in names:
            if name.startswith("/") or ".." in Path(name).parts or "\\" in name:
                raise ValueError(f"Unsafe source snapshot member: {name}")
            if hashlib.sha256(archive.read(name)).hexdigest() != expected_hashes[name]:
                raise ValueError(f"Source snapshot member hash mismatch: {name}")


def validate(out: Path, *, seal: bool = False, check_worktree: bool = False) -> dict:
    if seal and ((out / "run_manifest.json").exists() or (out / "tracka_source_snapshot.zip").exists()):
        raise ValueError("Run already sealed or snapshot exists; choose a fresh run ID")
    required = [
        "environment_report.json", "prepared_bundle.npz", "prepared_bundle.json", "recorded_estimates.npz",
        "report.json", "foundation_report.html", "foundation_report.json", "nominal_signature_library.npz",
        "nominal_ambiguity_threshold_095.npz", "nominal_ambiguity_pairs.csv", "gbfs_parity.json",
        "mne_minimum_norm.json", "mne_minimum_norm_preview.npz", "mne_resolution_report.json",
        "mne_resolution_summary.npz", "sensitivity_report.json", "case_validation.json",
        "empirical_evaluation_report.json", "empirical_evaluation_report.html",
        "predicted_observed_similarity.csv", "basis_20_per_hemisphere.npz", "basis_300_per_hemisphere.npz",
    ]
    missing = [name for name in required if not (out / name).is_file()]
    if missing:
        raise ValueError("Missing expected foundation artifacts: " + ", ".join(missing))
    env = strict_json(out / "environment_report.json")
    req_hash = sha256_file(ROOT / "requirements-foundation.txt")
    if (env["status"] != "PASS" or env["pinned_package_count"] != 34 or
            env["requirements_sha256"] != req_hash or env["python_version"].split(".")[:2] != ["3", "12"] or
            not env["is_virtual_environment"]):
        raise ValueError("Environment report does not certify Python 3.12, a venv, and all exact current pins")
    report = strict_json(out / "foundation_report.json")
    pilot = strict_json(out / "report.json")
    parity = strict_json(out / "gbfs_parity.json")
    resolution = strict_json(out / "mne_resolution_report.json")
    sensitivity = strict_json(out / "sensitivity_report.json")
    case = strict_json(out / "case_validation.json")
    empirical = strict_json(out / "empirical_evaluation_report.json")
    if pilot["subject"] != report["participant"] or pilot["run"] != report["run"]:
        raise ValueError("Report provenance disagrees with the recorded-data manifest")
    with np.load(out / "prepared_bundle.npz", allow_pickle=False) as b:
        channels = b["data"].shape[0]
        if b["data"].ndim != 2 or b["leadfield"].shape[0] != channels or b["noise_cov"].shape != (channels, channels):
            raise ValueError("Prepared bundle channel dimensions disagree")
        if not all(np.isfinite(b[key]).all() for key in ("data", "leadfield", "basis", "noise_cov", "noise_cov_single_trial", "prior_cov")):
            raise ValueError("Prepared bundle contains nonfinite values")
    with np.load(out / "nominal_signature_library.npz", allow_pickle=False) as z, \
            np.load(out / "nominal_ambiguity_threshold_095.npz", allow_pickle=False) as tz:
        validate_signature_arrays(z, tz)
        threshold_set_edges = int(len(tz["indices"]))
        summary = report["analysis"]
        if (summary["valid_signature_count"] != int(z["valid_source"].sum()) or
                summary["source_count_with_distant_alternative"] != int(np.sum(z["distant_candidate_count"] > 0))):
            raise ValueError("Signature summaries do not match source-level arrays")
        best = z["absolute_cosine"][:, 0]
        best = best[np.isfinite(best)]
        if (not np.isclose(summary["median_best_distant_abs_cosine"], np.median(best), atol=1e-7) or
                not np.isclose(summary["p90_best_distant_abs_cosine"], np.quantile(best, .9), atol=1e-7)):
            raise ValueError("Signature median or 90th percentile does not recompute from saved rows")
        with np.load(out / "prepared_bundle.npz", allow_pickle=False) as bundle:
            current = nearest_distant_signatures(bundle["leadfield"], bundle["noise_cov"],
                z["source_coordinates"], min_distance_mm=20, top_k=5, block_size=256,
                collect_above=.95)
            raw = nearest_distant_signatures(bundle["leadfield"], np.eye(bundle["leadfield"].shape[0]),
                z["source_coordinates"], min_distance_mm=20, top_k=5, block_size=256)
        for key in ("candidate_indices", "absolute_cosine", "profiled_residual_at_unit_snr", "valid_source", "distant_candidate_count"):
            if not np.allclose(current[key], z[key], rtol=1e-6, atol=1e-7, equal_nan=True):
                raise ValueError(f"Saved nominal output does not reproduce from its inputs: {key}")
        for key, stored in (("candidate_indices", z["raw_candidate_indices"]),
                            ("absolute_cosine", z["raw_absolute_cosine"])):
            if not np.allclose(raw[key], stored, rtol=1e-6, atol=1e-7, equal_nan=True):
                raise ValueError(f"Saved raw comparator does not reproduce: {key}")
        saved_threshold = {key: tz[key] for key in ("indptr", "indices", "absolute_cosine")}
        for key, stored in saved_threshold.items():
            if not np.allclose(current["threshold_set"][key], stored, rtol=1e-6, atol=1e-7, equal_nan=True):
                raise ValueError(f"Complete threshold set does not reproduce: {key}")
    with (out / "nominal_ambiguity_pairs.csv").open(encoding="utf-8", newline="") as stream:
        pair_rows = list(csv.DictReader(stream))
    if (len(pair_rows) != 20 or any(not np.isfinite(float(r["rho"])) or not 0 <= float(r["rho"]) <= 1 or
                                    float(r["mm"]) < 20 for r in pair_rows)):
        raise ValueError("Top-pair table is missing pairs or has invalid metrics")
    if parity["status"] != "independent algebraic parity check passed" or parity["relative_frobenius_difference"] >= 1e-7:
        raise ValueError("Independent GBFs algebraic parity is missing or outside tolerance")
    if resolution["source_count"] != 8196:
        raise ValueError("MNE resolution summary does not cover the full source grid")
    if "median_psf_l1_mass_within_10mm" not in resolution or "median_psf_energy_within_10mm" in resolution:
        raise ValueError("Point-spread concentration metric is mislabeled or stale")
    if len(sensitivity["variants"]) != 3:
        raise ValueError("Sensitivity report variants are incomplete")
    if case["status"] != "PASS" or case["channel_contract"]["forward_vs_electrode_position_max_error_mm"] > 0.1:
        raise ValueError("Physical channel geometry or case contract failed")
    if case["source_target"]["transform_roundtrip_error_mm"] > 1e-6:
        raise ValueError("Source-target coordinate transform failed")
    rows = empirical["localization_errors"]
    validate_empirical_rows(rows, empirical["summary_error_mm"])
    if len(empirical["pair_similarity_rows"]) != 15 or len(empirical["per_run"]) != 11:
        raise ValueError("Empirical evaluation must report all six-site pairs and eleven run sensitivities")
    site_names = [r["condition"] for r in rows]
    if len(set(site_names)) != 6:
        raise ValueError("Empirical primary site identities must be unique")
    pair_identities = [frozenset((r["site_a"], r["site_b"])) for r in empirical["pair_similarity_rows"]]
    if (any(len(pair) != 2 or not pair.issubset(site_names) for pair in pair_identities) or
            len(set(pair_identities)) != 15):
        raise ValueError("Empirical pair identities do not cover the unique six-site pairs")
    pair_values = np.asarray([[r["predicted_signature_similarity"], r["observed_artifact_similarity"]]
                              for r in empirical["pair_similarity_rows"]], dtype=float)
    if not np.isfinite(pair_values).all() or ((pair_values < 0) | (pair_values > 1)).any():
        raise ValueError("Empirical similarity rows contain invalid values")
    aggregates = empirical["predicted_vs_observed_pair_similarity"]
    for name, actual in (("pearson_r", pearsonr(pair_values[:, 0], pair_values[:, 1]).statistic),
                         ("spearman_rho", spearmanr(pair_values[:, 0], pair_values[:, 1]).statistic)):
        if not np.isfinite(actual) or not np.isclose(float(aggregates[name]), actual, rtol=1e-9, atol=1e-9):
            raise ValueError(f"Empirical {name} does not recompute from pair rows")
    for label, item in empirical["per_run"].items():
        for key in ("gbfs_peak_error_mm", "mne_peak_error_mm", "midpoint_to_cortical_grid_mm"):
            if key not in item or not np.isfinite(item[key]):
                raise ValueError(f"Nonfinite/missing per-run metric in run {label}: {key}")
    if empirical["GBFs"]["modes_per_hemisphere"] != 300:
        raise ValueError("Empirical GBFs configuration differs from frozen setting")
    html = (out / "foundation_report.html").read_text(encoding="utf-8")
    for marker in ('id="signatures"', "D.sensor_signatures", "median_psf_l1_mass_within_10mm"):
        if marker not in html:
            raise ValueError(f"Interactive report is missing required feature: {marker}")
    if "median_psf_energy_within_10mm" in html:
        raise ValueError("Interactive report contains stale point-spread energy label")
    with (out / "predicted_observed_similarity.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    if len(csv_rows) != len(empirical["pair_similarity_rows"]):
        raise ValueError("CSV and JSON empirical pair outputs disagree")
    for csv_row, json_row in zip(csv_rows, empirical["pair_similarity_rows"]):
        for key in ("site_a", "site_b"):
            if csv_row[key] != json_row[key]:
                raise ValueError("CSV and JSON empirical pair identities disagree")
        for key in ("predicted_signature_similarity", "observed_artifact_similarity"):
            if not np.isclose(float(csv_row[key]), float(json_row[key]), rtol=1e-12, atol=1e-12):
                raise ValueError("CSV and JSON empirical pair values disagree")
    # Revalidate the geometry basis identities against current inputs, not just
    # the metadata embedded in each cache.
    fwd_path = ROOT / "data/payload/derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif"
    vendor_path = ROOT / "vendor/GBFs/utils/seeg_with_eeg.py"
    fwd = mne.read_forward_solution(fwd_path, verbose="ERROR")
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True, use_cps=True, verbose="ERROR")
    for modes in (20, 300):
        cache = out / f"basis_{modes}_per_hemisphere.npz"
        _, identity = load_or_compute(cache, fwd_path, vendor_path, fwd["src"], modes, None)
        expected_identity = pilot.get("basis_cache_identity") if modes == 20 else empirical["GBFs"].get("basis_cache_identity")
        if identity != expected_identity:
            raise ValueError(f"Report/cache identity mismatch for {modes}-mode basis")
    # Verify source file hashes captured by empirical evaluation for every run.
    for run_id, details in empirical["per_run"].items():
        run_path = ROOT / "data/payload/derivatives/epochs/sub-01/eeg" / f"sub-01_task-seegstim_run-{int(run_id):02d}_epochs.npy"
        if details.get("epochs_sha256") != sha256_file(run_path):
            raise ValueError(f"Input hash mismatch for Localize-MI run {run_id}")
    result = {"status": "PASS", "run_id": RUN_ID, "participant": report["participant"],
              "run": report["run"], "channels": channels, "vertices": 8196,
              "top_pairs": len(pair_rows), "empirical_sites": len(rows),
              "empirical_runs": len(empirical["per_run"]), "threshold_set_edges": threshold_set_edges,
              "python_version": env["python_version"], "runtime_memory": report["signature_generation_performance"],
              "html_bytes": (out / "foundation_report.html").stat().st_size}
    if seal:
        source_zip = out / "tracka_source_snapshot.zip"
        source_files = _build_source_snapshot(source_zip)
        input_files = [f for base in (ROOT / "data/Localize-MI", ROOT / "data/payload")
                       for f in base.rglob("*") if f.is_file()]
        input_files.append(vendor_path)
        artifact_files = [p for p in out.iterdir() if p.is_file() and p.name != "run_manifest.json"]
        manifest = {
            "status": "SEALED", "run_id": RUN_ID, "created_utc": "2026-10-22",
            "claim_boundary": "single-participant descriptive stimulation-pulse-artifact benchmark; not physiology validation",
            "environment": env, "dataset_metadata_commit": "d7a123d3067213281f106b343c71f28c30e4dd60",
            "upstream_gbfs_commit": "99fc7c6e8afbd2e3e68a700c5f1fa1483b90f49e",
            "source_snapshot_sha256": sha256_file(source_zip),
            "source_files_sha256": _hashes(source_files), "input_files_sha256": _hashes(input_files),
            "artifact_files_sha256": _hashes(artifact_files),
            "protocol": {"primary_runs": [1, 3, 5, 6, 8, 10], "all_runs": list(range(1, 12)),
                         "GBFs_modes_per_hemisphere": 300, "ambiguity_cosine_threshold": .95,
                         "minimum_pair_distance_mm": 20.0, "artifact_window_s": [-.002, .002]},
            "performance": report["signature_generation_performance"],
        }
        verify_source_snapshot(source_zip, manifest["source_files_sha256"])
        (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        result["sealed_manifest"] = str(out / "run_manifest.json")
    else:
        manifest_path = out / "run_manifest.json"
        if not manifest_path.is_file():
            raise ValueError("Run manifest is absent; invoke verify_foundation.py --seal first")
        manifest = strict_json(manifest_path)
        if manifest["status"] != "SEALED" or manifest["run_id"] != RUN_ID:
            raise ValueError("Run manifest identity/status mismatch")
        for name, expected in manifest["artifact_files_sha256"].items():
            path = ROOT / name
            if not path.is_file() or sha256_file(path) != expected:
                raise ValueError(f"Sealed artifact hash mismatch: {name}")
        for name, expected in manifest["input_files_sha256"].items():
            path = ROOT / name
            if not path.is_file() or sha256_file(path) != expected:
                raise ValueError(f"Sealed input hash mismatch: {name}")
        if sha256_file(out / "tracka_source_snapshot.zip") != manifest["source_snapshot_sha256"]:
            raise ValueError("Sealed source snapshot hash mismatch")
        verify_source_snapshot(out / "tracka_source_snapshot.zip", manifest["source_files_sha256"])
        if check_worktree:
            for name, expected in manifest["source_files_sha256"].items():
                path = ROOT / name
                if not path.is_file() or sha256_file(path) != expected:
                    raise ValueError(f"Current worktree differs from sealed source: {name}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seal", action="store_true", help="write a hashed run manifest after all checks pass")
    parser.add_argument("--check-worktree", action="store_true", help="also require the live source files to match the sealed snapshot")
    args = parser.parse_args()
    try:
        result = validate(OUT, seal=args.seal, check_worktree=args.check_worktree)
    except Exception as error:
        raise SystemExit(f"FAIL: {error}") from error
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
