"""Static tests for the B2 verifier's prepared-bundle key boundary."""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "track_b"))
import audit_b2_signal_access_boundary as boundary  # noqa: E402


class PreparedBundleAccessBoundaryTests(unittest.TestCase):
    def keys_read(self, source: str) -> set[str]:
        return boundary.prepared_bundle_keys_read_by_verifier(ast.parse(source))

    def test_declared_model_keys_are_detected(self):
        source = '''
with np.load("prepared_bundle.npz", allow_pickle=False) as z:
    leadfield = z["leadfield"]
    covariance = z["noise_cov"]
'''
        self.assertEqual(self.keys_read(source), {"leadfield", "noise_cov"})

    def test_eeg_data_access_is_exposed_as_an_unexpected_key(self):
        source = '''
with np.load("prepared_bundle.npz", allow_pickle=False) as z:
    leadfield = z["leadfield"]
    eeg = z["data"]
'''
        found = self.keys_read(source)
        self.assertEqual(found - boundary.EXPECTED_PREPARED_KEYS, {"data"})

    def test_dynamic_archive_key_is_rejected(self):
        source = '''
with np.load("prepared_bundle.npz", allow_pickle=False) as z:
    leadfield = z[key]
'''
        with self.assertRaisesRegex(ValueError, "nonliteral key"):
            self.keys_read(source)


if __name__ == "__main__":
    unittest.main()
