"""Algebraic unit tests for the COG certificate.

These cases are solver/regression tests only.  They are not scientific evidence
and cannot enter calibration or the measured-data novelty decision.
"""
import numpy as np
import pytest

from observable_geometry.track_b.observability_certificate import (
    certify_observability,
    whiten_field_and_design,
)


def test_conservative_family_statuses_and_decision():
    y = np.array([1.0, 0.0, 0.0])
    result = certify_observability(
        y,
        {
            "point": [np.eye(3)[:, [0]], np.eye(3)[:, [0]]],
            "uniform": [np.ones((3, 1))],
            "ambiguous": [np.eye(3)[:, [0]], np.eye(3)[:, [1]]],
        },
        tolerance=1e-12,
    )
    assert result.decision == "ambiguous"
    assert result.families[0].status == "fit"
    assert result.families[1].status == "excluded"
    assert result.families[2].status == "sensitive"


def test_covariance_whitening_preserves_identity_case():
    y = np.array([2.0, 0.0])
    covariance = np.diag([4.0, 1.0])
    wy, wa, rank = whiten_field_and_design(y, np.eye(2), covariance)
    # Eigen-decomposition may permute/sign-flip equivalent axes.  Check the
    # covariance metric, which is invariant to that representation choice.
    assert np.isclose(float(np.linalg.norm(wy)), 1.0)
    np.testing.assert_allclose(wa.T @ wa, np.linalg.inv(covariance), atol=1e-12)
    assert rank == 2


def test_rejects_nonfinite_measured_field():
    with pytest.raises(ValueError, match="finite"):
        certify_observability(np.array([np.nan]), {"point": [np.ones((1, 1))]}, tolerance=1.0)


def test_rejects_empty_family():
    with pytest.raises(ValueError, match="at least one"):
        certify_observability(np.ones(2), {"point": []}, tolerance=1.0)
