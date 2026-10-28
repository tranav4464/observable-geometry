from __future__ import annotations

from math import erfc, sqrt

import numpy as np
import pytest

from observable_geometry.track_b.task_level_limits import gaussian_source_claim_limit


def test_gaussian_pair_formula_and_repeat_scaling() -> None:
    gain = np.array([[1.0, 0.0]])
    cov = np.array([[1.0]])
    target = np.array([1.0, 0.0])
    alternative = np.array([0.0, 1.0])
    mask = np.array([True, False])
    result = gaussian_source_claim_limit(gain, cov, target, alternative, mask, 1.0)
    repeated = gaussian_source_claim_limit(
        gain, cov, target, alternative, mask, 1.0, independent_observations=4
    )
    assert result.whitened_mean_distance == pytest.approx(1.0)
    assert result.conditional_minimax_error_lower_bound == pytest.approx(0.5*erfc(1/(2*sqrt(2))))
    assert repeated.conditional_minimax_error_lower_bound == pytest.approx(0.5*erfc(1/sqrt(2)))
    assert repeated.conditional_minimax_error_lower_bound < result.conditional_minimax_error_lower_bound


def test_identical_sensor_predictions_limit_error_to_chance() -> None:
    result = gaussian_source_claim_limit(
        np.array([[1.0, 1.0]]), np.array([[1.0]]),
        np.array([1.0, 0.0]), np.array([0.0, 1.0]),
        np.array([True, False]), 1.0,
    )
    assert result.conditional_minimax_error_lower_bound == pytest.approx(0.5)


def test_singular_reference_covariance_supported_difference() -> None:
    result = gaussian_source_claim_limit(
        np.array([[1.0, 0.0], [0.0, 0.0]]), np.diag([1.0, 0.0]),
        np.array([1.0, 0.0]), np.array([0.0, 1.0]),
        np.array([True, False]), 1.0,
    )
    assert result.covariance_rank == 1
    with pytest.raises(ValueError, match="outside covariance support"):
        gaussian_source_claim_limit(
            np.eye(2), np.diag([1.0, 0.0]),
            np.array([1.0, 0.0]), np.array([0.0, 1.0]),
            np.array([True, False]), 1.0,
        )


def test_source_claim_guards() -> None:
    base = (np.eye(2), np.eye(2), np.array([1.0, 0.0]),
            np.array([0.0, 1.0]), np.array([True, False]))
    with pytest.raises(ValueError, match="exceeds"):
        gaussian_source_claim_limit(*base, 0.5)
    with pytest.raises(ValueError, match="inside"):
        gaussian_source_claim_limit(base[0], base[1], base[2],
                                    np.array([0.1, 0.9]), base[4], 1.0)
    with pytest.raises(ValueError, match="positive integer"):
        gaussian_source_claim_limit(*base, 1.0, independent_observations=True)
