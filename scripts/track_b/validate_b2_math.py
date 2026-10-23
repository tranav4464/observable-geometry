"""Independent small-matrix checks for the B2 covariance-sensitivity equations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from observable_geometry.track_b.observable_sensitivity import (
    edge_observation_covariance_derivative,
    stationary_covariance,
)


def independent_gamma(a: np.ndarray, q: np.ndarray) -> np.ndarray:
    n = len(a)
    vector = np.linalg.solve(np.eye(n * n) - np.kron(a, a), q.reshape(-1, order="F"))
    return vector.reshape((n, n), order="F")


def independent_lag_covariance(a: np.ndarray, q: np.ndarray,
                               h: np.ndarray, lag: int) -> np.ndarray:
    return h @ np.linalg.matrix_power(a, lag) @ independent_gamma(a, q) @ h.T


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    a = np.array([[0.2, 0.15], [0.05, 0.25]], dtype=float)
    q = np.diag([0.8, 0.5])
    h = np.array([[1.0, 0.2], [0.1, 0.8]])
    gamma_ref = independent_gamma(a, q)
    gamma_impl = stationary_covariance(a, q, rtol=1e-14)

    step = 1e-5
    plus, minus = a.copy(), a.copy()
    plus[0, 1] += step
    minus[0, 1] -= step
    fd = (independent_lag_covariance(plus, q, h, 2)
          - independent_lag_covariance(minus, q, h, 2)) / (2 * step)
    analytic = edge_observation_covariance_derivative(a, q, h, 0, 1, 2)
    gamma_error = float(np.max(np.abs(gamma_impl - gamma_ref)))
    derivative_error = float(np.max(np.abs(analytic - fd)))

    checks = {
        "stationary_covariance_matches_independent_kronecker_solution": gamma_error < 1e-11,
        "edge_derivative_matches_independent_central_difference": derivative_error < 1e-8,
        "zero_observation_boundary_is_zero": bool(np.allclose(
            edge_observation_covariance_derivative(a, q, np.zeros((2, 2)), 0, 1, 2), 0.0
        )),
        "transition_is_strictly_stable": bool(np.max(np.abs(np.linalg.eigvals(a))) < 1.0),
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "max_abs_stationary_covariance_error": gamma_error,
        "max_abs_derivative_error": derivative_error,
        "finite_difference_step": step,
        "test_matrix": a.tolist(),
        "process_covariance": q.tolist(),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = args.report.resolve()
        if path.exists():
            raise SystemExit(f"Refusing to overwrite existing report: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
