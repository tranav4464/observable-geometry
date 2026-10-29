from pathlib import Path
import tempfile
import unittest

from scripts.track_b.run_b8_release_tests import (
    archive_skips_are_expected as check_archive_skips,
    test_results as summarize_junit,
)
from scripts.track_b.verify_b8_wheel_source import normalize_eol


class B8ReleaseTestRunnerTests(unittest.TestCase):
    def test_eol_normalization_maps_windows_crlf_to_git_lf(self):
        self.assertEqual(normalize_eol(b"first\r\nsecond\r\n"), b"first\nsecond\n")

    def test_eol_normalization_preserves_other_bytes(self):
        self.assertEqual(normalize_eol(b"first\nsecond\rthird"), b"first\nsecond\rthird")

    def test_accepts_only_the_two_documented_source_archive_skips(self):
        skips = [
            {
                "classname": "tests.test_track_b_gates.GateRegisterTests",
                "name": "test_current_gate_register_has_complete_evidence_and_valid_order",
                "reason": "source-only distributions omit the repository evidence outputs; run separately",
            },
            {
                "classname": "tests.test_wsgzp_coregistration_audit",
                "name": "test_fiducial_transform_is_not_treated_as_frame_validation",
                "reason": "Local WSGZP dataset is not available",
            },
        ]
        self.assertTrue(check_archive_skips(skips))

    def test_accepts_no_skips_when_archive_has_all_required_inputs(self):
        self.assertTrue(check_archive_skips([]))

    def test_accepts_a_subset_of_documented_skips(self):
        self.assertTrue(check_archive_skips([
            {
                "classname": "tests.test_track_b_gates.GateRegisterTests",
                "name": "test_current_gate_register_has_complete_evidence_and_valid_order",
                "reason": "source-only distributions omit the repository evidence outputs; run separately",
            }
        ]))

    def test_rejects_any_unexpected_skip(self):
        skips = [
            {"classname": "tests.test_unrelated", "name": "test_skipped", "reason": "environment"},
        ]
        self.assertFalse(check_archive_skips(skips))

    def test_rejects_known_skip_with_an_unexpected_reason(self):
        skips = [
            {
                "classname": "tests.test_track_b_gates.GateRegisterTests",
                "name": "test_current_gate_register_has_complete_evidence_and_valid_order",
                "reason": "some other reason",
            },
            {
                "classname": "tests.test_wsgzp_coregistration_audit",
                "name": "test_fiducial_transform_is_not_treated_as_frame_validation",
                "reason": "Local WSGZP dataset is not available",
            },
        ]
        self.assertFalse(check_archive_skips(skips))

    def test_junit_parser_returns_skip_names_and_reasons(self):
        xml = """<testsuites><testsuite tests="2" failures="0" errors="0" skipped="1">
        <testcase classname="sample" name="passed" />
        <testcase classname="sample" name="skipped"><skipped message="known reason" /></testcase>
        </testsuite></testsuites>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "junit.xml"
            path.write_text(xml, encoding="utf-8")
            result, skipped = summarize_junit(path)
        self.assertEqual(result, {"passed": 1, "skipped": 1, "failed": 0, "total": 2})
        self.assertEqual(skipped, [{"classname": "sample", "name": "skipped", "reason": "known reason"}])


if __name__ == "__main__":
    unittest.main()
