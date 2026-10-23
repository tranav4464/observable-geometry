from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/track_b/audit_osf_wsgzp_license_metadata.py"
SPEC = importlib.util.spec_from_file_location("osf_license_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_audit_follows_metadata_only_folder_links_and_does_not_find_embedded_license():
    root = f"{MODULE.API}/nodes/{MODULE.NODE}/files/osfstorage/"
    child = f"{MODULE.API}/nodes/{MODULE.NODE}/files/osfstorage/folder-id/"
    license_url = f"{MODULE.API}/licenses/license-id/"
    responses = {
        f"{MODULE.API}/nodes/{MODULE.NODE}/": {
            "data": {
                "attributes": {"title": "test project", "public": True},
                "relationships": {"license": {"data": {"id": "license-id"}}},
            }
        },
        license_url: {
            "data": {"attributes": {"name": "Other", "text": "See license.txt", "url": ""}}
        },
        root: {
            "data": [
                {
                    "attributes": {"name": "data", "materialized_path": "/data/", "kind": "folder"},
                    "relationships": {"files": {"links": {"related": {"href": child}}}},
                    "links": {"download": "https://files.example/archive.zip"},
                }
            ],
            "links": {},
        },
        child: {
            "data": [
                {"attributes": {"name": "recording.zip", "materialized_path": "/data/recording.zip", "kind": "file"}},
            ],
            "links": {},
        },
    }
    requested: list[str] = []

    def fake_fetch(url: str) -> dict:
        requested.append(url)
        return responses[url]

    result = MODULE.audit(fake_fetch)

    assert result["license"]["name"] == "Other"
    assert result["license_file_listed"] is False
    assert result["visible_file_count"] == 1
    assert result["visible_storage_inventory"][-1]["name"] == "recording.zip"
    assert all("download" not in url for url in requested)
    assert requested == [f"{MODULE.API}/nodes/{MODULE.NODE}/", license_url, root, child]
