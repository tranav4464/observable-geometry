from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.track_b import fetch_localizemi_forward_models as fetcher


def _annex_key(data: bytes) -> str:
    return f"/annex/objects/MD5-s{len(data)}--{hashlib.md5(data).hexdigest()}"


def test_parse_annex_pointer_extracts_exact_size_and_hash(tmp_path: Path) -> None:
    source = tmp_path / "sub-01_fwd.fif"
    payload = b"forward-model fixture"
    source.write_text(_annex_key(payload), encoding="ascii")

    result = fetcher.parse_annex_pointer(source, "derivatives/example.fif")

    assert result.relative_path == "derivatives/example.fif"
    assert result.size_bytes == len(payload)
    assert result.md5_hex == hashlib.md5(payload).hexdigest()


@pytest.mark.parametrize(
    "pointer",
    [
        "not an annex pointer",
        "/annex/objects/MD5-s--" + "a" * 32,
        "/annex/objects/MD5-s12--" + "z" * 32,
        "/annex/objects/MD5-s12--" + "a" * 31,
    ],
)
def test_parse_annex_pointer_rejects_malformed_keys(tmp_path: Path, pointer: str) -> None:
    source = tmp_path / "placeholder"
    source.write_text(pointer, encoding="ascii")
    with pytest.raises(ValueError):
        fetcher.parse_annex_pointer(source)


def test_forward_pointer_paths_resolves_requested_subjects(tmp_path: Path) -> None:
    source = tmp_path / "derivatives/sourcemodelling/sub-03/fwd/sub-03_fwd.fif"
    source.parent.mkdir(parents=True)
    source.write_text(_annex_key(b"model"), encoding="ascii")

    records = fetcher.forward_pointer_paths(tmp_path, ["sub-03"])

    assert len(records) == 1
    assert records[0].relative_path == "derivatives/sourcemodelling/sub-03/fwd/sub-03_fwd.fif"
    with pytest.raises(ValueError, match="Invalid Localize-MI subject"):
        fetcher.forward_pointer_paths(tmp_path, ["sub-3"])


def test_source_url_targets_pinned_dataset_path() -> None:
    path = "derivatives/sourcemodelling/sub-04/fwd/sub-04_fwd.fif"
    assert fetcher.source_url(path) == f"{fetcher.GIN_ROOT}/{path}"


class _FakeResponse:
    status = 200

    def __init__(self, data: bytes):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self, size: int = -1) -> bytes:
        if not self._data:
            return b""
        out, self._data = self._data[:size], self._data[size:]
        return out


def test_fetch_and_verify_checks_hash_and_publishes_only_verified_file(tmp_path: Path) -> None:
    payload = b"verified forward payload"
    pointer = fetcher.AnnexPointer("example.fif", len(payload), hashlib.md5(payload).hexdigest())
    target = tmp_path / "example.fif"
    with patch.object(fetcher.urllib.request, "urlopen", return_value=_FakeResponse(payload)):
        record = fetcher.fetch_and_verify(pointer, target)

    assert target.read_bytes() == payload
    assert record["verified"] is True
    assert record["sha256"] == hashlib.sha256(payload).hexdigest()
    assert not target.with_name("example.fif.partial").exists()


def test_fetch_and_verify_removes_failed_partial_and_preserves_existing_file(tmp_path: Path) -> None:
    payload = b"wrong payload"
    pointer = fetcher.AnnexPointer("example.fif", len(payload), "0" * 32)
    target = tmp_path / "example.fif"
    with patch.object(fetcher.urllib.request, "urlopen", return_value=_FakeResponse(payload)):
        with pytest.raises(ValueError, match="Downloaded MD5"):
            fetcher.fetch_and_verify(pointer, target)
    assert not target.exists()
    assert not target.with_name("example.fif.partial").exists()

    target.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        fetcher.fetch_and_verify(pointer, target)
    assert target.read_bytes() == b"keep"
