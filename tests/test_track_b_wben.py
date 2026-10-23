import numpy as np
import pytest

from observable_geometry.track_b.wben import (
    _m_step,
    _row_lasso,
    _row_literal_plus,
    fit_wben_k1,
    kalman_rts_smoother,
)
from observable_geometry.track_b.synthetic import SyntheticConfig, generate_synthetic


def _dense_condition(a, q, h, r, y, m0=None, p0=None):
    """Independent full joint-Gaussian posterior, built from covariances."""
    t_count, n_obs = y.shape
    n = a.shape[0]
    m0 = np.zeros(n) if m0 is None else m0
    p0 = np.eye(n) if p0 is None else p0
    prior = np.zeros((t_count * n, t_count * n))
    means = np.zeros((t_count, n)); means[0] = m0
    prior[:n, :n] = p0
    for t in range(1, t_count):
        means[t] = a @ means[t - 1]
        prior[t*n:(t+1)*n, t*n:(t+1)*n] = a @ prior[(t-1)*n:t*n, (t-1)*n:t*n] @ a.T + q
        for s in range(t):
            cross = a @ prior[(t-1)*n:t*n, s*n:(s+1)*n]
            prior[t*n:(t+1)*n, s*n:(s+1)*n] = cross
            prior[s*n:(s+1)*n, t*n:(t+1)*n] = cross.T
    obs_map = np.kron(np.eye(t_count), h)
    obs_cov = np.kron(np.eye(t_count), r)
    predicted = obs_map @ means.reshape(-1)
    residual = y.reshape(-1) - predicted
    obs_prior = obs_map @ prior @ obs_map.T + obs_cov
    gain = np.linalg.solve(obs_prior, obs_map @ prior).T
    post_mean = means.reshape(-1) + gain @ residual
    post_cov = prior - gain @ obs_map @ prior
    return post_mean.reshape(t_count, n), post_cov


def test_rts_matches_independent_dense_joint_posterior_including_cross_covariance():
    a = np.array([[0.55, 0.12], [-0.08, 0.35]])
    q = np.diag([0.25, 0.4])
    h = np.array([[1.0, 0.35], [-0.2, 0.8]])
    r = np.diag([0.12, 0.2])
    y = np.array([[0.2, -0.1], [0.4, 0.15], [-0.25, 0.3], [0.1, 0.5]])
    m0 = np.array([0.15, -0.12])
    p0 = np.array([[0.8, 0.1], [0.1, 0.6]])
    actual = kalman_rts_smoother(y, a, q, h, r, initial_mean=m0,
                                 initial_covariance=p0)
    expected_mean, expected_cov = _dense_condition(a, q, h, r, y, m0, p0)
    np.testing.assert_allclose(actual.smoothed_mean, expected_mean, atol=1e-11, rtol=1e-10)
    n = a.shape[0]
    for t in range(len(y)):
        block = expected_cov[t*n:(t+1)*n, t*n:(t+1)*n]
        np.testing.assert_allclose(actual.smoothed_covariance[t], block, atol=1e-11, rtol=1e-10)
    for t in range(len(y) - 1):
        block = expected_cov[(t+1)*n:(t+2)*n, t*n:(t+1)*n]
        np.testing.assert_allclose(actual.cross_covariance[t], block, atol=1e-11, rtol=1e-10)


def test_filter_log_likelihood_matches_dense_observation_marginal():
    a = np.array([[0.45, 0.05], [0.0, 0.2]])
    q = np.diag([0.3, 0.5]); h = np.array([[1.0, 0.2]])
    r = np.array([[0.15]])
    y = np.array([[0.1], [0.2], [-0.1]])
    result = kalman_rts_smoother(y, a, q, h, r)
    mean, cov = _dense_condition(a, q, h, r, y)
    # Recover the marginal likelihood directly from the dense prior observation law.
    n, t_count = a.shape[0], y.shape[0]
    prior = np.zeros((t_count*n, t_count*n)); prior[:n, :n] = np.eye(n)
    for t in range(1, t_count):
        prior[t*n:(t+1)*n, t*n:(t+1)*n] = a @ prior[(t-1)*n:t*n, (t-1)*n:t*n] @ a.T + q
        for s in range(t):
            cross = a @ prior[(t-1)*n:t*n, s*n:(s+1)*n]
            prior[t*n:(t+1)*n, s*n:(s+1)*n] = cross
            prior[s*n:(s+1)*n, t*n:(t+1)*n] = cross.T
    g = np.kron(np.eye(t_count), h)
    obs_cov = g @ prior @ g.T + np.kron(np.eye(t_count), r)
    sign, logdet = np.linalg.slogdet(obs_cov)
    assert sign > 0
    expected_ll = -0.5 * (t_count*np.log(2*np.pi) + logdet + y.reshape(-1) @ np.linalg.solve(obs_cov, y.reshape(-1)))
    assert result.log_likelihood == pytest.approx(expected_ll, abs=1e-11)
    np.testing.assert_allclose(result.smoothed_mean, mean, atol=1e-11)


def test_state_space_information_update_matches_dense_when_sensors_exceed_states():
    a = np.array([[0.42, -0.11], [0.17, 0.31]])
    q = np.array([[0.2, 0.03], [0.03, 0.35]])
    h = np.array([[1.0, 0.0], [0.3, 0.8], [-0.6, 0.2], [0.1, -0.7]])
    r = np.array([[0.16, 0.02, 0.0, 0.0], [0.02, 0.21, 0.01, 0.0],
                  [0.0, 0.01, 0.18, -0.015], [0.0, 0.0, -0.015, 0.24]])
    y = np.array([[0.1, -0.2, 0.05, 0.18], [-0.2, 0.1, 0.12, -0.08],
                  [0.16, 0.07, -0.11, 0.03], [0.0, -0.05, 0.19, 0.1]])
    actual = kalman_rts_smoother(y, a, q, h, r)
    expected_mean, expected_cov = _dense_condition(a, q, h, r, y)
    np.testing.assert_allclose(actual.smoothed_mean, expected_mean, atol=2e-11, rtol=1e-10)
    n = a.shape[0]
    for t in range(len(y)):
        np.testing.assert_allclose(actual.smoothed_covariance[t],
                                   expected_cov[t*n:(t+1)*n, t*n:(t+1)*n],
                                   atol=2e-11, rtol=1e-10)
    for t in range(len(y)-1):
        np.testing.assert_allclose(actual.cross_covariance[t],
                                   expected_cov[(t+1)*n:(t+2)*n, t*n:(t+1)*n],
                                   atol=2e-11, rtol=1e-10)


def test_primary_l1_row_solver_matches_soft_threshold_for_diagonal_design():
    solution = _row_lasso(np.diag([2.0, 4.0]), np.array([1.0, -1.0]), 0.25)
    np.testing.assert_allclose(solution, [0.375, -0.1875], atol=1e-10)


def test_primary_l1_row_solver_satisfies_kkt_conditions_on_correlated_design():
    rng = np.random.default_rng(12)
    design = rng.normal(size=(6, 6))
    gram = design.T @ design + 0.5*np.eye(6)
    b = rng.normal(size=6)
    penalty = 0.17
    solution = _row_lasso(gram, b, penalty)
    gradient = gram @ solution - b
    active = np.abs(solution) > 1e-8
    np.testing.assert_allclose(gradient[active] + penalty*np.sign(solution[active]),
                               0.0, atol=2e-8)
    assert np.all(np.abs(gradient[~active]) <= penalty + 2e-8)


def test_literal_plus_sign_is_preserved_as_non_sparsifying_branch():
    solution = _row_literal_plus(np.array([[1.0]]), np.array([0.0]), 0.2)
    assert solution[0] == pytest.approx(0.2)
    # Its stated objective rewards magnitude, unlike the primary penalty.
    assert abs(solution[0]) > 0


def test_m_step_recovers_unpenalized_transition_from_exact_latent_states():
    from observable_geometry.track_b.wben import SmootherResult

    rng = np.random.default_rng(42)
    a_true = np.array([[0.45, -0.15], [0.2, 0.3]])
    states = np.zeros((5000, 2))
    states[0] = rng.normal(size=2)
    for t in range(1, len(states)):
        states[t] = a_true @ states[t-1] + rng.normal(scale=0.08, size=2)
    cov = np.zeros((len(states), 2, 2))
    # With zero posterior covariance, cross moments reduce to observed outer products.
    cross = np.zeros((len(states)-1, 2, 2))
    # Construct exact cross-covariance field as zero; m-step adds mean outer products.
    fake = SmootherResult(states, cov, states, cov, states, cov, cross, 0.0)
    estimate, q = _m_step(fake, 0.0, "minus", 1e-8)
    np.testing.assert_allclose(estimate, a_true, atol=0.02)
    assert np.all(np.diag(q) > 0)
    assert np.allclose(q, np.diag(np.diag(q)))


@pytest.mark.parametrize("bad", [
    {"a": np.array([[1.1]]), "q": np.array([[1.0]]), "h": np.array([[1.0]]),
     "r": np.array([[0.1]]), "y": np.ones((3, 1))},
])
def test_smoother_accepts_unstable_dynamic_prior_as_finite_horizon_model(bad):
    # Stability is required for stationary sensitivity, but a finite-horizon
    # Kalman model is mathematically defined and must not reject rho(A)>1.
    out = kalman_rts_smoother(bad["y"], bad["a"], bad["q"], bad["h"], bad["r"])
    assert np.all(np.isfinite(out.smoothed_mean))


@pytest.mark.parametrize("kwargs", [
    {"penalty": -1.0}, {"penalty_sign": "typo"}, {"max_iter": 0},
])
def test_fit_rejects_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        fit_wben_k1(np.ones((5, 1)), np.ones((1, 1)), np.ones((1, 1)), **kwargs)


def test_fit_returns_finite_explicit_penalty_metadata():
    rng = np.random.default_rng(9)
    x = np.zeros(120)
    for t in range(1, len(x)):
        x[t] = 0.65*x[t-1] + rng.normal(scale=0.25)
    y = x[:, None] + rng.normal(scale=0.05, size=(len(x), 1))
    result = fit_wben_k1(y, np.ones((1, 1)), np.array([[0.0025]]),
                         penalty=0.0, max_iter=100)
    assert np.all(np.isfinite(result.transition))
    assert np.all(np.diag(result.process_covariance) >= result.variance_floor)
    assert result.penalty_sign == "minus"
    assert result.initialization == "zero"
    assert result.iterations <= 100
    assert np.isfinite(result.log_likelihood[-1])


def test_pseudoinverse_initialization_is_named_and_finite():
    rng = np.random.default_rng(18)
    a_true = np.array([[0.5, 0.1], [-0.05, 0.35]])
    x = np.zeros((180, 2))
    for t in range(1, len(x)):
        x[t] = a_true @ x[t-1] + rng.normal(scale=0.2, size=2)
    h = np.array([[1.0, 0.0], [0.4, 0.8], [-0.2, 0.5]])
    y = x @ h.T + rng.normal(scale=0.02, size=(len(x), h.shape[0]))
    result = fit_wben_k1(y, h, np.eye(3)*0.0004, penalty=0.005,
                         initialization="pseudoinverse", max_iter=100)
    assert result.initialization == "pseudoinverse"
    assert np.all(np.isfinite(result.transition))
    assert np.all(np.isfinite(result.process_covariance))


def test_zero_signal_with_unobservable_operator_is_finite_and_recovers_null_dynamics():
    result = fit_wben_k1(np.zeros((24, 1)), np.zeros((1, 2)), np.eye(1),
                         penalty=0.05, max_iter=20)
    np.testing.assert_allclose(result.transition, np.zeros((2, 2)), atol=1e-12)
    assert np.all(np.isfinite(result.process_covariance))
    assert result.converged


def test_rank_deficient_observation_keeps_nonconvergence_explicit():
    h = np.array([[1.0, 1.0]])
    result = fit_wben_k1(np.zeros((24, 1)), h, np.eye(1),
                         penalty=0.05, max_iter=10)
    assert np.all(np.isfinite(result.transition))
    assert np.all(np.isfinite(result.process_covariance))
    assert not result.converged
    assert result.iterations == 10


def test_multimodal_synthetic_generator_connects_to_state_space_fit():
    data = generate_synthetic(SyntheticConfig(
        n_regions=5, n_scalp=8, n_active_regions=4, max_indegree=1,
        n_ieeg_regions=3, n_samples=80, target_radius=0.55,
        scalp_snr_db=15.0, ieeg_snr_db=20.0, seed=21,
    ))
    h = np.vstack([data.scalp_operator, data.ieeg_operator])
    observations = np.column_stack([data.scalp, data.ieeg])
    noise_variances = np.r_[np.var(data.scalp_noise, axis=0),
                            np.var(data.ieeg_noise, axis=0)]
    result = fit_wben_k1(observations, h, np.diag(noise_variances),
                         penalty=0.005, initialization="pseudoinverse",
                         max_iter=2)
    # This checks end-to-end operator/shape compatibility only. Recovery and
    # convergence are assessed in separately prespecified benchmark gates.
    assert result.iterations <= 2
    assert np.all(np.isfinite(result.transition))
    assert np.all(np.isfinite(result.process_covariance))
    assert observations.shape == (80, 11)
