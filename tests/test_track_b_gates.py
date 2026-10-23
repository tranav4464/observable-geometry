import json
import tempfile
import unittest
from pathlib import Path

from observable_geometry.track_b.gates import validate_gate_register


class GateRegisterTests(unittest.TestCase):
    def test_current_gate_register_has_complete_evidence_and_valid_order(self):
        root = Path(__file__).resolve().parents[1]
        register = json.loads((root / "docs/track_b/GATE_REGISTER.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_gate_register(register, root), [])

    def test_rejects_started_gate_with_missing_evidence(self):
        register = {"gates": [{"id": "A", "status": "IN_PROGRESS",
                               "evidence": ["missing.json"], "blocking": []}]}
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_gate_register(register, Path(directory))
        self.assertTrue(any("missing evidence path" in error for error in errors))

    def test_rejects_advanced_gate_before_prerequisite_passes(self):
        register = {"gates": [
            {"id": "A", "status": "IN_PROGRESS", "evidence": [], "blocking": ["B"]},
            {"id": "B", "status": "IN_PROGRESS", "evidence": [], "blocking": []},
        ]}
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_gate_register(register, Path(directory))
        self.assertTrue(any("prerequisite A is IN_PROGRESS" in error for error in errors))

    def test_rejects_cyclic_gate_dependencies(self):
        register = {"gates": [
            {"id": "A", "status": "NOT_STARTED", "evidence": [], "blocking": ["B"]},
            {"id": "B", "status": "NOT_STARTED", "evidence": [], "blocking": ["A"]},
        ]}
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_gate_register(register, Path(directory))
        self.assertTrue(any("contains a cycle" in error for error in errors))

    def test_contract_version_requires_stage_exit_and_verification_fields(self):
        register = {"stage_contract_version": 1, "gates": [{
            "id": "A", "status": "NOT_STARTED", "evidence": [], "blocking": [],
        }]}
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_gate_register(register, Path(directory))
        self.assertTrue(any("objective must be a str" in error for error in errors))
        self.assertTrue(any("exit_criteria must be a list" in error for error in errors))
        self.assertTrue(any("failure_route must be a str" in error for error in errors))

    def test_contract_pass_requires_existing_verification_evidence(self):
        register = {"stage_contract_version": 1, "gates": [{
            "id": "A", "status": "PASS", "evidence": ["proof.txt"], "blocking": [],
            "objective": "Check one thing", "exit_criteria": ["It passes"],
            "verification": ["Run the check"], "falsification_check": "Try a negative control",
            "failure_route": "Revise and rerun", "independent_review": "Second reviewer checks",
            "verification_evidence": [],
        }]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "proof.txt").write_text("evidence", encoding="utf-8")
            errors = validate_gate_register(register, root)
        self.assertTrue(any("PASS requires verification_evidence" in error for error in errors))

    def test_rejects_missing_authority_document(self):
        register = {"authority": "missing-plan.md", "gates": [
            {"id": "A", "status": "NOT_STARTED", "evidence": [], "blocking": []},
        ]}
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_gate_register(register, Path(directory))
        self.assertTrue(any("missing authority document" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
