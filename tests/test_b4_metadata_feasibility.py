"""Tests for the metadata-only Localize-MI feasibility audit."""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "track_b"))
import audit_b4_multisubject_metadata as audit  # noqa: E402


def test_contact_pair_labels_resolve_to_canonical_contact_names():
    assert audit._contacts_for_site_label("X'1-2") == ("X'1", "X'2")
    assert audit._contacts_for_site_label("B11-12") == ("B11", "B12")


def test_multi_intensity_pair_inventory_requires_two_shared_levels():
    conditions = {
        "A1-2": {"1mA": {"01": 50}, "5mA": {"02": 50}},
        "B1-2": {"1mA": {"03": 45}, "5mA": {"04": 45}},
        "C1-2": {"1mA": {"05": 40}},
    }
    pairs = audit._multi_intensity_site_label_pairs(conditions)
    assert pairs == [("A1-2", "B1-2")]


def test_path_keys_support_inputs_outside_the_repository(tmp_path):
    assert audit.path_key(tmp_path / "external.tsv") == str((tmp_path / "external.tsv").resolve())
