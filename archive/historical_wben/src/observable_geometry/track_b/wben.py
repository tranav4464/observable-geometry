"""Independent CPU/float64 implementation of the K=1 WBEN state-space core.

This implements linear-Gaussian filtering/smoothing and the first-order EM
updates from the published formulation. Paper sign ambiguity is explicit:
``minus`` is the sparsity-promoting Eq. (4) reading; ``plus`` is an exact
coordinate-ascent M-step for the literal plus-sign reading in Eq. (12).
It is a reference implementation, not an author's-code reproduction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

PenaltySign = Literal["minus", "plus"]
Initialization = Literal["zero", "pseudoinverse"]


def _symmetric(a: np.ndarray) -> np.ndarray:
    return (a + a.T) * 0.5


def _validate_model(a: np.ndarray, q: np.ndarray, h: np.ndarray,
                    r: np.ndarray, observations: np.ndarray) -> tuple[int, int, int]:
    if any(np.asarray(x).dtype.kind not in "fiu" for x in (a, q, h, r, observations)):
        raise ValueError("all model inputs must be numeric arrays")
    n = a.shape[0] if np.asarray(a).ndim == 2 else -1
    if a.shape != (n, n) or n < 1:
        raise ValueError("A must be a non-empty square matrix")
    if q.shape != (n, n):
        raise ValueError("Q must have shape (n_state, n_state)")
    if h.ndim != 2 or h.shape[1] != n:
        raise ValueError("H must have shape (n_observation, n_state)")
    m = h.shape[0]
    if r.shape != (m, m):
        raise ValueError("R must have shape (n_observation, n_observation)")
    if observations.ndim != 2 or observations.shape[1] != m or observations.shape[0] < 1:
        raise ValueError("observations must have shape (n_time, n_observation)")
    arrays = [np.asarray(x, dtype=np.float64) for x in (a, q, h, r, observations)]
    if not all(np.all(np.isfinite(x)) for x in arrays):
        raise ValueError("model inputs must be finite")
    _, q, _, r, _ = arrays
    if not np.allclose(q, q.T, atol=1e-10) or not np.allclose(r, r.T, atol=1e-10):
        raise ValueError("Q and R must be symmetric")
    if np.linalg.eigvalsh(_symmetric(q))[0] <= 0:
        raise ValueError("Q must be positive definite")
    if np.linalg.eigvalsh(_symmetric(r))[0] <= 0:
        raise ValueError("R must be positive definite")
    return n, m, observations.shape[0]


@dataclass(frozen=True)
class SmootherResult:
    filtered_mean: np.ndarray
    filtered_covariance: np.ndarray
    predicted_mean: np.ndarray
    predicted_covariance: np.ndarray
    smoothed_mean: np.ndarray
    smoothed_covariance: np.ndarray
    # cross_covariance[t] = Cov(x[t+1], x[t] | all observations)
    cross_covariance: np.ndarray
    log_likelihood: float


def kalman_rts_smoother(
    observations: np.ndarray, a: np.ndarray, q: np.ndarray, h: np.ndarray,
    r: np.ndarray, *, initial_mean: np.ndarray | None = None,
    initial_covariance: np.ndarray | None = None,
) -> SmootherResult:
    """Run a dense-covariance Kalman filter and RTS smoother for K=1."""
    y = np.asarray(observations, dtype=np.float64)
    a = np.asarray(a, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    r = np.asarray(r, dtype=np.float64)
    n, m, t_count = _validate_model(a, q, h, r, y)
    m0 = np.zeros(n) if initial_mean is None else np.asarray(initial_mean, dtype=np.float64)
    p0 = np.eye(n) if initial_covariance is None else np.asarray(initial_covariance, dtype=np.float64)
    if m0.shape != (n,) or p0.shape != (n, n) or not np.all(np.isfinite(m0)):
        raise ValueError("invalid initial state moments")
    if not np.allclose(p0, p0.T, atol=1e-10) or np.linalg.eigvalsh(_symmetric(p0))[0] <= 0:
        raise ValueError("initial covariance must be symmetric positive definite")

    fm = np.empty((t_count, n)); fp = np.empty((t_count, n, n))
    pm = np.empty_like(fm); pp = np.empty_like(fp)
    loglike = 0.0
    eye = np.eye(m)
    state_eye = np.eye(n)
    # When there are more sensors than latent states, update in state space
    # via the information form/Woodbury identity. This is algebraically the
    # same Gaussian conditioning as the sensor-space update, but avoids a
    # fresh M x M factorization at every sample.
    use_state_space_update = m > n
    if use_state_space_update:
        r_chol = np.linalg.cholesky(r)
        r_inverse = np.linalg.solve(r, eye)
        observation_information = _symmetric(h.T @ r_inverse @ h)
        logdet_r = float(2.0 * np.log(np.diag(r_chol)).sum())
    for t in range(t_count):
        if t == 0:
            pm[t], pp[t] = m0, p0
        else:
            pm[t] = a @ fm[t - 1]
            pp[t] = _symmetric(a @ fp[t - 1] @ a.T + q)
        innovation = y[t] - h @ pm[t]
        try:
            if use_state_space_update:
                prior_chol = np.linalg.cholesky(pp[t])
                prior_precision = np.linalg.solve(pp[t], state_eye)
                posterior_precision = _symmetric(prior_precision + observation_information)
                precision_chol = np.linalg.cholesky(posterior_precision)
                fp[t] = _symmetric(np.linalg.solve(posterior_precision, state_eye))
                weighted_innovation = r_inverse @ innovation
                information_vector = h.T @ weighted_innovation
                fm[t] = pm[t] + fp[t] @ information_vector
                quad = float(innovation @ weighted_innovation
                             - information_vector @ fp[t] @ information_vector)
                logdet = (logdet_r
                          + 2.0 * np.log(np.diag(prior_chol)).sum()
                          + 2.0 * np.log(np.diag(precision_chol)).sum())
            else:
                innovation_cov = _symmetric(h @ pp[t] @ h.T + r)
                chol = np.linalg.cholesky(innovation_cov)
                gain = np.linalg.solve(innovation_cov, h @ pp[t]).T
                fm[t] = pm[t] + gain @ innovation
                # Joseph form keeps positive semidefiniteness under roundoff.
                residual_map = state_eye - gain @ h
                fp[t] = _symmetric(residual_map @ pp[t] @ residual_map.T + gain @ r @ gain.T)
                whitened = np.linalg.solve(chol, innovation)
                quad = float(whitened @ whitened)
                logdet = float(2.0 * np.log(np.diag(chol)).sum())
        except np.linalg.LinAlgError as exc:
            raise FloatingPointError(f"innovation covariance failed at time {t}") from exc
        loglike += -0.5 * (m * np.log(2.0 * np.pi) + logdet + quad)

    sm = fm.copy(); sp = fp.copy(); gains = np.empty((max(t_count - 1, 0), n, n))
    for t in range(t_count - 2, -1, -1):
        try:
            gains[t] = np.linalg.solve(pp[t + 1], a @ fp[t]).T
        except np.linalg.LinAlgError as exc:
            raise FloatingPointError(f"predicted covariance failed at time {t + 1}") from exc
        sm[t] = fm[t] + gains[t] @ (sm[t + 1] - pm[t + 1])
        sp[t] = _symmetric(fp[t] + gains[t] @ (sp[t + 1] - pp[t + 1]) @ gains[t].T)
    cross = np.empty((max(t_count - 1, 0), n, n))
    for t in range(t_count - 1):
        cross[t] = sp[t + 1] @ gains[t].T
    return SmootherResult(fm, fp, pm, pp, sm, sp, cross, float(loglike))


def _row_lasso(u: np.ndarray, b: np.ndarray, lam: float, *, tol: float = 1e-9,
               max_iter: int = 20_000) -> np.ndarray:
    """Cyclic coordinate solve of .5*x'Ux - b'x + lam*||x||_1.

    Each update is the exact one-dimensional minimizer. This avoids repeated
    eigensolves and slow fixed-step convergence on nearly unobservable latent
    directions. The convex row problem has a unique solution when ``u`` is
    positive definite; callers add a tiny diagonal floor explicitly.
    """
    u = _symmetric(u)
    diag = np.diag(u)
    if np.any(diag <= 0) or not np.all(np.isfinite(diag)):
        raise FloatingPointError("transition normal matrix must have positive diagonal")
    x = np.zeros_like(b)
    for _ in range(max_iter):
        largest = 0.0
        for j in range(len(x)):
            partial = b[j] - u[j] @ x + diag[j] * x[j]
            updated = np.sign(partial) * max(abs(partial) - lam, 0.0) / diag[j]
            largest = max(largest, abs(updated - x[j]))
            x[j] = updated
        if largest <= tol * (1.0 + np.linalg.norm(x)):
            return x
    raise RuntimeError("L1 coordinate descent did not converge")


def _row_literal_plus(u: np.ndarray, b: np.ndarray, lam: float, *, tol: float = 1e-10,
                      max_iter: int = 100_000) -> np.ndarray:
    """Coordinate-maximize -.5*x'Ux + b'x + lam*||x||_1.

    This objective is non-concave. Each coordinate update selects its exact
    one-dimensional global maximum; the result is a stationary point, not a
    guaranteed global maximum. Its purpose is to expose the paper's alternate
    printed sign, never to silently treat that sign as sparsity.
    """
    diag = np.diag(u)
    if np.any(diag <= 0):
        raise FloatingPointError("transition normal matrix must have positive diagonal")
    x = np.zeros_like(b)
    for _ in range(max_iter):
        largest = 0.0
        for j in range(len(x)):
            partial = b[j] - u[j] @ x + diag[j] * x[j]
            candidates = np.array([0.0, (partial + lam) / diag[j], (partial - lam) / diag[j]])
            values = -0.5 * diag[j] * candidates**2 + partial * candidates + lam * np.abs(candidates)
            updated = candidates[int(np.argmax(values))]
            largest = max(largest, abs(updated - x[j]))
            x[j] = updated
        if largest <= tol * (1.0 + np.linalg.norm(x)):
            return x
    raise RuntimeError("literal plus-sign coordinate ascent did not converge")


@dataclass(frozen=True)
class EMResult:
    transition: np.ndarray
    process_covariance: np.ndarray
    log_likelihood: tuple[float, ...]
    penalized_objective: tuple[float, ...]
    converged: bool
    iterations: int
    penalty_sign: PenaltySign
    initialization: Initialization
    variance_floor: float


def _m_step(sm: SmootherResult, lam: float, penalty_sign: PenaltySign,
            variance_floor: float) -> tuple[np.ndarray, np.ndarray]:
    means = sm.smoothed_mean
    covs = sm.smoothed_covariance
    n, t_count = means.shape[1], means.shape[0]
    suu = np.zeros((n, n)); sxu = np.zeros((n, n)); sxx = np.zeros((n, n))
    for t in range(t_count - 1):
        suu += covs[t] + np.outer(means[t], means[t])
        sxu += sm.cross_covariance[t] + np.outer(means[t + 1], means[t])
        sxx += covs[t + 1] + np.outer(means[t + 1], means[t + 1])
    suu = _symmetric(suu)
    information_scale = max(float(np.trace(suu)) / n, np.finfo(np.float64).tiny)
    suu.flat[:: n + 1] += 1e-12 * information_scale
    a = np.empty((n, n))
    for i in range(n):
        if penalty_sign == "minus":
            a[i] = _row_lasso(suu, sxu[i], lam)
        else:
            a[i] = _row_literal_plus(suu, sxu[i], lam)
    residual = sxx - a @ sxu.T - sxu @ a.T + a @ suu @ a.T
    q_diag = np.maximum(np.diag(_symmetric(residual)) / max(t_count - 1, 1), variance_floor)
    return a, np.diag(q_diag)


def fit_wben_k1(
    observations: np.ndarray, h: np.ndarray, r: np.ndarray, *,
    penalty: float = 0.05, penalty_sign: PenaltySign = "minus",
    initialization: Initialization = "zero",
    initial_process_covariance: np.ndarray | None = None,
    initial_state_covariance: np.ndarray | None = None,
    max_iter: int = 200, tolerance_per_sample: float = 1e-6,
    variance_floor: float = 1e-8,
) -> EMResult:
    """Fit a K=1 WBEN-style model with EM and fixed observation noise.

    Choices not specified by the article are explicit: `zero` uses A0=0 and
    Q0=I; `pseudoinverse` estimates an initial VAR from H^+ observations and
    its residual diagonal. Both use initial latent state N(0,I). Objective
    histories include the selected penalty sign. `plus` follows the literal
    alternative sign and is a non-concave coordinate-ascent sensitivity branch.
    """
    y = np.asarray(observations, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64); r = np.asarray(r, dtype=np.float64)
    if penalty_sign not in ("minus", "plus"):
        raise ValueError("penalty_sign must be 'minus' or 'plus'")
    if initialization not in ("zero", "pseudoinverse"):
        raise ValueError("initialization must be 'zero' or 'pseudoinverse'")
    if not np.isfinite(penalty) or penalty < 0:
        raise ValueError("penalty must be finite and non-negative")
    if not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")
    if not np.isfinite(tolerance_per_sample) or tolerance_per_sample <= 0:
        raise ValueError("tolerance_per_sample must be positive and finite")
    if not np.isfinite(variance_floor) or variance_floor <= 0:
        raise ValueError("variance_floor must be positive and finite")
    if y.ndim != 2 or h.ndim != 2:
        raise ValueError("observations and H must be matrices")
    n = h.shape[1]
    a = np.zeros((n, n))
    q = np.eye(n) if initial_process_covariance is None else np.asarray(initial_process_covariance, dtype=np.float64)
    p0 = np.eye(n) if initial_state_covariance is None else np.asarray(initial_state_covariance, dtype=np.float64)
    if q.shape != (n, n) or p0.shape != (n, n):
        raise ValueError("initial covariance matrices must match latent-state dimensions")
    if (not np.all(np.isfinite(q)) or not np.all(np.isfinite(p0))
            or not np.allclose(q, q.T, atol=1e-10 * max(np.linalg.norm(q), 1.0))
            or not np.allclose(p0, p0.T, atol=1e-10 * max(np.linalg.norm(p0), 1.0))
            or np.linalg.eigvalsh(_symmetric(q))[0] <= 0
            or np.linalg.eigvalsh(_symmetric(p0))[0] <= 0):
        raise ValueError("initial state/process covariance must be finite symmetric positive definite")
    if initialization == "pseudoinverse":
        latent_proxy = y @ np.linalg.pinv(h).T
        x_prev, x_next = latent_proxy[:-1], latent_proxy[1:]
        gram = x_prev.T @ x_prev
        a = x_next.T @ x_prev @ np.linalg.pinv(gram)
        residual = x_next - x_prev @ a.T
        q = np.diag(np.maximum(np.mean(np.square(residual), axis=0), variance_floor))
    ll_hist: list[float] = []; obj_hist: list[float] = []
    converged = False
    m_steps = 0
    for _ in range(max_iter):
        sm = kalman_rts_smoother(y, a, q, h, r, initial_covariance=p0)
        ll_hist.append(sm.log_likelihood)
        penalty_term = penalty * np.abs(a).sum()
        current_objective = (sm.log_likelihood - penalty_term if penalty_sign == "minus"
                             else sm.log_likelihood + penalty_term)
        obj_hist.append(current_objective)
        if len(obj_hist) >= 2 and abs(obj_hist[-1] - obj_hist[-2]) / y.shape[0] <= tolerance_per_sample:
            converged = True
            break
        new_a, new_q = _m_step(sm, penalty, penalty_sign, variance_floor)
        if not np.all(np.isfinite(new_a)) or not np.all(np.isfinite(new_q)):
            raise FloatingPointError("EM update produced non-finite parameters")
        a, q = new_a, new_q
        m_steps += 1
    final = kalman_rts_smoother(y, a, q, h, r, initial_covariance=p0)
    ll_hist.append(final.log_likelihood)
    penalty_term = penalty * np.abs(a).sum()
    final_objective = (final.log_likelihood - penalty_term if penalty_sign == "minus"
                       else final.log_likelihood + penalty_term)
    if not obj_hist or final_objective != obj_hist[-1]:
        obj_hist.append(final_objective)
    if (not converged and len(obj_hist) >= 2
            and abs(obj_hist[-1] - obj_hist[-2]) / y.shape[0] <= tolerance_per_sample):
        converged = True
    return EMResult(a, q, tuple(ll_hist), tuple(obj_hist), converged,
                    m_steps, penalty_sign, initialization, variance_floor)
