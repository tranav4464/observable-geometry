"""Reference-compatible sensor-subset transforms for model-only audits."""
from __future__ import annotations

import numpy as np


def average_reference_subset(
    leadfield: np.ndarray,
    covariance: np.ndarray,
    channel_indices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Select sensors and apply their common-average reference to model arrays.

    This is an algebraic transform of a declared forward model and covariance;
    it does not read or generate neural time series.
    """
    gain = np.asarray(leadfield, dtype=np.float64)
    noise = np.asarray(covariance, dtype=np.float64)
    indices = np.asarray(channel_indices)
    if gain.ndim != 2 or min(gain.shape) < 1 or not np.isfinite(gain).all():
        raise ValueError("leadfield must be a finite, nonempty sensors-by-sources matrix")
    if noise.shape != (gain.shape[0], gain.shape[0]) or not np.isfinite(noise).all():
        raise ValueError("covariance must be finite and match the leadfield sensor dimension")
    if indices.ndim != 1 or indices.size < 2 or not np.issubdtype(indices.dtype, np.integer):
        raise ValueError("channel_indices must be a one-dimensional integer array with at least two entries")
    indices = indices.astype(np.int64, copy=False)
    if np.any(indices < 0) or np.any(indices >= gain.shape[0]) or np.unique(indices).size != indices.size:
        raise ValueError("channel_indices must be unique valid leadfield row indices")

    subset_gain = gain[indices]
    subset_noise = noise[np.ix_(indices, indices)]
    reference = np.eye(indices.size, dtype=np.float64) - np.ones(
        (indices.size, indices.size), dtype=np.float64
    ) / indices.size
    projected_gain = reference @ subset_gain
    projected_noise = reference @ subset_noise @ reference.T
    projected_noise = (projected_noise + projected_noise.T) * 0.5
    return projected_gain, projected_noise
