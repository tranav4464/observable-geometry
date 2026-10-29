"""Read-only OSF API inventory check for WSGZP coordinate provenance files.

Only JSON:API folder/file metadata is requested. This script never downloads
file contents and never accesses EEG/SEEG samples.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any
from urllib.request import Request, urlopen


GEOMETRY_EXTENSIONS = {
    ".hpts", ".elp", ".sfp", ".pos", ".mrk", ".h5", ".hdf5", ".xfm", ".mat", ".fif"
}
GEOMETRY_NAME = re.compile(
    r"(?<![a-z0-9])(?:transform|registration|digitiz|coreg|fiducial|egi[_-]?dig)(?![a-z0-9])",
    re.I,
)


def is_geometry_candidate(name: str) -> bool:
    """Return whether a file name could indicate a registration artifact."""
    return Path(name).suffix.lower() in GEOMETRY_EXTENSIONS or bool(GEOMETRY_NAME.search(name))


def fetch_json(url: str, timeout: float = 30.0) -> tuple[dict[str, Any], str]:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.api+json",
            "User-Agent": "Observable-Geometry-read-only-metadata-audit/1.0",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"OSF API returned HTTP {response.status} for {url}")
        payload = response.read()
    parsed = json.loads(payload)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("data"), list):
        raise ValueError(f"Unexpected OSF JSON:API response at {url}")
    return parsed, hashlib.sha256(payload).hexdigest()


def inventory(node_id: str = "wsgzp") -> dict[str, Any]:
    root_url = f"https://api.osf.io/v2/nodes/{node_id}/files/osfstorage/"
    queue = deque([root_url])
    visited: set[str] = set()
    entries: list[dict[str, Any]] = []
    response_hashes: dict[str, str] = {}
    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        payload, digest = fetch_json(url)
        response_hashes[url] = digest
        for item in payload["data"]:
            attrs = item.get("attributes") or {}
            name = str(attrs.get("name") or "")
            path = str(attrs.get("materialized_path") or attrs.get("path") or name)
            kind = str(attrs.get("kind") or "")
            entry = {
                "id": item.get("id"),
                "kind": kind,
                "name": name,
                "path": path,
                "size_bytes": attrs.get("size"),
                "sha256_metadata": (attrs.get("extra") or {}).get("hashes", {}).get("sha256"),
            }
            entries.append(entry)
            if kind == "folder":
                related = (
                    (item.get("relationships") or {})
                    .get("files", {})
                    .get("links", {})
                    .get("related", {})
                    .get("href")
                )
                if related:
                    queue.append(str(related))
        next_url = (payload.get("links") or {}).get("next")
        if isinstance(next_url, str):
            queue.append(next_url)

    entries.sort(key=lambda row: (row["path"].lower(), row["name"].lower()))
    candidates = [
        entry for entry in entries
        if entry["kind"] == "file"
        and is_geometry_candidate(entry["name"])
    ]
    return {
        "audit_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "node_id": node_id,
        "root_api_url": root_url,
        "access_scope": "OSF JSON:API file and folder metadata only; no file-content downloads",
        "signal_samples_accessed": False,
        "response_sha256": response_hashes,
        "entry_count": len(entries),
        "file_count": sum(entry["kind"] == "file" for entry in entries),
        "geometry_candidate_count": len(candidates),
        "geometry_candidates": candidates,
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node-id", default="wsgzp")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    result = inventory(args.node_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "entry_count": result["entry_count"],
        "file_count": result["file_count"],
        "geometry_candidate_count": result["geometry_candidate_count"],
        "signal_samples_accessed": result["signal_samples_accessed"],
        "status": "PASS",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
