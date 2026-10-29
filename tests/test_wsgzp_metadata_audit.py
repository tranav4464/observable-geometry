import numpy as np

from scripts.track_b.audit_wsgzp_extracted_metadata import (
    eeg_coordinate_contract,
    npy_header,
    read_json_metadata,
)
from scripts.track_b.validate_wsgzp_coordinate_metadata import build_fixture


def test_json_parser_reports_trailing_comma_repair(tmp_path):
    strict = tmp_path / "strict.json"
    strict.write_text('{"a": 1}', encoding="utf-8")
    parsed, repaired = read_json_metadata(strict)
    assert parsed == {"a": 1}
    assert repaired is False

    malformed = tmp_path / "trailing.json"
    malformed.write_text('{"a": 1,\n}', encoding="utf-8")
    parsed, repaired = read_json_metadata(malformed)
    assert parsed == {"a": 1}
    assert repaired is True


def test_npy_header_reader_returns_shape_without_loading_payload(tmp_path):
    path = tmp_path / "header_only.npy"
    values = np.zeros((2, 3, 4), dtype=np.float32)
    np.save(path, values)
    with path.open("r+b") as stream:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            _, _, _ = np.lib.format.read_array_header_1_0(stream)
        else:
            _, _, _ = np.lib.format.read_array_header_2_0(stream)
        stream.truncate(stream.tell())

    result = npy_header(path)
    assert result["shape"] == [2, 3, 4]
    assert result["dtype"] == "float32"


def test_eeg_t1w_coordinate_label_is_flagged_as_bids_1_6_nonconformance():
    result = eeg_coordinate_contract(
        {
            "EEGCoordinateSystem": "T1w",
            "AnatomicalLandmarkCoordinateSystem": "T1w",
            "EEGCoordinateUnits": "mm",
        },
        "1.6.0",
    )
    assert result["coordinate_semantics_status"] == "BIDS_1_6_COORDINATE_KEYWORD_NOT_ALLOWED"
    assert "does not list T1w" in result["coordinate_semantics_note"]
    assert "not proof" in result["coordinate_semantics_note"]


def test_eeg_t1w_semantics_are_flagged_even_when_bids_version_is_unknown():
    result = eeg_coordinate_contract({"EEGCoordinateSystem": "T1w"}, None)
    assert result["coordinate_semantics_status"] == "COORDINATE_KEYWORD_REQUIRES_VERSION_CHECK"


def test_eeg_other_coordinate_system_requires_description():
    result = eeg_coordinate_contract({"EEGCoordinateSystem": "Other"}, "1.6.0")
    assert result["coordinate_semantics_status"] == "DESCRIPTION_REQUIRED_FOR_OTHER"


def test_eeg_captrak_does_not_receive_targeted_warning():
    result = eeg_coordinate_contract({"EEGCoordinateSystem": "CapTrak"}, "1.6.0")
    assert result["coordinate_semantics_status"] == "NO_TARGETED_WARNING"
    assert result["coordinate_semantics_note"] is None


def test_coordinate_validator_fixture_copies_metadata_only_and_refuses_overwrite(tmp_path):
    source = tmp_path / "source"
    eeg = source / "derivatives" / "epochs" / "sub-01" / "eeg"
    eeg.mkdir(parents=True)
    (source / "dataset_description.json").write_text(
        '{"BIDSVersion":"1.6.0"}', encoding="utf-8"
    )
    (source / "sub-01").mkdir()
    (eeg / "sub-01_task-ccepcoreg_coordsystem.json").write_text(
        '{"EEGCoordinateSystem":"T1w"}', encoding="utf-8"
    )
    (eeg / "sub-01_task-ccepcoreg_electrodes.tsv").write_text(
        "name\tx\ty\tz\nCz\t0\t0\t0\n", encoding="utf-8"
    )
    (eeg / "sub-01_task-ccepcoreg_run-01_epochs.npy").write_bytes(b"signal")

    fixture = tmp_path / "fixture"
    copied = build_fixture(source, fixture, "sub-01")
    assert len(copied) == 2
    assert sorted(path.name for path in fixture.rglob("*.*")) == sorted([
        "dataset_description.json",
        "sub-01_task-ccepcoreg_coordsystem.json",
        "sub-01_task-ccepcoreg_electrodes.tsv",
    ])
    try:
        build_fixture(source, fixture, "sub-01")
    except FileExistsError:
        pass
    else:
        raise AssertionError("existing fixture should not be overwritten")
