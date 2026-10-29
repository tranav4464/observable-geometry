import numpy as np

from scripts.track_b.audit_wsgzp_extracted_metadata import npy_header, read_json_metadata


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
