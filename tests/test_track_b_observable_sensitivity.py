import numpy as np
import pytest

from observable_geometry.track_b.observable_sensitivity import (
    edge_observation_covariance_derivative,
    edge_observation_sensitivity,
    stationary_covariance,
)


def _lag_covariance(a, q, h, lag):
    gamma = stationary_covariance(a, q, rtol=1e-14)
    return h @ np.linalg.matrix_power(a, lag) @ gamma @ h.T


def test_stationary_covariance_matches_independent_kronecker_solution():
    a = np.array([[0.2, 0.15], [0.05, 0.25]])
    q = np.diag([0.8, 0.5])
    expected = np.linalg.solve(
        np.eye(4) - np.kron(a, a), q.reshape(-1, order="F")
    ).reshape((2, 2), order="F")

    actual = stationary_covariance(a, q, rtol=1e-14)

    assert np.allclose(actual, expected, rtol=1e-12, atol=1e-12)
    assert np.allclose(actual, actual.T, atol=1e-12)


def test_edge_covariance_derivative_matches_central_finite_difference():
    a = np.array([[0.2, 0.15], [0.05, 0.25]])
    q = np.diag([0.8, 0.5])
    h = np.array([[1.0, 0.2], [0.1, 0.8]])
    step = 1e-5
    plus, minus = a.copy(), a.copy()
    plus[0, 1] += step
    minus[0, 1] -= step

    analytic = edge_observation_covariance_derivative(a, q, h, 0, 1, 2)
    numeric = (_lag_covariance(plus, q, h, 2)
               - _lag_covariance(minus, q, h, 2)) / (2 * step)

    assert np.allclose(analytic, numeric, rtol=2e-7, atol=1e-9)


def test_zero_observation_operator_cannot_distinguish_any_edge():
    a = np.array([[0.2, 0.15], [0.05, 0.25]])
    q = np.eye(2)
    h = np.zeros((3, 2))
    r = np.eye(3)

    score = edge_observation_sensitivity(a, q, h, r, max_lag=2)

    assert np.array_equal(score, np.zeros((2, 2)))


def test_observed_edge_has_nonzero_score():
    a = np.array([[0.2, 0.15], [0.0, 0.25]])
    q = np.eye(2)
    h = np.eye(2)
    r = np.eye(2) * 0.1

    score = edge_observation_sensitivity(a, q, h, r, max_lag=2)

    assert score[0, 1] > 0
    assert np.all(np.diag(score) == 0)


def test_unconnected_hidden_region_cannot_change_observed_lag_covariance():
    a = np.diag([0.2, 0.25])
    q = np.eye(2)
    h = np.array([[1.0, 0.0]])
    r = np.array([[0.1]])

    score = edge_observation_sensitivity(a, q, h, r, max_lag=3)

    assert np.array_equal(score, np.zeros((2, 2)))


@pytest.mark.parametrize("a,q,h,r,lag", [
    (np.eye(2), np.eye(2), np.eye(2), np.eye(2), 1),
    (np.zeros((2, 3)), np.eye(2), np.eye(2), np.eye(2), 1),
    (np.zeros((2, 2)), np.eye(2), np.eye(2), np.eye(2), 0),
])
def test_invalid_sensitivity_inputs_fail_closed(a, q, h, r, lag):
    with pytest.raises(ValueError):
        edge_observation_covariance_derivative(a, q, h, 0, 1, lag)


def test_sensitivity_requires_positive_definite_observation_noise():
    with pytest.raises(ValueError, match="positive definite"):
        edge_observation_sensitivity(np.zeros((2, 2)), np.eye(2),
                                     np.eye(2), np.diag([1.0, 0.0]))
