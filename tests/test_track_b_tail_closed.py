import numpy as np
import pytest

from observable_geometry.track_b.tail_closed import (
    construct_finite_prior_sensor_witness, exact_mimicry_audit,
    finite_prior_gram_envelope, finite_prior_sensor_witness, model_mimicry_subspace,
    tail_closed_margin_frontier,
)


def test_tail_closed_frontier_is_invariant_to_sensor_rotation():
    b = np.array([[1.0, 0.0], [0.2, 0.7], [0.0, 0.3]])
    d = np.array([[0.3, 0.0], [0.0, 1.0], [0.2, 0.4]])
    c = d @ d.T
    q, _ = np.linalg.qr(np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 1.0], [1.0, 0.0, 1.0]]))
    first = tail_closed_margin_frontier(b, c, grid_size=31)
    rotated = tail_closed_margin_frontier(q @ b, q @ c @ q.T, grid_size=31)
    assert np.allclose(first.normalized_lower_margin, rotated.normalized_lower_margin, rtol=1e-10, atol=1e-12)


def test_error_inflation_cannot_increase_a_frontier_lower_bound():
    b = np.array([[1.0, 0.0], [0.2, 0.7], [0.0, 0.3]])
    d = np.array([[0.3, 0.0], [0.0, 1.0], [0.2, 0.4]])
    c = d @ d.T
    nominal = tail_closed_margin_frontier(b, c, grid_size=31)
    robust = tail_closed_margin_frontier(b, c, gram_error_bound=0.2, grid_size=31)
    assert np.all(robust.normalized_lower_margin <= nominal.normalized_lower_margin + 1e-12)


def test_selected_basis_is_orthonormal_for_positive_margin():
    b = np.array([[2.0, 0.0], [0.0, 1.0]])
    c = np.array([[0.01, 0.0], [0.0, 0.04]])
    result = tail_closed_margin_frontier(b, c, eta=1.0, grid_size=31)
    assert result.normalized_lower_margin[0] > 0
    basis = result.selected_basis_by_rank[0]
    assert basis is not None
    assert basis.shape == (2, 1)
    assert np.allclose(basis.T @ basis, np.eye(1), atol=1e-12)


def test_tail_closed_frontier_rejects_indefinite_gram():
    with pytest.raises(ValueError, match="positive semidefinite"):
        tail_closed_margin_frontier(np.eye(2), np.array([[1.0, 2.0], [2.0, 1.0]]))


def test_tail_closed_frontier_requires_positive_budget():
    with pytest.raises(ValueError, match="eta"):
        tail_closed_margin_frontier(np.eye(2), np.eye(2), eta=0.0)


def test_prior_envelope_dominates_nested_and_incomparable_grams():
    for family in (
        (np.diag([1.0, 1.0]), np.diag([2.0, 2.0])),
        (np.diag([2.0, 1.0]), np.diag([1.0, 2.0])),
    ):
        result = finite_prior_gram_envelope(family)
        assert result.isotropic_inflation >= 0
        for gram in family:
            assert np.linalg.eigvalsh(result.gram-gram)[0] >= -1e-12
        assert min(result.minimum_dominance_eigenvalue) >= -1e-12


def test_prior_envelope_is_sensor_rotation_equivariant():
    family = (np.diag([1.0, 2.0]), np.array([[2.0, 0.4], [0.4, 1.0]]))
    q = np.array([[0.6, -0.8], [0.8, 0.6]])
    original = finite_prior_gram_envelope(family)
    rotated = finite_prior_gram_envelope(tuple(q @ c @ q.T for c in family))
    assert np.allclose(rotated.gram, q @ original.gram @ q.T, rtol=1e-12, atol=1e-12)


def test_prior_envelope_rejects_invalid_family():
    with pytest.raises(ValueError, match="nonempty"):
        finite_prior_gram_envelope([])
    with pytest.raises(ValueError, match="common square"):
        finite_prior_gram_envelope([np.eye(2), np.eye(3)])
    with pytest.raises(ValueError, match="positive semidefinite"):
        finite_prior_gram_envelope([np.diag([1.0, -1.0])])


def test_exact_mimicry_audit_separates_universal_mimicry_from_a_resistant_direction():
    easy = exact_mimicry_audit(np.eye(2), 4*np.eye(2))
    assert easy.all_exactly_mimickable
    assert easy.maximum_required_alternative_norm == pytest.approx(0.5)
    hard = exact_mimicry_audit(np.eye(2), np.diag([4.0, 0.25]))
    assert not hard.all_exactly_mimickable
    assert hard.count_directions_above_budget == 1


def test_exact_mimicry_audit_is_rotation_invariant_and_requires_full_rank():
    b = np.array([[1.0, 0.2], [0.0, 0.8]])
    c = np.diag([2.0, 0.5])
    q = np.array([[0.6, -0.8], [0.8, 0.6]])
    initial = exact_mimicry_audit(b, c)
    rotated = exact_mimicry_audit(q@b, q@c@q.T)
    assert np.allclose(initial.cost_eigenvalues, rotated.cost_eigenvalues, rtol=1e-12)
    with pytest.raises(ValueError, match="positive-definite"):
        exact_mimicry_audit(b, np.diag([1.0, 0.0]))


def test_finite_prior_sensor_witness_excludes_all_declared_ellipsoids():
    b = np.array([[2.0], [0.0]])
    grams = (np.diag([1.0, 4.0]), np.diag([2.25, 1.0]))
    result = finite_prior_sensor_witness(b, grams, np.array([1.0]), np.array([1.0, 0.0]))
    assert result.strict_exact_mimicry_exclusion
    assert result.sensor_norm_separation_lower == pytest.approx(0.5)
    assert result.normalized_margin_over_retained_gain == pytest.approx(0.25)
    q = np.array([[0.6, -0.8], [0.8, 0.6]])
    rotated = finite_prior_sensor_witness(q@b, tuple(q@g@q.T for g in grams),
                                          np.array([1.0]), q@np.array([1.0, 0.0]))
    assert rotated.sensor_norm_separation_lower == pytest.approx(result.sensor_norm_separation_lower)


def test_finite_prior_sensor_witness_fails_closed_on_invalid_or_borderline_input():
    b = np.array([[1.0], [0.0]])
    with pytest.raises(ValueError, match="nonempty"):
        finite_prior_sensor_witness(b, [], np.array([1.0]), np.array([1.0, 0.0]))
    with pytest.raises(ValueError, match="numerically unresolved"):
        finite_prior_sensor_witness(b, [np.eye(2)], np.array([1.0]), np.array([1.0, 0.0]))
    with pytest.raises(ValueError, match="positive semidefinite"):
        finite_prior_sensor_witness(b, [np.diag([1.0, -1.0])],
                                    np.array([1.0]), np.array([1.0, 0.0]))


def test_constructed_witness_matches_exact_convex_hull_distance_in_simple_case():
    b = np.array([[2.0], [0.0]])
    grams = (np.diag([1.0, 4.0]), np.diag([2.25, 1.0]))
    result = construct_finite_prior_sensor_witness(b, grams, np.array([1.0]))
    assert result is not None
    assert result.tight_for_convex_prior_hull
    assert result.normalized_common_margin_lower == pytest.approx(0.25)
    replay = finite_prior_sensor_witness(b, grams, result.retained_direction,
                                         result.sensor_witness)
    assert replay.normalized_margin_over_retained_gain == pytest.approx(0.25)


def test_constructed_witness_returns_no_claim_for_exact_mimicry_or_singular_prior():
    b = np.array([[1.0], [0.0]])
    assert construct_finite_prior_sensor_witness(b, [4*np.eye(2)],
                                                  np.array([1.0])) is None
    with pytest.raises(ValueError, match="positive-definite"):
        construct_finite_prior_sensor_witness(b, [np.diag([1.0, 0.0])],
                                              np.array([1.0]))


def test_model_mimicry_subspace_certifies_every_combination_with_budget_buffer():
    b = np.eye(2)
    gram = np.diag([4.0, 0.5])
    result = model_mimicry_subspace(b, gram, relative_squared_budget_buffer=0.1)
    assert result.dimension == 1
    assert result.maximum_cost_on_subspace == pytest.approx(0.25)
    assert np.allclose(result.coefficient_basis.T@result.coefficient_basis, np.eye(1))
    assert np.allclose(result.coefficient_basis@result.coefficient_basis.T,
                       np.diag([1.0, 0.0]))
    q = np.array([[0.6, -0.8], [0.8, 0.6]])
    rotated = model_mimicry_subspace(q@b, q@gram@q.T,
                                     relative_squared_budget_buffer=0.1)
    assert np.allclose(result.coefficient_basis@result.coefficient_basis.T,
                       rotated.coefficient_basis@rotated.coefficient_basis.T)


def test_model_mimicry_subspace_rejects_singular_and_unresolved_cases():
    with pytest.raises(ValueError, match="positive-definite"):
        model_mimicry_subspace(np.eye(2), np.diag([1.0, 0.0]))
    with pytest.raises(ValueError, match="numerically unresolved"):
        model_mimicry_subspace(np.eye(2), np.diag([1.0/0.9, 0.5]),
                               relative_squared_budget_buffer=0.1)
