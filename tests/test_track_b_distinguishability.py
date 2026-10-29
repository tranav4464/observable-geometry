import numpy as np
import pytest

from observable_geometry.nominal import nearest_distant_signatures
from observable_geometry.track_b.distinguishability import compute_distinguishability, summarize


def test_analytic_orthogonal_and_identical_signatures_are_ranked_in_float64():
    # Algebraic software fixture only; this is not a neural-signal simulation.
    leadfield = np.array([[1.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float64)
    covariance = np.eye(2, dtype=np.float64)
    coordinates_m = np.array([[0.0, 0, 0], [.03, 0, 0], [.06, 0, 0]], dtype=np.float64)
    result = compute_distinguishability(leadfield, covariance, coordinates_m, top_k=2)

    assert result.absolute_cosine.dtype == np.float64
    assert result.candidate_indices[0, 0] == 1
    assert result.absolute_cosine[0, 0] == pytest.approx(1.0)
    assert result.profiled_residual[0, 0] == pytest.approx(0.0)
    assert result.candidate_indices[2, 0] == 0
    assert result.absolute_cosine[2, 0] == pytest.approx(0.0)
    assert result.profiled_residual[2, 0] == pytest.approx(1.0)
    assert summarize(result, 20.0)["valid_signature_count"] == 3


def test_covariance_global_scale_invariance_and_stable_tie_breaking():
    leadfield = np.array([[1.0, -1.0, 1.0], [0.0, 0.0, 0.0]])
    coordinates_m = np.array([[0.0, 0, 0], [.03, 0, 0], [.06, 0, 0]])
    a = compute_distinguishability(leadfield, np.eye(2), coordinates_m, top_k=2)
    b = compute_distinguishability(leadfield, 17.0 * np.eye(2), coordinates_m, top_k=2)
    np.testing.assert_array_equal(a.candidate_indices, b.candidate_indices)
    np.testing.assert_allclose(a.absolute_cosine, b.absolute_cosine, rtol=1e-14, atol=1e-14, equal_nan=True)
    assert a.candidate_indices[0, :2].tolist() == [1, 2]


@pytest.mark.parametrize("bad_cov", [
    np.array([[1.0, 0.2], [0.0, 1.0]]),
    np.diag([1.0, -0.01]),
    np.zeros((2, 2)),
])
def test_invalid_covariance_contract_is_rejected(bad_cov):
    leadfield = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])
    xyz = np.array([[0, 0, 0], [.03, 0, 0], [.06, 0, 0]], dtype=float)
    with pytest.raises(ValueError):
        compute_distinguishability(leadfield, bad_cov, xyz)


def test_leadfield_outside_covariance_support_is_not_silently_discarded():
    leadfield = np.array([[1.0, 1.0], [0.2, 0.0]])
    covariance = np.diag([1.0, 0.0])
    xyz = np.array([[0, 0, 0], [.03, 0, 0]], dtype=float)
    with pytest.raises(ValueError, match="outside the supported covariance subspace"):
        compute_distinguishability(leadfield, covariance, xyz)


def test_float64_track_b_api_matches_legacy_topk_and_threshold_csr_contract():
    # Fixed algebraic fixture only; no synthetic neural observations are used.
    leadfield = np.array([
        [1.0, 1.0, 0.0, -1.0, 0.2],
        [0.0, 0.0, 1.0, 1.0, 0.5],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ], dtype=np.float64)
    covariance = np.diag([2.0, 0.7, 0.0])
    coordinates_m = np.column_stack((np.arange(5) * 0.03, np.zeros((5, 2))))

    current = compute_distinguishability(
        leadfield, covariance, coordinates_m, minimum_distance_mm=20.0, top_k=4,
        block_size=2,
    )
    legacy = nearest_distant_signatures(
        leadfield, covariance, coordinates_m, min_distance_mm=20.0, top_k=4,
        block_size=3, collect_above=0.7,
    )

    np.testing.assert_array_equal(
        current.candidate_indices, legacy["candidate_indices"].astype(np.int64)
    )
    np.testing.assert_array_equal(current.valid_source, legacy["valid_source"])
    np.testing.assert_array_equal(current.candidate_count, legacy["distant_candidate_count"])
    np.testing.assert_allclose(
        current.whitened_norm, legacy["whitened_norm"], rtol=1e-14, atol=1e-14
    )
    np.testing.assert_allclose(
        current.absolute_cosine, legacy["absolute_cosine"], rtol=0.0, atol=1e-7,
        equal_nan=True,
    )
    np.testing.assert_allclose(
        current.profiled_residual, legacy["profiled_residual_at_unit_snr"],
        rtol=0.0, atol=2e-4, equal_nan=True,
    )

    sparse = legacy["threshold_set"]
    for source in range(len(coordinates_m)):
        lo, hi = sparse["indptr"][source:source + 2]
        ranked = current.candidate_indices[source]
        scores = current.absolute_cosine[source]
        expected = ranked[np.isfinite(scores) & (scores >= 0.7)]
        np.testing.assert_array_equal(sparse["indices"][lo:hi], expected)
