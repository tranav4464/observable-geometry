import pytest

from observable_geometry.track_b.forward_error_budget import (
    certified_opposite_decision_radius,
    perturbed_certificate_envelopes,
)


def test_preserves_opposite_decisions_below_open_radius():
    radius = certified_opposite_decision_radius(0.8, 1.2, 1.0, 1.0, 2.0)
    assert radius.epsilon_supremum == pytest.approx(0.2 / 3.0)
    feasible, excluded = perturbed_certificate_envelopes(0.8, 1.2, 0.06, 1.0, 2.0)
    assert feasible <= 1.0 < excluded


def test_includes_target_forward_error():
    with_target = certified_opposite_decision_radius(0.8, 1.2, 1.0, 1.0, 2.0)
    fixed_target = certified_opposite_decision_radius(0.8, 1.2, 1.0, 0.0, 2.0)
    assert with_target.epsilon_supremum < fixed_target.epsilon_supremum


def test_rejects_unproven_or_malformed_decisions():
    with pytest.raises(ValueError):
        certified_opposite_decision_radius(1.1, 1.2, 1.0, 1.0, 2.0)
    with pytest.raises(ValueError):
        certified_opposite_decision_radius(0.8, 1.0, 1.0, 1.0, 2.0)
    with pytest.raises(ValueError):
        certified_opposite_decision_radius(0.8, 1.2, float("nan"), 1.0, 2.0)
    with pytest.raises(ValueError):
        perturbed_certificate_envelopes(0.8, 1.2, -0.1, 1.0, 2.0)
