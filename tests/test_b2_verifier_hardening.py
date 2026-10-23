"""Regression checks for the B2 v11 parity and runtime access gates."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "track_b" / "recompute_b2_gbf_cpu64_v11.py"
SPEC = importlib.util.spec_from_file_location("b2_v11", SCRIPT)
b2 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(b2)


def valid_pair():
    result_indices = np.full((2, b2.TOP_K), -1, dtype=np.int64)
    result_indices[0, 0] = 1
    result_indices[1, 0] = 0
    result_scores = np.full((2, b2.TOP_K), np.nan, dtype=np.float64)
    result_scores[:, 0] = 0.8
    result = {
        "indices": result_indices,
        "scores": result_scores,
        "valid": np.array([True, True], dtype=bool),
        "norms": np.array([1.0, 1.0], dtype=np.float64),
        "counts": np.array([1, 1], dtype=np.int64),
    }
    ref_indices = result_indices.astype(np.int32)
    ref_scores = result_scores.astype(np.float32)
    ref_residuals = np.sqrt(np.maximum(0.0, 1.0 - ref_scores**2)).astype(np.float32)
    reference = (
        ref_indices,
        ref_scores,
        ref_residuals,
        np.array([True, True], dtype=bool),
        np.array([1.0, 1.0], dtype=np.float64),
        np.array([1, 1], dtype=np.int32),
    )
    return result, reference


class B2ParityHardeningTests(unittest.TestCase):
    def test_matching_contract_passes(self):
        result, reference = valid_pair()
        compared = b2.compare_sealed(result, reference)
        self.assertTrue(compared["ranking_exact_match"])

    def test_nonfinite_computed_score_in_occupied_slot_fails(self):
        result, reference = valid_pair()
        result["scores"][0, 0] = np.nan
        with self.assertRaisesRegex(AssertionError, "finite-value masks"):
            b2.compare_sealed(result, reference)

    def test_nonfinite_sealed_score_in_occupied_slot_fails(self):
        result, reference = valid_pair()
        ref = list(reference)
        ref[1][0, 0] = np.nan
        with self.assertRaisesRegex(AssertionError, "finite-value masks"):
            b2.compare_sealed(result, tuple(ref))

    def test_finite_value_in_unused_score_slot_fails(self):
        result, reference = valid_pair()
        ref = list(reference)
        ref[1][0, 1] = 0.0
        with self.assertRaisesRegex(AssertionError, "finite-value masks"):
            b2.compare_sealed(result, tuple(ref))

    def test_nonfinite_sealed_residual_in_occupied_slot_fails(self):
        result, reference = valid_pair()
        ref = list(reference)
        ref[2][1, 0] = np.nan
        with self.assertRaisesRegex(AssertionError, "residual finite-value locations"):
            b2.compare_sealed(result, tuple(ref))

    def test_candidate_slot_misalignment_fails(self):
        result, reference = valid_pair()
        result["indices"][0, 0] = -1
        with self.assertRaisesRegex(AssertionError, "ranking mismatch"):
            b2.compare_sealed(result, reference)

    def test_malformed_storage_dtype_fails(self):
        result, reference = valid_pair()
        ref = list(reference)
        ref[1] = ref[1].astype(np.float64)
        with self.assertRaisesRegex(AssertionError, "sealed scores storage dtype"):
            b2.compare_sealed(result, tuple(ref))

    def test_score_outside_valid_range_fails(self):
        result, reference = valid_pair()
        result["scores"][0, 0] = 1.01
        with self.assertRaisesRegex(AssertionError, r"lie in \[0, 1\]"):
            b2.compare_sealed(result, reference)


class B2RuntimeAccessGuardTests(unittest.TestCase):
    def test_dummy_archive_denies_data_before_materializing_member(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "dummy.npz"
            log_path = root / "access.jsonl"
            np.savez(archive_path, leadfield=np.ones((1, 1)), data=np.arange(100))
            with b2.guarded_npz(archive_path, {"leadfield"}, log_path, "dummy-test") as archive:
                np.testing.assert_array_equal(archive["leadfield"], [[1.0]])
                with self.assertRaisesRegex(PermissionError, "denied key 'data'"):
                    archive["data"]
            events = [__import__("json").loads(line) for line in log_path.read_text().splitlines()]
            self.assertEqual([event["decision"] for event in events], ["allow", "deny"])
            self.assertEqual(events[1]["key"], "data")

    def test_dynamic_nonstring_key_is_denied_and_logged(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "dummy.npz"
            log_path = root / "access.jsonl"
            np.savez(archive_path, leadfield=np.ones((1, 1)))
            with b2.guarded_npz(archive_path, {"leadfield"}, log_path, "dummy-test") as archive:
                with self.assertRaisesRegex(PermissionError, "literal string keys"):
                    archive[object()]
            self.assertIn('"decision": "deny"', log_path.read_text())


if __name__ == "__main__":
    unittest.main()
