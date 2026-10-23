"""Versioned nominal source-signature distinguishability for a fixed EEG model.

This module implements the B2-GBF-v10 forward-signature diagnostic. It is
separate from the upstream GBFs inverse estimator: it compares leadfield
columns directly and makes no claim about physiological source recovery.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DistinguishabilityResult:
    """Float64 pair ranking and metadata for one declared forward model."""

    source_indices: np.ndarray
    candidate_indices: np.ndarray
    absolute_cosine: np.ndarray
    profiled_residual: np.ndarray
    valid_source: np.ndarray
    whitened_norm: np.ndarray
    candidate_count: np.ndarray
    covariance_rank: int


def compute_distinguishability(
    leadfield: np.ndarray,
    noise_covariance: np.ndarray,
    coordinates_m: np.ndarray,
    *,
    minimum_distance_mm: float = 20.0,
    top_k: int = 5,
    block_size: int = 128,
    eigenvalue_rtol: float = 1e-10,
    support_rtol: float = 1e-7,
) -> DistinguishabilityResult:
    """Rank distant source pairs by normalized, covariance-whitened similarity.

    Inputs are only a sensor-by-source forward matrix, sensor noise covariance,
    and source coordinates in metres. Calculations and returned scores use
    float64. The metric is conditional on these inputs and is not a recovery
    probability or an empirical localization-accuracy estimate.
    """
    g = np.asarray(leadfield, dtype=np.float64)
    cov = np.asarray(noise_covariance, dtype=np.float64)
    xyz = np.asarray(coordinates_m, dtype=np.float64)
    if g.ndim != 2 or min(g.shape) < 1 or not np.isfinite(g).all():
        raise ValueError("leadfield must be a finite, nonempty sensors-by-sources matrix")
    n_sensors, n_sources = g.shape
    if cov.shape != (n_sensors, n_sensors) or not np.isfinite(cov).all():
        raise ValueError("noise covariance must be finite and match the leadfield sensor dimension")
    if xyz.shape != (n_sources, 3) or not np.isfinite(xyz).all():
        raise ValueError("coordinates must be finite (n_sources, 3) values in metres")
    if (not np.isfinite(minimum_distance_mm) or minimum_distance_mm < 0
            or not isinstance(top_k, (int, np.integer)) or top_k < 1
            or not isinstance(block_size, (int, np.integer)) or block_size < 1
            or not np.isfinite(eigenvalue_rtol) or eigenvalue_rtol <= 0
            or not np.isfinite(support_rtol) or support_rtol <= 0):
        raise ValueError("distance, top_k, block_size, and tolerances must be positive and finite")
    covariance_scale = max(float(np.linalg.norm(cov)), np.finfo(np.float64).tiny)
    if float(np.linalg.norm(cov - cov.T)) > 1e-8 * covariance_scale:
        raise ValueError("noise covariance is not symmetric within tolerance")
    eigenvalues, eigenvectors = np.linalg.eigh((cov + cov.T) * 0.5)
    spectral_scale = max(float(np.max(np.abs(eigenvalues))), np.finfo(np.float64).tiny)
    if float(eigenvalues.min()) < -eigenvalue_rtol * spectral_scale:
        raise ValueError("noise covariance is not positive semidefinite")
    keep = eigenvalues > eigenvalue_rtol * spectral_scale
    if not keep.any():
        raise ValueError("noise covariance has zero supported rank")
    discarded = eigenvectors[:, ~keep].T @ g
    lead_norm = np.maximum(np.linalg.norm(g, axis=0), np.finfo(np.float64).tiny)
    if np.any(np.linalg.norm(discarded, axis=0) > support_rtol * lead_norm):
        raise ValueError("leadfield has components outside the supported covariance subspace")
    z = (eigenvectors[:, keep].T @ g) / np.sqrt(eigenvalues[keep, None])
    norms = np.linalg.norm(z, axis=0)
    norm_scale = max(float(norms.max()), np.finfo(np.float64).tiny)
    valid = norms > eigenvalue_rtol * norm_scale
    unit = np.zeros_like(z, dtype=np.float64)
    unit[:, valid] = z[:, valid] / norms[valid]

    indices = np.full((n_sources, int(top_k)), -1, dtype=np.int64)
    scores = np.full((n_sources, int(top_k)), np.nan, dtype=np.float64)
    counts = np.zeros(n_sources, dtype=np.int64)
    source_ids = np.arange(n_sources, dtype=np.int64)
    cutoff_m = float(minimum_distance_mm) / 1000.0
    for start in range(0, n_sources, int(block_size)):
        stop = min(start + int(block_size), n_sources)
        similarities = np.clip(np.abs(unit[:, start:stop].T @ unit), 0.0, 1.0)
        distances = np.linalg.norm(xyz[start:stop, None, :] - xyz[None, :, :], axis=2)
        eligible = (distances >= cutoff_m) & valid[None, :] & valid[start:stop, None]
        eligible &= source_ids[start:stop, None] != source_ids[None, :]
        similarities[~eligible] = -np.inf
        for offset, row in enumerate(similarities):
            query = start + offset
            choices = np.flatnonzero(np.isfinite(row))
            counts[query] = len(choices)
            if choices.size:
                order = np.lexsort((choices, -row[choices]))
                selected = choices[order[:int(top_k)]]
                indices[query, :selected.size] = selected
                scores[query, :selected.size] = row[selected]
    has_alternative = valid & (counts > 0)
    if not has_alternative.any():
        raise ValueError("no valid source has an eligible distant alternative")
    residuals = np.full_like(scores, np.nan)
    occupied = np.isfinite(scores)
    residuals[occupied] = np.sqrt(np.maximum(0.0, 1.0 - scores[occupied] ** 2))
    return DistinguishabilityResult(
        source_indices=source_ids,
        candidate_indices=indices,
        absolute_cosine=scores,
        profiled_residual=residuals,
        valid_source=valid,
        whitened_norm=norms,
        candidate_count=counts,
        covariance_rank=int(keep.sum()),
    )


def summarize(result: DistinguishabilityResult, minimum_distance_mm: float) -> dict:
    has_alternative = result.valid_source & (result.candidate_count > 0)
    best = result.absolute_cosine[has_alternative, 0]
    return {
        "source_count": int(len(result.valid_source)),
        "valid_signature_count": int(result.valid_source.sum()),
        "source_count_with_distant_alternative": int(has_alternative.sum()),
        "covariance_rank": result.covariance_rank,
        "minimum_euclidean_separation_mm": float(minimum_distance_mm),
        "top_k": int(result.candidate_indices.shape[1]),
        "median_best_distant_abs_cosine": float(np.median(best)),
        "p90_best_distant_abs_cosine": float(np.quantile(best, 0.9)),
        "fraction_best_abs_cosine_ge_0_95": float(np.mean(best >= 0.95)),
        "fraction_best_abs_cosine_ge_0_99": float(np.mean(best >= 0.99)),
        "interpretation": (
            "Nominal normalized sensor-pattern similarity conditional on one declared "
            "head model, reference, source family, and noise covariance. It is not a "
            "probability of correct localization or evidence of physiological source recovery."
        ),
    }
