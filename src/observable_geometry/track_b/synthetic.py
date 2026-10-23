"""Known-truth simulator for the Track B multimodal network task.

This is a transparent simulator, not a reproduction of the authors' exact
synthetic generator. It implements a first-order stable VAR observed through a
scalp mixing operator and a sparse region-selection operator. Generator choices
must be reported with each run.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SyntheticConfig:
    n_regions: int = 69
    n_scalp: int = 128
    n_active_regions: int = 10
    max_indegree: int = 2
    n_ieeg_regions: int = 21
    n_samples: int = 512
    target_radius: float = 0.85
    scalp_snr_db: float = -5.0
    ieeg_snr_db: float = 30.0
    innovation_scale: float = 1.0
    seed: int = 0

    def validate(self) -> None:
        if not isinstance(self.n_regions, int) or self.n_regions < 2:
            raise ValueError("n_regions must be an integer >= 2")
        if not isinstance(self.n_scalp, int) or self.n_scalp < 1:
            raise ValueError("n_scalp must be a positive integer")
        if not isinstance(self.n_active_regions, int) or not 2 <= self.n_active_regions <= self.n_regions:
            raise ValueError("n_active_regions must be between 2 and n_regions")
        if (not isinstance(self.max_indegree, int)
                or not 0 <= self.max_indegree < self.n_active_regions):
            raise ValueError("max_indegree must be between 0 and n_active_regions - 1")
        if not isinstance(self.n_ieeg_regions, int) or not 1 <= self.n_ieeg_regions <= self.n_regions:
            raise ValueError("n_ieeg_regions must be between 1 and n_regions")
        if not isinstance(self.n_samples, int) or self.n_samples < 3:
            raise ValueError("n_samples must be an integer >= 3")
        if not 0 < self.target_radius < 1:
            raise ValueError("target_radius must be in (0, 1) for a stable VAR")
        if not np.isfinite(self.scalp_snr_db) or not np.isfinite(self.ieeg_snr_db):
            raise ValueError("SNR values must be finite")
        if not np.isfinite(self.innovation_scale) or self.innovation_scale <= 0:
            raise ValueError("innovation_scale must be positive and finite")
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError("seed must be a non-negative integer")


@dataclass(frozen=True)
class SyntheticDataset:
    config: SyntheticConfig
    adjacency: np.ndarray
    transition: np.ndarray
    latent: np.ndarray
    scalp_operator: np.ndarray
    ieeg_operator: np.ndarray
    scalp: np.ndarray
    ieeg: np.ndarray
    scalp_noise: np.ndarray
    ieeg_noise: np.ndarray
    active_region_indices: np.ndarray
    ieeg_region_indices: np.ndarray
    realized_snr_db: tuple[float, float]


def _snr_noise(signal: np.ndarray, target_db: float,
               rng: np.random.Generator) -> tuple[np.ndarray, float]:
    """Draw iid Gaussian noise scaled to the requested finite-sample RMS SNR."""
    signal_power = float(np.mean(np.square(signal)))
    if not np.isfinite(signal_power) or signal_power <= np.finfo(float).tiny:
        raise ValueError("observation signal has zero or invalid power")
    raw = rng.standard_normal(signal.shape)
    raw_power = float(np.mean(np.square(raw)))
    desired_noise_power = signal_power / (10.0 ** (target_db / 10.0))
    noise = raw * np.sqrt(desired_noise_power / raw_power)
    return noise, 10.0 * np.log10(signal_power / np.mean(np.square(noise)))


def generate_synthetic(config: SyntheticConfig = SyntheticConfig(), *,
                       scalp_operator: np.ndarray | None = None) -> SyntheticDataset:
    """Generate directed VAR truth and paired scalp/iEEG observations.

    Adjacency uses ``adjacency[target, source]`` and the returned transition
    matrix follows ``x[t] = transition @ x[t-1] + innovation[t]``. Scalp
    observations are ``scalp_operator @ x``; iEEG directly selects chosen
    regions. Exactly ``n_active_regions`` have active network dynamics, with
    ``max_indegree`` incoming edges per active target. SNR is set separately on each observed modality using finite-sample
    RMS power, so the exact requested ratio is reproducible and auditable.
    """
    config.validate()
    rng = np.random.default_rng(config.seed)
    n = config.n_regions

    active_indices = np.sort(rng.choice(n, size=config.n_active_regions, replace=False))
    adjacency = np.zeros((n, n), dtype=np.uint8)
    for target in active_indices:
        candidate_sources = active_indices[active_indices != target]
        sources = rng.choice(candidate_sources, size=config.max_indegree, replace=False)
        adjacency[target, sources] = 1
    coefficients = rng.normal(0.0, 1.0, size=(n, n)) * adjacency
    radius = float(np.max(np.abs(np.linalg.eigvals(coefficients))))
    if radius > np.finfo(float).tiny:
        transition = coefficients * (config.target_radius / radius)
    else:
        transition = coefficients

    latent = np.zeros((config.n_samples, n), dtype=np.float64)
    innovations = config.innovation_scale * rng.standard_normal((config.n_samples - 1, n))
    inactive_mask = np.ones(n, dtype=bool)
    inactive_mask[active_indices] = False
    innovations[:, inactive_mask] = 0.0
    for t in range(1, config.n_samples):
        latent[t] = transition @ latent[t - 1] + innovations[t - 1]

    if scalp_operator is None:
        scalp_operator = rng.normal(0.0, 1.0 / np.sqrt(n),
                                    size=(config.n_scalp, n)).astype(np.float64)
    else:
        scalp_operator = np.asarray(scalp_operator, dtype=np.float64)
        if (scalp_operator.shape != (config.n_scalp, n)
                or not np.all(np.isfinite(scalp_operator))):
            raise ValueError("provided scalp_operator must be finite with shape (n_scalp, n_regions)")
    scalp_signal = latent @ scalp_operator.T
    indices = np.sort(rng.choice(n, size=config.n_ieeg_regions, replace=False))
    ieeg_operator = np.eye(n, dtype=np.float64)[indices]
    ieeg_signal = latent @ ieeg_operator.T

    scalp_noise, scalp_snr = _snr_noise(scalp_signal, config.scalp_snr_db, rng)
    ieeg_noise, ieeg_snr = _snr_noise(ieeg_signal, config.ieeg_snr_db, rng)
    return SyntheticDataset(
        config=config,
        adjacency=adjacency,
        transition=transition,
        latent=latent,
        scalp_operator=scalp_operator,
        ieeg_operator=ieeg_operator,
        scalp=scalp_signal + scalp_noise,
        ieeg=ieeg_signal + ieeg_noise,
        scalp_noise=scalp_noise,
        ieeg_noise=ieeg_noise,
        active_region_indices=active_indices,
        ieeg_region_indices=indices,
        realized_snr_db=(scalp_snr, ieeg_snr),
    )
