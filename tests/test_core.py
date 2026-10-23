"""Algebraic correctness checks only. No synthetic brain experiment is implied."""
import unittest
import numpy as np
from observable_geometry import average_reference, fit_linear_geometry, robust_sensor_scores


class CoreTests(unittest.TestCase):
    def test_scalar_bayes_closed_form(self):
        f = fit_linear_geometry([[3]], [[2]], [[1]], [[4]], [[1]])
        np.testing.assert_allclose(f.coefficient_mean, [[.75]])
        np.testing.assert_allclose(f.coefficient_covariance, [[.5]])

    def test_null_direction_retains_prior_uncertainty(self):
        f = fit_linear_geometry([[2]], [[1, 0]], np.eye(2), [[1]], np.eye(2))
        self.assertEqual(f.forward_rank, 1)
        np.testing.assert_allclose(f.coefficient_covariance, np.diag([.5, 1]))
        np.testing.assert_allclose(f.information_fractions, [.5, 0])

    def test_average_reference_rank_and_common_signal_invariance(self):
        x, l, c = average_reference([[1], [2], [4]], np.eye(3), np.eye(3))
        f = fit_linear_geometry(x, l, np.eye(3), c, np.eye(3))
        y, ll, cc = average_reference([[101], [102], [104]], np.eye(3), np.eye(3))
        g = fit_linear_geometry(y, ll, np.eye(3), cc, np.eye(3))
        self.assertEqual(f.noise_rank, 2)
        np.testing.assert_allclose(f.source_mean, g.source_mean, atol=1e-12)

    def test_consistent_voltage_unit_change_invariant(self):
        x, l, c, q = np.array([[3.], [1.]]), np.eye(2), np.eye(2), np.eye(2)
        f = fit_linear_geometry(x, l, np.eye(2), c, q)
        g = fit_linear_geometry(x*1e-6, l*1e-6, np.eye(2), c*1e-12, q)
        np.testing.assert_allclose(f.source_mean, g.source_mean)
        np.testing.assert_allclose(f.source_std, g.source_std)

    def test_reject_inconsistent_reference(self):
        _, l, c = average_reference([[1], [2]], np.eye(2), np.eye(2))
        with self.assertRaisesRegex(ValueError, "unsupported noise direction"):
            fit_linear_geometry([[1], [2]], l, np.eye(2), c, np.eye(2))

    def test_reject_negative_covariance(self):
        with self.assertRaises(ValueError):
            fit_linear_geometry([[1]], [[1]], [[1]], [[-1]], [[1]])

    def test_sensor_score_matches_explicit_covariance_update(self):
        cov = np.diag([.5, 2.])
        row = np.array([1., 2.])
        result = robust_sensor_scores(cov[None], row[None, None], [[3]], np.eye(2))
        updated = np.linalg.inv(np.linalg.inv(cov) + np.outer(row, row)/3)
        np.testing.assert_allclose(result['worst_case_reduction'], [np.trace(cov-updated)])

    def test_robust_selection_penalizes_model_sensitive_candidate(self):
        cov = np.array([np.eye(2), np.eye(2)])
        rows = np.array([[[10., 0], [0, 1]], [[.01, 0], [0, 1]]])
        r = robust_sensor_scores(cov, rows, np.ones((2, 2)), np.eye(2))
        self.assertEqual(r['ranking'][0], 1)


if __name__ == '__main__':
    unittest.main()
