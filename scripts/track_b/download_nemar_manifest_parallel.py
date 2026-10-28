"""Parallel, resumable NEMAR manifest downloader with SHA-256 checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fetch(item: dict, root: Path) -> dict:
    target = root / Path(item["path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    expected_size = int(item["size"])
    if not target.exists() or target.stat().st_size != expected_size:
        existing = target.stat().st_size if target.exists() else 0
        request = Request(item["bytes_url"], headers={"Range": f"bytes={existing}-"} if existing else {})
        for attempt in range(6):
            try:
                with urlopen(request, timeout=180) as response:
                    append = existing and response.headers.get("Content-Range")
                    mode = "ab" if append else "wb"
                    with target.open(mode) as stream:
                        while True:
                            block = response.read(1024 * 1024)
                            if not block:
                                break
                            stream.write(block)
                break
            except (HTTPError, URLError):
                if attempt == 5:
                    raise
                time.sleep(2 ** attempt)
    actual_size = target.stat().st_size
    actual_hash = digest(target)
    algorithm = item.get("checksum_algorithm")
    status = "size_only" if algorithm != "sha256" and actual_size == expected_size else (
        "verified" if actual_hash.lower() == item["checksum"].lower() else "hash_mismatch"
    )
    if actual_size != expected_size or status == "hash_mismatch":
        raise RuntimeError(f"verification failed for {item['path']}: {actual_size=} {status=}")
    return {"path": item["path"], "expected_bytes": expected_size, "bytes": actual_size,
            "checksum_algorithm": algorithm, "expected_checksum": item.get("checksum"),
            "sha256": actual_hash, "status": status}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", default="on004752/v1.0.0")
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with urlopen(f"https://data.nemar.org/{args.release}/manifest.json", timeout=120) as response:
        manifest = json.load(response)
    (root / "NEMAR_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    records = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(fetch, item, root) for item in manifest]
        for index, future in enumerate(as_completed(futures), start=1):
            record = future.result()
            records.append(record)
            if index % 25 == 0 or index == len(manifest):
                print(f"verified {index}/{len(manifest)} files", flush=True)
    records.sort(key=lambda row: row["path"])
    (root / "DOWNLOAD_CHECKS.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    if len(records) != len(manifest):
        raise RuntimeError("manifest and verification record counts differ")


if __name__ == "__main__":
    main()
