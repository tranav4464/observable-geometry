import numpy as np
import pytest

from observable_geometry.track_b.synthetic import SyntheticConfig, generate_synthetic
from observable_geometry.track_b.physical_synthetic import geometric_regional_leadfield


def test_simulator_has_known_directed_network_and_paired_observation_shapes():
    cfg = SyntheticConfig(n_regions=9, n_scalp=7, n_active_regions=5,
                         max_indegree=2, n_ieeg_regions=3,
                         n_samples=40, seed=17)
    result = generate_synthetic(cfg)

    assert result.adjacency.shape == (9, 9)
    assert result.transition.shape == (9, 9)
    assert result.latent.shape == (40, 9)
    assert result.scalp_operator.shape == (7, 9)
    assert result.ieeg_operator.shape == (3, 9)
    assert result.scalp.shape == (40, 7)
    assert result.ieeg.shape == (40, 3)
    assert set(np.unique(result.adjacency)).issubset({0, 1})
    assert np.all(np.diag(result.adjacency) == 0)
    assert len(result.active_region_indices) == 5
    assert np.all(result.adjacency.sum(axis=1)[result.active_region_indices] == 2)
    inactive = np.setdiff1d(np.arange(9), result.active_region_indices)
    assert np.all(result.adjacency[inactive] == 0)
    assert np.all(result.adjacency[:, inactive] == 0)
    assert np.array_equal(result.ieeg_operator.sum(axis=0) <= 1,
                          np.ones(9, dtype=bool))
    assert np.allclose(result.ieeg_operator.sum(axis=0).sum(), 3)


def test_simulator_is_deterministic_and_reports_exact_finite_sample_snr():
    cfg = SyntheticConfig(n_regions=8, n_scalp=6, n_active_regions=5,
                         n_ieeg_regions=3,
                         n_samples=80, seed=23)
    a, b = generate_synthetic(cfg), generate_synthetic(cfg)

    for field in ("adjacency", "transition", "latent", "scalp_operator",
                  "ieeg_operator", "scalp", "ieeg", "active_region_indices"):
        assert np.array_equal(getattr(a, field), getattr(b, field))
    assert np.allclose(a.realized_snr_db,
                       (cfg.scalp_snr_db, cfg.ieeg_snr_db), atol=1e-12)


def test_simulated_dynamics_are_stable_and_finite():
    result = generate_synthetic(SyntheticConfig(n_regions=12, n_scalp=8,
                                n_active_regions=7, max_indegree=3,
                                n_ieeg_regions=4, n_samples=1000,
                                target_radius=0.72,
                                seed=31))
    spectral_radius = np.max(np.abs(np.linalg.eigvals(result.transition)))

    assert spectral_radius == pytest.approx(0.72, abs=1e-12)
    assert np.isfinite(result.latent).all()
    assert np.isfinite(result.scalp).all()
    assert np.isfinite(result.ieeg).all()


def test_zero_edge_graph_is_a_valid_known_truth_case():
    result = generate_synthetic(SyntheticConfig(n_regions=5, n_scalp=4,
                                n_active_regions=3, max_indegree=0,
                                n_ieeg_regions=2, n_samples=16, seed=4))

    assert not result.adjacency.any()
    assert not result.transition.any()
    assert np.isfinite(result.latent).all()


@pytest.mark.parametrize("overrides", [
    {"n_regions": 1},
    {"n_scalp": 0},
    {"n_ieeg_regions": 0},
    {"n_samples": 2},
    {"max_indegree": 10},
    {"target_radius": 1.0},
    {"scalp_snr_db": float("nan")},
])
def test_invalid_simulation_parameters_fail_closed(overrides):
    with pytest.raises(ValueError):
        generate_synthetic(SyntheticConfig(**overrides))


def test_simulator_accepts_external_leadfield_and_preserves_physical_operator():
    operator = np.array([[1.0, 0.0, 0.3, -0.2],
                         [0.0, 0.8, -0.1, 0.4],
                         [-0.5, 0.1, 0.7, 0.2],
                         [0.2, -0.4, 0.1, 0.9]])
    cfg = SyntheticConfig(n_regions=4, n_scalp=4, n_active_regions=3,
                          max_indegree=1, n_ieeg_regions=2, n_samples=64,
                          innovation_scale=1e-8, seed=7)
    generated = generate_synthetic(cfg, scalp_operator=operator)
    np.testing.assert_array_equal(generated.scalp_operator, operator)
    assert np.max(np.abs(generated.latent)) < 1e-6
    assert generated.realized_snr_db == pytest.approx((-5.0, 30.0), abs=1e-12)


def test_simulator_rejects_external_leadfield_shape_mismatch():
    cfg = SyntheticConfig(n_regions=4, n_scalp=4, n_active_regions=3,
                          n_ieeg_regions=2, n_samples=20, seed=2)
    with pytest.raises(ValueError, match="scalp_operator"):
        generate_synthetic(cfg, scalp_operator=np.ones((3, 4)))


def test_geometric_parcels_create_reproducible_reference_projected_operator():
    rng = np.random.default_rng(3)
    left = rng.normal(loc=(-0.04, 0.0, 0.0), scale=0.01, size=(40, 3))
    right = rng.normal(loc=(0.04, 0.0, 0.0), scale=0.01, size=(40, 3))
    positions = np.vstack([left, right])
    hemisphere = np.r_[np.zeros(40, dtype=np.int8), np.ones(40, dtype=np.int8)]
    leadfield = rng.normal(size=(12, 80))
    first = geometric_regional_leadfield(leadfield, positions, hemisphere,
                                         regions_per_hemisphere=(3, 2), seed=19)
    second = geometric_regional_leadfield(leadfield, positions, hemisphere,
                                          regions_per_hemisphere=(3, 2), seed=19)
    assert first.operator.shape == (12, 5)
    assert first.node_positions_m.shape == (5, 3)
    assert first.parcel_sizes.sum() == 80
    assert np.all(first.parcel_sizes > 0)
    assert np.array_equal(np.bincount(first.hemisphere), [3, 2])
    assert np.all(first.source_to_node >= 0)
    np.testing.assert_allclose(first.operator.mean(axis=0), 0.0, atol=1e-14)
    np.testing.assert_array_equal(first.operator, second.operator)
    np.testing.assert_array_equal(first.source_to_node, second.source_to_node)
