"""Hardened independent CPU float64 recomputation for the frozen GBFs B2 check.

This is a validation script, not the reusable Track B API. It deliberately
does not import observable_geometry.nominal and loads only the saved leadfield,
noise covariance, coordinates, and Track A comparison outputs. It never indexes
the recorded ``data`` key in prepared_bundle.npz. Run only after the specified
independent review and resolution of any findings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "outputs" / "tracka_release_20261022_v2"
DEFAULT_OUTPUT = ROOT / "outputs" / "track_b" / "b2_independent_cpu64_REQUIRES_UNIQUE_RUN_ID"
RTOL = 1e-10
SUPPORT_RTOL = 1e-7
SCORE_ABS_TOL = 1e-7
LEGACY_RESIDUAL_ABS_TOL = 1e-7
NORM_RTOL = 1e-8
NORM_ATOL = 1e-15
MIN_DISTANCE_MM = 20.0
TOP_K = 5
BLOCK_SIZE = 128

PREPARED_ALLOWED_KEYS = frozenset({"leadfield", "noise_cov"})
SIGNATURE_ALLOWED_KEYS = frozenset({
    "source_coordinates", "vertex_ids", "candidate_indices", "absolute_cosine",
    "profiled_residual_at_unit_snr", "valid_source", "whitened_norm",
    "distant_candidate_count",
})


class GuardedNPZ:
    """Runtime key allowlist for NPZ reads, with durable attempt logging.

    The guard rejects a disallowed key before delegating to NumPy, so its array
    payload is never materialized. It intentionally exposes no ``files`` or
    generic attribute escape hatch.
    """

    def __init__(self, path: Path, allowed_keys, access_log: Path, run_id: str):
        self.path = Path(path)
        self.allowed_keys = frozenset(allowed_keys)
        self.access_log = Path(access_log)
        self.run_id = run_id
        self._archive = None

    def __enter__(self):
        self._archive = np.load(self.path, allow_pickle=False)
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self._archive is not None:
            self._archive.close()
            self._archive = None

    def _record(self, key: str, allowed: bool):
        event = {
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "archive": self.path.name,
            "key": key,
            "decision": "allow" if allowed else "deny",
        }
        data = (json.dumps(event, sort_keys=True) + "\n").encode("utf-8")
        fd = os.open(self.access_log, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)

    def __getitem__(self, key: str):
        if not isinstance(key, str):
            self._record(repr(key), False)
            raise PermissionError("NPZ runtime guard permits literal string keys only")
        allowed = key in self.allowed_keys
        self._record(key, allowed)
        if not allowed:
            raise PermissionError(f"NPZ runtime guard denied key {key!r} in {self.path.name}")
        if self._archive is None:
            raise RuntimeError("NPZ archive is not open")
        return self._archive[key]


def guarded_npz(path: Path, allowed_keys, access_log: Path, run_id: str):
    return GuardedNPZ(path, allowed_keys, access_log, run_id)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_input_arrays(access_log: Path, run_id: str):
    """Load named model arrays only; do not materialize the EEG ``data`` key."""
    with (TRACK_A / "run_manifest.json").open(encoding="utf-8") as f:
        manifest = json.load(f)
    rels = [
        "outputs/tracka_release_20261022_v2/prepared_bundle.npz",
        "outputs/tracka_release_20261022_v2/nominal_signature_library.npz",
    ]
    for rel in rels:
        path = ROOT / rel
        expected = manifest["artifact_files_sha256"][rel]
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"sealed input hash mismatch: {rel}")

    with guarded_npz(TRACK_A / "prepared_bundle.npz", PREPARED_ALLOWED_KEYS,
                     access_log, run_id) as z:
        # The runtime allowlist rejects any other key before NumPy can load it.
        leadfield = np.asarray(z["leadfield"], dtype=np.float64)
        covariance = np.asarray(z["noise_cov"], dtype=np.float64)
    with guarded_npz(TRACK_A / "nominal_signature_library.npz", SIGNATURE_ALLOWED_KEYS,
                     access_log, run_id) as z:
        coordinates = np.asarray(z["source_coordinates"], dtype=np.float64)
        vertex_ids = np.asarray(z["vertex_ids"], dtype=np.int64)
        # Preserve on-disk dtypes so the parity gate checks the sealed contract.
        reference_indices = np.asarray(z["candidate_indices"])
        reference_scores = np.asarray(z["absolute_cosine"])
        reference_residuals = np.asarray(z["profiled_residual_at_unit_snr"])
        reference_valid = np.asarray(z["valid_source"])
        reference_norms = np.asarray(z["whitened_norm"])
        reference_counts = np.asarray(z["distant_candidate_count"])

    if leadfield.ndim != 2 or covariance.shape != (leadfield.shape[0],) * 2:
        raise ValueError("saved leadfield/covariance dimensions disagree")
    n = leadfield.shape[1]
    if coordinates.shape != (n, 3) or vertex_ids.shape != (n,):
        raise ValueError("saved source coordinates/IDs do not align with leadfield columns")
    if (reference_indices.shape != (n, TOP_K) or reference_scores.shape != (n, TOP_K)
            or reference_residuals.shape != (n, TOP_K)):
        raise ValueError("sealed comparison library shape does not match frozen top-k contract")
    if reference_valid.shape != (n,) or reference_norms.shape != (n,) or reference_counts.shape != (n,):
        raise ValueError("sealed comparison library metadata shape mismatch")
    return manifest, rels, leadfield, covariance, coordinates, vertex_ids, (
        reference_indices, reference_scores, reference_residuals,
        reference_valid, reference_norms, reference_counts
    )


def independent_scores(leadfield: np.ndarray, covariance: np.ndarray, coordinates: np.ndarray):
    """Compute the spec's eigenspace-whitened cosine without production code."""
    if not np.isfinite(leadfield).all() or not np.isfinite(covariance).all() or not np.isfinite(coordinates).all():
        raise ValueError("model arrays contain non-finite values")
    sym_scale = max(float(np.linalg.norm(covariance)), np.finfo(np.float64).tiny)
    if np.linalg.norm(covariance - covariance.T) > 1e-8 * sym_scale:
        raise ValueError("noise covariance is not symmetric within tolerance")
    eigenvalues, eigenvectors = np.linalg.eigh((covariance + covariance.T) * 0.5)
    spectral_scale = max(float(np.max(np.abs(eigenvalues))), np.finfo(np.float64).tiny)
    if float(eigenvalues.min()) < -RTOL * spectral_scale:
        raise ValueError("noise covariance is not positive semidefinite")
    keep = eigenvalues > RTOL * spectral_scale
    if not np.any(keep):
        raise ValueError("noise covariance has zero supported rank")
    discarded = eigenvectors[:, ~keep].T @ leadfield
    lead_norm = np.maximum(np.linalg.norm(leadfield, axis=0), np.finfo(np.float64).tiny)
    if np.any(np.linalg.norm(discarded, axis=0) > SUPPORT_RTOL * lead_norm):
        raise ValueError("leadfield has a component outside covariance support")
    whitened = (eigenvectors[:, keep].T @ leadfield) / np.sqrt(eigenvalues[keep, None])
    norms = np.linalg.norm(whitened, axis=0)
    max_norm = max(float(norms.max()), np.finfo(np.float64).tiny)
    valid = norms > RTOL * max_norm
    unit = np.zeros_like(whitened, dtype=np.float64)
    unit[:, valid] = whitened[:, valid] / norms[valid]

    n = leadfield.shape[1]
    indices = np.full((n, TOP_K), -1, dtype=np.int64)
    scores = np.full((n, TOP_K), np.nan, dtype=np.float64)
    counts = np.zeros(n, dtype=np.int64)
    ids = np.arange(n, dtype=np.int64)
    cutoff_m = MIN_DISTANCE_MM / 1000.0
    for start in range(0, n, BLOCK_SIZE):
        stop = min(start + BLOCK_SIZE, n)
        similarity = np.clip(np.abs(unit[:, start:stop].T @ unit), 0.0, 1.0)
        distance = np.linalg.norm(coordinates[start:stop, None, :] - coordinates[None, :, :], axis=2)
        eligible = (distance >= cutoff_m) & valid[None, :] & valid[start:stop, None]
        eligible &= ids[start:stop, None] != ids[None, :]
        similarity[~eligible] = -np.inf
        for offset, row in enumerate(similarity):
            query = start + offset
            choices = np.flatnonzero(np.isfinite(row))
            counts[query] = len(choices)
            if choices.size:
                order = np.lexsort((choices, -row[choices]))
                selected = choices[order[:TOP_K]]
                indices[query, :selected.size] = selected
                scores[query, :selected.size] = row[selected]
    has_alternative = valid & (counts > 0)
    if not has_alternative.any():
        raise ValueError("no valid source has a distant candidate")
    return {
        "indices": indices,
        "scores": scores,
        "valid": valid,
        "norms": norms,
        "counts": counts,
        "has_alternative": has_alternative,
        "coordinates_m": coordinates,
    }


def compare_sealed(result, reference):
    ref_indices, ref_scores, ref_residuals, ref_valid, ref_norms, ref_counts = reference
    result_indices = np.asarray(result["indices"])
    result_scores = np.asarray(result["scores"])
    result_valid = np.asarray(result["valid"])
    result_norms = np.asarray(result["norms"])
    result_counts = np.asarray(result["counts"])
    n = len(result_valid)
    expected_shape = (n, TOP_K)
    if result_indices.shape != expected_shape or ref_indices.shape != expected_shape:
        raise AssertionError(f"candidate-index arrays must both have shape {expected_shape}")
    if result_scores.shape != expected_shape or ref_scores.shape != expected_shape:
        raise AssertionError(f"score arrays must both have shape {expected_shape}")
    if ref_residuals.shape != expected_shape:
        raise AssertionError(f"sealed residual array must have shape {expected_shape}")
    if result_valid.shape != (n,) or ref_valid.shape != (n,):
        raise AssertionError("valid-source masks must have shape (n_sources,)")
    if result_norms.shape != (n,) or ref_norms.shape != (n,):
        raise AssertionError("whitened-norm arrays must have shape (n_sources,)")
    if result_counts.shape != (n,) or ref_counts.shape != (n,):
        raise AssertionError("candidate-count arrays must have shape (n_sources,)")

    expected_dtypes = {
        "result indices": (result_indices, np.dtype(np.int64)),
        "sealed indices": (ref_indices, np.dtype(np.int32)),
        "result scores": (result_scores, np.dtype(np.float64)),
        "sealed scores": (ref_scores, np.dtype(np.float32)),
        "sealed residuals": (ref_residuals, np.dtype(np.float32)),
        "result valid mask": (result_valid, np.dtype(bool)),
        "sealed valid mask": (ref_valid, np.dtype(bool)),
        "result norms": (result_norms, np.dtype(np.float64)),
        "sealed norms": (ref_norms, np.dtype(np.float64)),
        "result counts": (result_counts, np.dtype(np.int64)),
        "sealed counts": (ref_counts, np.dtype(np.int32)),
    }
    for label, (array, dtype) in expected_dtypes.items():
        if array.dtype != dtype:
            raise AssertionError(f"{label} storage dtype must be {dtype}, got {array.dtype}")

    if not np.isin(ref_indices, np.r_[-1, np.arange(n)]).all():
        raise AssertionError("sealed candidate indices contain an invalid sentinel or source index")
    if not np.isin(result_indices, np.r_[-1, np.arange(n)]).all():
        raise AssertionError("computed candidate indices contain an invalid sentinel or source index")
    if np.any(result_counts < 0) or np.any(ref_counts < 0) or np.any(result_counts > n - 1) or np.any(ref_counts > n - 1):
        raise AssertionError("candidate counts are outside the valid range")

    if not np.array_equal(result["indices"], ref_indices):
        mismatch = np.argwhere(result["indices"] != ref_indices)[0].tolist()
        raise AssertionError(f"top-k source ranking mismatch at row/slot {mismatch}")
    if not np.array_equal(result["valid"], ref_valid):
        raise AssertionError("valid-source mask differs from sealed output")
    if not np.array_equal(result["counts"], ref_counts):
        raise AssertionError("distant-candidate counts differ from sealed output")

    occupied = ref_indices >= 0
    expected_occupied = (np.arange(TOP_K)[None, :] < np.minimum(ref_counts, TOP_K)[:, None])
    expected_occupied &= ref_valid[:, None]
    if not np.array_equal(occupied, expected_occupied):
        raise AssertionError("sealed candidate slots do not match validity and candidate counts")
    result_occupied = result_indices >= 0
    if not np.array_equal(result_occupied, occupied):
        raise AssertionError("computed and sealed occupied candidate slots differ")
    result_score_finite = np.isfinite(result_scores)
    ref_score_finite = np.isfinite(ref_scores)
    ref_residual_finite = np.isfinite(ref_residuals)
    if not np.array_equal(result_score_finite, ref_score_finite):
        raise AssertionError("computed and sealed score finite-value masks differ")
    if not np.array_equal(result_score_finite, occupied) or not np.array_equal(ref_score_finite, occupied):
        raise AssertionError("score finite-value locations do not match occupied candidate slots")
    if not np.array_equal(ref_residual_finite, occupied):
        raise AssertionError("sealed residual finite-value locations do not match occupied candidate slots")
    if not np.isnan(result_scores[~occupied]).all() or not np.isnan(ref_scores[~occupied]).all():
        raise AssertionError("unused score slots must contain NaN sentinels, not infinities or values")
    if not np.isnan(ref_residuals[~occupied]).all():
        raise AssertionError("unused residual slots must contain NaN sentinels, not infinities or values")
    if not np.isfinite(result_norms).all() or not np.isfinite(ref_norms).all() or (result_norms < 0).any() or (ref_norms < 0).any():
        raise AssertionError("whitened norms must be finite and nonnegative")
    if np.any(result_scores[occupied] < 0) or np.any(result_scores[occupied] > 1):
        raise AssertionError("computed cosine scores must lie in [0, 1]")
    if np.any(ref_scores[occupied] < 0) or np.any(ref_scores[occupied] > 1):
        raise AssertionError("sealed cosine scores must lie in [0, 1]")
    if np.any(ref_residuals[occupied] < 0) or np.any(ref_residuals[occupied] > 1):
        raise AssertionError("sealed residuals must lie in [0, 1]")

    score_mask = occupied
    score_delta = np.abs(result_scores[score_mask] - ref_scores[score_mask])
    computed_residuals = np.sqrt(np.maximum(0.0, 1.0 - result_scores ** 2))
    residual_mask = occupied
    legacy_scores = result_scores.astype(np.float32)
    with np.errstate(invalid="ignore"):
        replayed_legacy_residuals = np.sqrt(np.maximum(0.0, 1.0 - legacy_scores ** 2))
    legacy_residual_delta = np.abs(
        replayed_legacy_residuals[residual_mask] - ref_residuals[residual_mask]
    )
    float64_residual_delta = np.abs(computed_residuals[residual_mask] - ref_residuals[residual_mask])
    norm_delta = np.abs(result_norms - ref_norms)
    score_max = float(score_delta.max(initial=0.0))
    legacy_residual_max = float(legacy_residual_delta.max(initial=0.0))
    if score_max > SCORE_ABS_TOL:
        raise AssertionError(f"float64 cosine differs from sealed float32 output by {score_max:g} > {SCORE_ABS_TOL:g}")
    if legacy_residual_max > LEGACY_RESIDUAL_ABS_TOL:
        raise AssertionError(f"replayed float32 residual differs from sealed output by {legacy_residual_max:g} > {LEGACY_RESIDUAL_ABS_TOL:g}")
    if not np.allclose(result_norms, ref_norms, rtol=NORM_RTOL, atol=NORM_ATOL):
        raise AssertionError("whitened norms exceed the preregistered rtol/atol")
    return {
        "ranking_exact_match": True,
        "valid_mask_exact_match": True,
        "candidate_counts_exact_match": True,
        "sealed_float32_score_max_abs_difference": score_max,
        "legacy_float32_residual_replay_max_abs_difference": legacy_residual_max,
        "float64_residual_vs_sealed_float32_max_abs_difference_descriptive": float(float64_residual_delta.max(initial=0.0)),
        "whitened_norm_max_abs_difference": float(norm_delta.max(initial=0.0)),
        "score_abs_tolerance": SCORE_ABS_TOL,
        "legacy_residual_replay_abs_tolerance": LEGACY_RESIDUAL_ABS_TOL,
        "whitened_norm_rtol": NORM_RTOL,
        "whitened_norm_atol": NORM_ATOL,
        "score_comparison_note": "Sealed Track A score storage is float32; this calculation retains float64.",
    }


def summarize(result):
    best = result["scores"][result["has_alternative"], 0]
    residual = np.sqrt(np.maximum(0.0, 1.0 - best * best))
    return {
        "source_count": int(len(result["valid"])),
        "valid_signature_count": int(result["valid"].sum()),
        "source_count_with_distant_alternative": int(result["has_alternative"].sum()),
        "minimum_euclidean_separation_mm": MIN_DISTANCE_MM,
        "top_k": TOP_K,
        "median_best_distant_abs_cosine": float(np.median(best)),
        "p90_best_distant_abs_cosine": float(np.quantile(best, 0.9)),
        "fraction_best_abs_cosine_ge_0_95": float(np.mean(best >= 0.95)),
        "fraction_best_abs_cosine_ge_0_99": float(np.mean(best >= 0.99)),
        "median_profiled_residual_at_unit_whitened_norm": float(np.median(residual)),
        "score_semantics": "Nominal normalized signature similarity under one fixed model/covariance; not calibrated detection or localization uncertainty.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new, empty output directory; never use a Track A path")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    if output == TRACK_A.resolve() or TRACK_A.resolve() in output.parents:
        raise SystemExit("Refusing to write inside the sealed Track A release")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_b2_v11_cpu64"
    access_log = output / "npz_key_access.jsonl"
    manifest, input_rels, leadfield, covariance, coordinates, vertex_ids, reference = load_input_arrays(access_log, run_id)
    result = independent_scores(leadfield, covariance, coordinates)
    comparison = compare_sealed(result, reference)
    summary = summarize(result)
    arrays_path = output / "independent_pairwise_top5_float64.npz"
    np.savez_compressed(
        arrays_path,
        candidate_indices=result["indices"],
        absolute_cosine=result["scores"],
        profiled_residual_at_unit_whitened_norm=np.sqrt(np.maximum(0.0, 1.0 - result["scores"] ** 2)),
        valid_source=result["valid"],
        whitened_norm=result["norms"],
        distant_candidate_count=result["counts"],
        source_coordinates_m=coordinates,
        vertex_ids=vertex_ids,
    )
    inputs = {rel: sha256(ROOT / rel) for rel in input_rels}
    report = {
        "run_type": "B2 independent CPU float64 recomputation from saved real forward-model artifacts",
        "spec_id": "B2-GBF-2026-10-23-v10",
        "spec_sha256": "1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062",
        "verifier_revision": "v11 hardened parity and runtime key allowlists",
        "verifier_sha256": sha256(Path(__file__).resolve()),
        "run_id": run_id,
        "dataset": manifest.get("dataset"),
        "input_sha256": inputs,
        "arrays_accessed": ["prepared_bundle.npz:leadfield", "prepared_bundle.npz:noise_cov", "nominal_signature_library.npz:source_coordinates", "nominal_signature_library.npz:vertex_ids", "nominal_signature_library.npz:sealed comparison arrays"],
        "recorded_eeg_data_key_accessed": False,
        "runtime_access_guard": {
            "status": "PASS",
            "prepared_bundle_allowlist": sorted(PREPARED_ALLOWED_KEYS),
            "signature_library_allowlist": sorted(SIGNATURE_ALLOWED_KEYS),
            "attempt_log": access_log.name,
            "attempt_log_sha256": sha256(access_log),
            "enforcement": "disallowed keys are rejected before NumPy materializes the member array",
            "limitation": "Python runtime guard plus durable per-key log; not an operating-system sandbox",
        },
        "execution": {"device": "CPU", "dtype": "float64", "implementation": "standalone NumPy; does not import observable_geometry.nominal", "rtol_covariance": RTOL, "support_rtol": SUPPORT_RTOL, "score_abs_tolerance": SCORE_ABS_TOL, "legacy_residual_replay_abs_tolerance": LEGACY_RESIDUAL_ABS_TOL, "whitened_norm_rtol": NORM_RTOL, "whitened_norm_atol": NORM_ATOL, "min_distance_mm": MIN_DISTANCE_MM, "top_k": TOP_K, "block_size": BLOCK_SIZE},
        "summary": summary,
        "comparison_to_sealed_track_a": comparison,
        "outputs": {"arrays": arrays_path.name, "arrays_sha256": sha256(arrays_path), "access_log": access_log.name},
        "limitations": ["Uses the existing one-participant development forward model.", "Does not validate physiological source recovery or population performance.", "Comparison library stores its scores in float32; independent outputs remain float64."],
    }
    report_path = output / "independent_recompute_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output), "summary": summary, "comparison": comparison}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
