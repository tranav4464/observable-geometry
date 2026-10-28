"""Download a NEMAR release with resumable files and SHA-256 verification.

This is an acquisition utility, not an analysis step. It uses the release
manifest served by NEMAR, does not alter the upstream files, and writes a
machine-readable verification record after each file. Use only for releases
whose license and access terms have been checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.stat().st_size if path.exists() else 0
    headers = {"Range": f"bytes={existing}-"} if existing else {}
    request = Request(url, headers=headers)
    try:
        response = urlopen(request, timeout=120)
    except Exception:
        if existing:
            path.unlink()
        response = urlopen(Request(url), timeout=120)
        existing = 0
    mode = "ab" if existing and response.headers.get("Content-Range") else "wb"
    with response, path.open(mode) as stream:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            stream.write(block)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", default="on004752/v1.0.0")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    manifest_url = f"https://data.nemar.org/{args.release}/manifest.json"
    with urlopen(manifest_url, timeout=120) as response:
        manifest = json.load(response)
    (root / "NEMAR_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    checks = root / "DOWNLOAD_CHECKS.jsonl"
    completed = 0
    with checks.open("a", encoding="utf-8") as log:
        for item in manifest:
            relative = Path(item["path"])
            target = root / relative
            if target.exists() and target.stat().st_size == int(item["size"]):
                digest = sha256(target)
                status = "existing_verified_size" if item.get("checksum_algorithm") != "sha256" else (
                    "verified" if digest.lower() == item["checksum"].lower() else "redownload_required"
                )
                if status == "redownload_required":
                    target.unlink()
                    download(item["bytes_url"], target)
                    digest = sha256(target)
                    status = "verified" if digest.lower() == item["checksum"].lower() else "hash_mismatch"
            else:
                download(item["bytes_url"], target)
                digest = sha256(target)
                status = "verified" if item.get("checksum_algorithm") != "sha256" or digest.lower() == item["checksum"].lower() else "hash_mismatch"
            record = {"path": item["path"], "expected_bytes": item["size"], "bytes": target.stat().st_size, "checksum_algorithm": item.get("checksum_algorithm"), "expected_checksum": item.get("checksum"), "sha256": digest, "status": status}
            log.write(json.dumps(record) + "\n")
            log.flush()
            if status == "hash_mismatch":
                raise RuntimeError(f"SHA-256 mismatch: {item['path']}")
            completed += 1
            if completed % 25 == 0 or completed == len(manifest):
                print(f"verified {completed}/{len(manifest)} files", flush=True)


if __name__ == "__main__":
    main()
