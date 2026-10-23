"""Independent dense-posterior and known-truth checks for the WBEN K=1 core."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from observable_geometry.track_b.wben import fit_wben_k1, kalman_rts_smoother


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dense_posterior(a, q, h, r, y):
    """Form p(x_0:T | y_0:T) by dense covariance conditioning."""
    t_count, m = y.shape
    n = a.shape[0]
    prior = np.zeros((t_count*n, t_count*n))
    prior[:n, :n] = np.eye(n)
    for t in range(1, t_count):
        prior[t*n:(t+1)*n, t*n:(t+1)*n] = a @ prior[(t-1)*n:t*n, (t-1)*n:t*n] @ a.T + q
        for s in range(t):
            cross = a @ prior[(t-1)*n:t*n, s*n:(s+1)*n]
            prior[t*n:(t+1)*n, s*n:(s+1)*n] = cross
            prior[s*n:(s+1)*n, t*n:(t+1)*n] = cross.T
    g = np.kron(np.eye(t_count), h)
    obs_cov = g @ prior @ g.T + np.kron(np.eye(t_count), r)
    gain = np.linalg.solve(obs_cov, g @ prior).T
    mean = gain @ y.reshape(-1)
    covariance = prior - gain @ g @ prior
    return mean.reshape(t_count, n), covariance, obs_cov


def main() -> None:
    # Deterministic tiny exact fixture, independent of the production smoother.
    a = np.array([[0.55, 0.12], [-0.08, 0.35]])
    q = np.diag([0.25, 0.4])
    h = np.array([[1.0, 0.35], [-0.2, 0.8]])
    r = np.diag([0.12, 0.2])
    y = np.array([[0.2, -0.1], [0.4, 0.15], [-0.25, 0.3], [0.1, 0.5]])
    actual = kalman_rts_smoother(y, a, q, h, r)
    dense_mean, dense_cov, dense_obs_cov = dense_posterior(a, q, h, r, y)
    n, t_count = a.shape[0], y.shape[0]
    errors = {
        "smoothed_mean_max_abs": float(np.max(np.abs(actual.smoothed_mean - dense_mean))),
        "smoothed_covariance_max_abs": 0.0,
        "adjacent_cross_covariance_max_abs": 0.0,
    }
    for t in range(t_count):
        errors["smoothed_covariance_max_abs"] = max(
            errors["smoothed_covariance_max_abs"],
            float(np.max(np.abs(actual.smoothed_covariance[t] - dense_cov[t*n:(t+1)*n, t*n:(t+1)*n]))),
        )
    for t in range(t_count - 1):
        errors["adjacent_cross_covariance_max_abs"] = max(
            errors["adjacent_cross_covariance_max_abs"],
            float(np.max(np.abs(actual.cross_covariance[t] - dense_cov[(t+1)*n:(t+2)*n, t*n:(t+1)*n]))),
        )
    sign, logdet = np.linalg.slogdet(dense_obs_cov)
    if sign <= 0:
        raise AssertionError("dense observation covariance is not positive definite")
    dense_ll = -0.5 * (y.size*np.log(2*np.pi) + logdet + y.reshape(-1) @ np.linalg.solve(dense_obs_cov, y.reshape(-1)))
    errors["log_likelihood_abs"] = abs(actual.log_likelihood - float(dense_ll))
    if max(errors.values()) > 2e-10:
        raise AssertionError(f"dense Gaussian parity failed: {errors}")

    # Exercise the information-form branch with more sensors than states and
    # correlated sensor noise, again against the independently dense posterior.
    a_wide = np.array([[0.42, -0.11], [0.17, 0.31]])
    q_wide = np.array([[0.2, 0.03], [0.03, 0.35]])
    h_wide = np.array([[1.0, 0.0], [0.3, 0.8], [-0.6, 0.2], [0.1, -0.7]])
    r_wide = np.array([[0.16, 0.02, 0.0, 0.0], [0.02, 0.21, 0.01, 0.0],
                       [0.0, 0.01, 0.18, -0.015], [0.0, 0.0, -0.015, 0.24]])
    y_wide = np.array([[0.1, -0.2, 0.05, 0.18], [-0.2, 0.1, 0.12, -0.08],
                       [0.16, 0.07, -0.11, 0.03], [0.0, -0.05, 0.19, 0.1]])
    wide = kalman_rts_smoother(y_wide, a_wide, q_wide, h_wide, r_wide)
    wide_mean, wide_cov, wide_obs_cov = dense_posterior(a_wide, q_wide, h_wide, r_wide, y_wide)
    wide_errors = {"smoothed_mean_max_abs": float(np.max(np.abs(wide.smoothed_mean - wide_mean))),
                   "smoothed_covariance_max_abs": 0.0,
                   "adjacent_cross_covariance_max_abs": 0.0}
    n_wide = a_wide.shape[0]
    for t in range(len(y_wide)):
        wide_errors["smoothed_covariance_max_abs"] = max(
            wide_errors["smoothed_covariance_max_abs"],
            float(np.max(np.abs(wide.smoothed_covariance[t] - wide_cov[t*n_wide:(t+1)*n_wide, t*n_wide:(t+1)*n_wide]))),
        )
    for t in range(len(y_wide)-1):
        wide_errors["adjacent_cross_covariance_max_abs"] = max(
            wide_errors["adjacent_cross_covariance_max_abs"],
            float(np.max(np.abs(wide.cross_covariance[t] - wide_cov[(t+1)*n_wide:(t+2)*n_wide, t*n_wide:(t+1)*n_wide]))),
        )
    wide_sign, wide_logdet = np.linalg.slogdet(wide_obs_cov)
    if wide_sign <= 0:
        raise AssertionError("wide dense observation covariance is not positive definite")
    wide_ll = -0.5 * (y_wide.size*np.log(2*np.pi) + wide_logdet
                      + y_wide.reshape(-1) @ np.linalg.solve(wide_obs_cov, y_wide.reshape(-1)))
    wide_errors["log_likelihood_abs"] = abs(wide.log_likelihood - float(wide_ll))
    if max(wide_errors.values()) > 2e-10:
        raise AssertionError(f"information-form dense parity failed: {wide_errors}")

    # Known-truth development check: fully observed low-dimensional stable VAR.
    rng = np.random.default_rng(8)
    true_a = np.array([[0.4, 0.18], [-0.12, 0.3]])
    true_q = np.diag([0.16, 0.12])
    states = np.zeros((700, 2))
    for t in range(1, len(states)):
        states[t] = true_a @ states[t-1] + rng.multivariate_normal(np.zeros(2), true_q)
    observed = states + rng.normal(0.0, 0.01, states.shape)
    fitted = fit_wben_k1(observed, np.eye(2), np.eye(2)*0.0001,
                         penalty=0.001, max_iter=200, tolerance_per_sample=1e-7)
    alternate_sign_fit = fit_wben_k1(
        observed, np.eye(2), np.eye(2)*0.0001,
        penalty=0.001, penalty_sign="plus", max_iter=200,
        tolerance_per_sample=1e-7,
    )
    transition_error = float(np.linalg.norm(fitted.transition - true_a, ord="fro"))
    alternate_error = float(np.linalg.norm(alternate_sign_fit.transition - true_a, ord="fro"))
    if not fitted.converged or not alternate_sign_fit.converged or transition_error > 0.09:
        raise AssertionError("known-truth development fit did not meet predeclared tolerance")
    null_fit = fit_wben_k1(np.zeros((24, 1)), np.zeros((1, 2)), np.eye(1),
                           penalty=0.05, max_iter=20)
    if not null_fit.converged or np.max(np.abs(null_fit.transition)) > 1e-12:
        raise AssertionError("unobservable zero-signal negative control failed")
    rank_deficient_fit = fit_wben_k1(
        np.zeros((24, 1)), np.array([[1.0, 1.0]]), np.eye(1),
        penalty=0.05, max_iter=10,
    )
    if rank_deficient_fit.converged or not np.all(np.isfinite(rank_deficient_fit.transition)):
        raise AssertionError("rank-deficient non-convergence was not reported explicitly")

    run_id = "b3_wben_reference_20261022_v9"
    out_dir = ROOT / "outputs" / "track_b" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "b3_reference_verification.json"
    if out.exists():
        raise FileExistsError(f"refusing to overwrite evidence: {out}")
    report = {
        "status": "PASS",
        "run_id": run_id,
        "scope": "K=1 linear-Gaussian CPU float64 implementation; synthetic development only",
        "paper_claim": False,
        "participant_data_used": False,
        "dense_posterior_parity": errors,
        "more_sensors_than_states_parity": wide_errors,
        "tolerance": 2e-10,
        "known_truth": {
            "seed": 8, "samples": int(len(states)),
            "true_transition": true_a.tolist(),
            "estimated_transition": fitted.transition.tolist(),
            "transition_frobenius_error": transition_error,
            "process_covariance_estimate": fitted.process_covariance.tolist(),
            "converged": fitted.converged,
            "iterations": fitted.iterations,
            "penalty_sign": fitted.penalty_sign,
            "penalty": 0.001,
        },
        "alternate_paper_sign_audit": {
            "penalty_sign": alternate_sign_fit.penalty_sign,
            "estimated_transition": alternate_sign_fit.transition.tolist(),
            "transition_frobenius_error": alternate_error,
            "converged": alternate_sign_fit.converged,
            "iterations": alternate_sign_fit.iterations,
            "interpretation": "Literal plus-sign sensitivity branch; non-concave coordinate-ascent stationary result, not claimed globally optimal or sparsity-promoting.",
        },
        "negative_controls": {
            "zero_signal_unobservable": {
                "converged": null_fit.converged,
                "transition_max_abs": float(np.max(np.abs(null_fit.transition))),
                "expected": "zero transition and finite estimates",
            },
            "rank_deficient_observation": {
                "converged": rank_deficient_fit.converged,
                "iterations": rank_deficient_fit.iterations,
                "finite_estimates": bool(np.all(np.isfinite(rank_deficient_fit.transition))),
                "expected": "non-convergence remains explicit at the fixed 10-iteration budget",
            },
        },
        "source_hashes": {
            "implementation": sha256(ROOT / "src/observable_geometry/track_b/wben.py"),
            "formal_spec": sha256(ROOT / "docs/track_b/B2_FORMAL_SPEC.md"),
            "tests": sha256(ROOT / "tests/test_track_b_wben.py"),
            "verification_script": sha256(Path(__file__)),
        },
        "interpretation": "This verifies the state-space core and one controlled easy case. It is not a replication of the paper's realistic lead-field simulation, a general recovery guarantee, or a result on neural recordings.",
    }
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(out),
                      "dense_errors": errors, "transition_error": transition_error}, indent=2))


if __name__ == "__main__":
    main()
