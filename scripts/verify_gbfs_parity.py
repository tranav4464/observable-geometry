"""Independently re-evaluate GBFs recorded-data algebra on the saved inputs."""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
from tracka_paths import OUT


def main():
    with np.load(OUT / "prepared_bundle.npz", allow_pickle=False) as b:
        x, lead, phi, cov = [b[k] for k in ("data", "leadfield", "basis", "noise_cov")]
    with np.load(OUT / "recorded_estimates.npz", allow_pickle=False) as e:
        expected = e["upstream_gbfs_source"]
        eigenvalues = e["geometric_eigenvalues"].copy()
    if eigenvalues.size != phi.shape[1] or phi.shape[1] % 2:
        raise ValueError("geometric eigenvalues and two-hemisphere basis disagree")
    half = phi.shape[1] // 2
    # Preserve the upstream code's first-mode replacement and inv-log penalty.
    eigenvalues[0] = eigenvalues[1]
    eigenvalues[half] = eigenvalues[half + 1]
    with np.errstate(divide="raise", invalid="raise"):
        penalty = -1.0 / np.log(eigenvalues)
    values, vectors = np.linalg.eigh((cov + cov.T) / 2)
    keep = values > 1e-10 * values.max()
    whitener = vectors[:, keep].T / np.sqrt(values[keep, None])
    whitened_data = whitener @ x
    data_scale = float(np.std(whitened_data))
    y = whitened_data / data_scale
    whitened_lead = whitener @ lead
    row_norm = np.linalg.norm(whitened_lead, axis=1)
    if (row_norm <= 0).any():
        raise ValueError("upstream row normalization contains a zero row")
    normalized_lead = whitened_lead / row_norm[:, None]
    gain = normalized_lead @ phi
    lam = 1.2
    system = gain.T @ gain + lam * np.diag(penalty)
    theta = np.linalg.solve(system, gain.T @ y)
    reproduced = phi @ theta * data_scale
    abs_error = float(np.max(np.abs(reproduced - expected)))
    rel_error = float(np.linalg.norm(reproduced - expected) /
                      max(np.linalg.norm(expected), np.finfo(float).tiny))
    report = {
        "status": "independent algebraic parity check passed" if rel_error < 1e-7 else "parity mismatch",
        "scope": "same saved data, forward, basis, covariance, eigenvalues, and Lambda=1.2; not reproduction of the GBFs paper benchmark",
        "lambda": lam, "noise_rank": int(keep.sum()), "max_abs_difference": abs_error,
        "relative_frobenius_difference": rel_error,
        "penalty_min": float(penalty.min()), "penalty_max": float(penalty.max()),
        "penalty_eigenvalues_below_one": int(np.sum(eigenvalues < 1)),
        "penalty_eigenvalues_above_one": int(np.sum(eigenvalues > 1)),
        "relative_tolerance": 1e-7,
        "note": "Direct solve was used for numerical stability in this independent check; upstream uses an explicit inverse.",
    }
    (OUT / "gbfs_parity.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if rel_error >= 1e-7:
        raise SystemExit("Independent GBFs parity check exceeded tolerance")


if __name__ == "__main__":
    main()
