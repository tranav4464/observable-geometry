"""Noise-aware sensor signature comparisons under a fixed forward model."""
from __future__ import annotations

import numpy as np

from .core import _psd_eigh


def whitened_unit_signatures(leadfield, noise_cov, rtol=1e-10, support_rtol=1e-7):
    """Return normalized noise-whitened signatures and their validity mask.

    A leadfield component in a zero-noise direction is deterministic under the
    supplied covariance. We reject it rather than silently projecting it away.
    """
    lead = np.asarray(leadfield, dtype=float)
    if lead.ndim != 2 or not np.isfinite(lead).all():
        raise ValueError("leadfield must be a finite 2D matrix")
    values, vectors, scale = _psd_eigh(noise_cov, "noise_cov", rtol)
    if lead.shape[0] != len(values):
        raise ValueError("leadfield and noise covariance channel dimensions disagree")
    keep = values > rtol * scale
    if not keep.any():
        raise ValueError("noise covariance has zero supported rank")
    null_component = vectors[:, ~keep].T @ lead
    lead_norm = np.maximum(np.linalg.norm(lead, axis=0), np.finfo(float).tiny)
    if (np.linalg.norm(null_component, axis=0) > support_rtol * lead_norm).any():
        raise ValueError("leadfield has components outside the supported noise-covariance subspace")
    white = (vectors[:, keep].T @ lead) / np.sqrt(values[keep, None])
    norms = np.linalg.norm(white, axis=0)
    valid = norms > rtol * max(float(norms.max()), np.finfo(float).tiny)
    units = np.zeros_like(white)
    units[:, valid] = white[:, valid] / norms[valid]
    return units, valid, norms


def nearest_distant_signatures(leadfield, noise_cov, coordinates, *,
                               min_distance_mm=20.0, top_k=5, block_size=256,
                               collect_above=None):
    """Find similar observable signatures outside a spatial exclusion radius.

    Similarity is absolute cosine in whitened sensor space, treating amplitude
    and polarity as nuisance parameters. ``collect_above`` optionally returns
    complete per-source threshold sets as CSR arrays, in addition to top-k.
    """
    units, valid, norms = whitened_unit_signatures(leadfield, noise_cov)
    xyz = np.asarray(coordinates, dtype=float)
    n = units.shape[1]
    if xyz.shape != (n, 3) or not np.isfinite(xyz).all():
        raise ValueError("coordinates must be finite N x 3 and match source count")
    if (not np.isfinite(min_distance_mm) or min_distance_mm < 0 or
            not isinstance(top_k, (int, np.integer)) or top_k < 1 or
            not isinstance(block_size, (int, np.integer)) or block_size < 1):
        raise ValueError("min_distance_mm >= 0, integer top_k >= 1, and integer block_size >= 1 required")
    if collect_above is not None and (not np.isfinite(collect_above) or not 0 <= collect_above <= 1):
        raise ValueError("collect_above must be None or a finite cosine threshold in [0, 1]")
    indices = np.full((n, int(top_k)), -1, dtype=np.int32)
    correlations = np.full((n, int(top_k)), np.nan, dtype=np.float32)
    alternative_counts = np.zeros(n, dtype=np.int32)
    cutoff = min_distance_mm / 1000.0
    threshold_indptr = [0]
    threshold_indices: list[int] = []
    threshold_correlations: list[float] = []
    source_ids = np.arange(n)
    for start in range(0, n, int(block_size)):
        stop = min(start + int(block_size), n)
        similarity = np.abs(units[:, start:stop].T @ units)
        spatial = np.linalg.norm(xyz[start:stop, None, :] - xyz[None, :, :], axis=2)
        allowed = (spatial >= cutoff) & valid[None, :]
        allowed &= valid[start:stop, None]
        allowed &= source_ids[start:stop, None] != source_ids[None, :]
        similarity[~allowed] = -np.inf
        for local, row in enumerate(similarity):
            source = start + local
            candidates = np.flatnonzero(np.isfinite(row))
            alternative_counts[source] = len(candidates)
            if len(candidates):
                order = np.lexsort((candidates, -row[candidates]))
                chosen = candidates[order[:int(top_k)]]
                indices[source, :len(chosen)] = chosen
                correlations[source, :len(chosen)] = row[chosen]
                if collect_above is not None:
                    accepted = candidates[row[candidates] >= collect_above]
                    accepted = accepted[np.lexsort((accepted, -row[accepted]))]
                    threshold_indices.extend(accepted.tolist())
                    threshold_correlations.extend(row[accepted].tolist())
            if collect_above is not None:
                threshold_indptr.append(len(threshold_indices))
    has_alternative = valid & (alternative_counts > 0)
    if not has_alternative.any():
        raise ValueError("no valid source has a distant candidate signature")
    residual = np.full(correlations.shape, np.nan, dtype=np.float32)
    finite = np.isfinite(correlations)
    residual[finite] = np.sqrt(np.maximum(0.0, 1.0 - correlations[finite] ** 2))
    best = correlations[has_alternative, 0]
    result = {
        "candidate_indices": indices,
        "absolute_cosine": correlations,
        "profiled_residual_at_unit_snr": residual,
        "valid_source": valid,
        "whitened_norm": norms,
        "distant_candidate_count": alternative_counts,
        "summary": {
            "source_count": int(n),
            "valid_signature_count": int(valid.sum()),
            "source_count_with_distant_alternative": int(has_alternative.sum()),
            "min_exclusion_distance_mm": float(min_distance_mm),
            "top_k": int(top_k),
            "median_best_distant_abs_cosine": float(np.median(best)),
            "p90_best_distant_abs_cosine": float(np.quantile(best, .9)),
            "fraction_best_distant_abs_cosine_ge_0_95": float(np.mean(best >= .95)),
            "fraction_best_distant_abs_cosine_ge_0_99": float(np.mean(best >= .99)),
            "distant_candidate_count_min": int(alternative_counts[has_alternative].min()),
            "distant_candidate_count_max": int(alternative_counts[has_alternative].max()),
            "interpretation": "Nominal topographic similarity conditional on this head model, reference, and noise covariance; not calibrated source-location uncertainty.",
        },
    }
    if collect_above is not None:
        result["threshold_set"] = {
            "threshold": float(collect_above),
            "indptr": np.asarray(threshold_indptr, dtype=np.int64),
            "indices": np.asarray(threshold_indices, dtype=np.int32),
            "absolute_cosine": np.asarray(threshold_correlations, dtype=np.float32),
        }
    return result
