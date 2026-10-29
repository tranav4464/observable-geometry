"""Algebraic unit tests for the COG linear-span screen.

These cases are solver/regression tests only.  They are not scientific evidence
and cannot enter calibration or the measured-data novelty decision.
"""
import numpy as np
import pytest

from observable_geometry.track_b.observability_certificate import (
    screen_family_spans,
    whiten_field_and_design,
)


def test_float64_span_residual_screen_never_claims_certified_exclusion():
    y = np.array([1.0, 0.0, 0.0])
    result = screen_family_spans(
        y,
        {
            "point": [np.eye(3)[:, [0]], np.eye(3)[:, [0]]],
            "uniform": [np.ones((3, 1))],
            "ambiguous": [np.eye(3)[:, [0]], np.eye(3)[:, [1]]],
        },
        tolerance=1e-12,
    )
    assert result.summary == "one_or_more_float64_span_residuals_within_tolerance"
    assert result.families[0].status == "within_tolerance_for_at_least_one_tested_variant"
    assert result.families[1].status == "above_tolerance_for_all_tested_variants"
    assert result.families[2].status == "within_tolerance_for_at_least_one_tested_variant"
    assert result.within_tolerance_family_names == ("point", "ambiguous")
    assert result.above_tolerance_family_names == ("uniform",)
    assert all(not item.exclusion_certified for item in result.families)
    assert result.numerical_certification == "uncertified_float64_residuals"
    assert not hasattr(result, "decision")


def test_one_unexcluded_label_does_not_claim_spatial_uniqueness():
    y = np.array([1.0, 0.0])
    result = screen_family_spans(
        y, {"one_label": [np.eye(2)[:, [0]]], "other": [np.eye(2)[:, [1]]]},
        tolerance=1e-12,
    )
    assert result.within_tolerance_family_names == ("one_label",)
    assert result.summary == "one_or_more_float64_span_residuals_within_tolerance"
    assert "unique" not in result.summary


def test_covariance_whitening_preserves_identity_case():
    y = np.array([2.0, 0.0])
    covariance = np.diag([4.0, 1.0])
    wy, wa, rank = whiten_field_and_design(y, np.eye(2), covariance)
    # Eigen-decomposition may permute/sign-flip equivalent axes.  Check the
    # covariance metric, which is invariant to that representation choice.
    assert np.isclose(float(np.linalg.norm(wy)), 1.0)
    np.testing.assert_allclose(wa.T @ wa, np.linalg.inv(covariance), atol=1e-12)
    assert rank == 2


def test_covariance_whitening_handles_reference_rank_deficiency():
    y = np.array([2.0, 0.0])
    design = np.eye(2)
    covariance = np.diag([4.0, 0.0])
    wy, wa, rank = whiten_field_and_design(y, design, covariance)

    assert rank == 1
    np.testing.assert_allclose(wy, np.array([1.0]))
    np.testing.assert_allclose(wa, np.array([[0.5, 0.0]]))


@pytest.mark.parametrize("rtol", [-1e-6, 1.0, np.nan, np.inf])
def test_rejects_invalid_covariance_eigenvalue_cutoff(rtol):
    with pytest.raises(ValueError, match="eigenvalue_rtol"):
        whiten_field_and_design(
            np.ones(2), np.eye(2), np.eye(2), eigenvalue_rtol=rtol
        )


def test_rejects_indefinite_noise_covariance():
    with pytest.raises(ValueError, match="positive semidefinite"):
        whiten_field_and_design(
            np.ones(2), np.eye(2), np.diag([1.0, -0.01])
        )


def test_rejects_asymmetric_noise_covariance():
    with pytest.raises(ValueError, match="not symmetric"):
        whiten_field_and_design(
            np.ones(2), np.eye(2), np.array([[1.0, 0.1], [0.0, 1.0]])
        )


def test_rejects_zero_rank_noise_covariance():
    with pytest.raises(ValueError, match="zero supported rank"):
        whiten_field_and_design(np.ones(2), np.eye(2), np.zeros((2, 2)))


def test_rejects_nonfinite_measured_field():
    with pytest.raises(ValueError, match="finite"):
        screen_family_spans(np.array([np.nan]), {"point": [np.ones((1, 1))]}, tolerance=1.0)


def test_rejects_empty_family():
    with pytest.raises(ValueError, match="at least one"):
        screen_family_spans(np.ones(2), {"point": []}, tolerance=1.0)
