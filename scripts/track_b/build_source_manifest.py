"""Hash the source-only project snapshot without including data or run outputs."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "docs/track_b/SOURCE_SNAPSHOT_MANIFEST.json"
EXCLUDED_DIRS = {
    ".git", ".pytest_cache", "__pycache__", "build", "data", "dist",
    "outputs", "reviewer_handoff", "tmp", "vendor",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def included_files() -> list[Path]:
    result = []
    for current, directories, names in os.walk(ROOT, topdown=True):
        current_path = Path(current)
        directories[:] = sorted(
            name for name in directories
            if name not in EXCLUDED_DIRS and not name.startswith(".venv") and not name.endswith(".egg-info")
        )
        for name in names:
            path = current_path / name
            if path == TARGET or path.suffix in {".pyc", ".pyo"}:
                continue
            result.append(path)
    return sorted(result, key=lambda item: item.relative_to(ROOT).as_posix().casefold())


def main() -> None:
    files = included_files()
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Source-only project snapshot; excludes datasets, vendor checkouts, run outputs, environments, and reviewer handoff artifacts.",
        "hash_algorithm": "SHA-256",
        "self_hash": "The manifest does not hash itself; verify its containing version-control snapshot separately.",
        "license_declared": (ROOT / "LICENSE").is_file(),
        "file_count": len(files),
        "files": {
            path.relative_to(ROOT).as_posix(): {
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        },
    }
    TARGET.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_SOURCE_MANIFEST_WRITTEN", "file_count": len(files), "path": str(TARGET)}))


if __name__ == "__main__":
    main()
