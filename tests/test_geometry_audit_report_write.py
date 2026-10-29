import json

import pytest

from scripts.track_b.audit_geometry import contacts_for, write_report


def test_geometry_audit_report_is_written_as_new_json(tmp_path):
    path = tmp_path / "nested" / "geometry.json"
    payload = {"status": "PASS", "scope": "metadata-only"}

    write_report(payload, path)

    assert json.loads(path.read_text(encoding="utf-8")) == payload


def test_geometry_audit_report_refuses_to_overwrite(tmp_path):
    path = tmp_path / "geometry.json"
    path.write_text("sealed result", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_report({"status": "replacement"}, path)

    assert path.read_text(encoding="utf-8") == "sealed result"


@pytest.mark.parametrize(
    "label, expected",
    [
        ("K13-14 1mA", ("K13", "K14")),
        ("X'1-2 1mA", ("X'1", "X'2")),
        ("N10-11 5mA", ("N10", "N11")),
    ],
)
def test_geometry_audit_contact_parser_matches_dataset_label_convention(label, expected):
    assert contacts_for(label) == expected
