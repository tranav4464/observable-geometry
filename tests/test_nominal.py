import unittest
import numpy as np

from observable_geometry.nominal import nearest_distant_signatures, whitened_unit_signatures


class NominalSignatureTests(unittest.TestCase):
    def test_scaled_polarity_reversal_is_same_signature(self):
        lead = np.array([[1., -2., -3.], [2., -4., 1.], [0., 0., 1.]])
        units, valid, _ = whitened_unit_signatures(lead, np.eye(3))
        self.assertTrue(valid.all())
        self.assertAlmostEqual(abs(float(units[:, 0] @ units[:, 1])), 1.0, places=12)

    def test_global_covariance_scale_does_not_change_normalized_scores(self):
        lead = np.array([[1., 1., -1.], [2., 2.1, 1.]])
        covariance = np.array([[2., 0.3], [0.3, 1.]])
        xyz = np.array([[0., 0., 0.], [.05, 0., 0.], [.1, 0., 0.]])
        base = nearest_distant_signatures(lead, covariance, xyz, top_k=2)
        scaled = nearest_distant_signatures(lead, covariance / 38.0, xyz, top_k=2)
        np.testing.assert_allclose(base['absolute_cosine'], scaled['absolute_cosine'],
                                   rtol=1e-12, atol=1e-12, equal_nan=True)
        np.testing.assert_allclose(base['profiled_residual_at_unit_snr'],
                                   scaled['profiled_residual_at_unit_snr'],
                                   rtol=1e-7, atol=1e-7, equal_nan=True)
        np.testing.assert_array_equal(base['candidate_indices'], scaled['candidate_indices'])

    def test_distant_match_excludes_nearby_sources(self):
        lead = np.array([[1., 1., -1.], [0., 0., 0.], [0., 0., 0.]])
        xyz = np.array([[0., 0., 0.], [.001, 0., 0.], [.05, 0., 0.]])
        result = nearest_distant_signatures(lead, np.eye(3), xyz,
                                            min_distance_mm=10, top_k=1)
        self.assertEqual(int(result['candidate_indices'][0, 0]), 2)
        self.assertAlmostEqual(float(result['absolute_cosine'][0, 0]), 1.0)

    def test_rejects_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            nearest_distant_signatures(np.eye(2), np.eye(2), np.zeros((3, 3)))

    def test_invalid_query_is_not_reported_as_distinguishable(self):
        lead = np.array([[0., 1., 1.], [0., 0., 1.]])
        xyz = np.array([[0., 0., 0.], [.05, 0., 0.], [.1, 0., 0.]])
        result = nearest_distant_signatures(lead, np.eye(2), xyz, top_k=4)
        self.assertFalse(result['valid_source'][0])
        self.assertTrue(np.isnan(result['absolute_cosine'][0]).all())
        self.assertTrue((result['candidate_indices'][0] == -1).all())
        self.assertEqual(result['summary']['source_count_with_distant_alternative'], 2)

    def test_one_valid_source_returns_clear_no_alternative_error(self):
        lead = np.array([[1., 0.], [0., 0.]])
        xyz = np.array([[0., 0., 0.], [.05, 0., 0.]])
        with self.assertRaisesRegex(ValueError, 'no valid source'):
            nearest_distant_signatures(lead, np.eye(2), xyz)

    def test_missing_top_k_slots_use_sentinel_and_nan(self):
        lead = np.array([[1., 1.], [0., 1.]])
        xyz = np.array([[0., 0., 0.], [.05, 0., 0.]])
        result = nearest_distant_signatures(lead, np.eye(2), xyz, top_k=4)
        self.assertTrue(np.all(result['candidate_indices'][:, 1:] == -1))
        self.assertTrue(np.isnan(result['absolute_cosine'][:, 1:]).all())

    def test_rejects_component_outside_noise_support(self):
        lead = np.array([[1., 1.], [0., 100.]])
        with self.assertRaisesRegex(ValueError, 'outside the supported'):
            whitened_unit_signatures(lead, np.diag([1., 0.]))

    def test_threshold_set_is_complete_csr(self):
        lead = np.array([[1., 1., -1., 0.], [0., 0., 0., 1.]])
        xyz = np.array([[0., 0., 0.], [.05, 0., 0.], [.1, 0., 0.], [.15, 0., 0.]])
        result = nearest_distant_signatures(lead, np.eye(2), xyz, top_k=1,
                                            collect_above=.99)
        sparse = result['threshold_set']
        self.assertEqual(len(sparse['indptr']), 5)
        self.assertEqual(int(sparse['indptr'][-1]), len(sparse['indices']))
        for i in range(4):
            lo, hi = sparse['indptr'][i:i+2]
            self.assertTrue(np.all(sparse['absolute_cosine'][lo:hi] >= .99))
            self.assertFalse(np.any(sparse['indices'][lo:hi] == i))


if __name__ == '__main__':
    unittest.main()
