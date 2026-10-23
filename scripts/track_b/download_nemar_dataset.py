"""Download a manifest-pinned NEMAR raw EEG/iEEG subset with integrity checks."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CHUNK = 4 * 1024 * 1024


def checksum(path: Path, algorithm: str, expected_size: int) -> str:
    if algorithm == "sha256":
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK), b""):
                digest.update(block)
        return digest.hexdigest()
    if algorithm == "git":
        digest = hashlib.sha1()
        digest.update(f"blob {expected_size}\0".encode("ascii"))
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK), b""):
                digest.update(block)
        return digest.hexdigest()
    raise ValueError(f"unsupported manifest checksum algorithm: {algorithm!r}")


def valid_file(path: Path, entry: dict) -> bool:
    if not path.is_file() or path.stat().st_size != int(entry["size"]):
        return False
    return checksum(path, entry["checksum_algorithm"], int(entry["size"])) == entry["checksum"]


def download_one(root: Path, entry: dict, retries: int = 5) -> tuple[str, int, str]:
    rel = PurePosixPath(entry["path"])
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe manifest path: {entry['path']!r}")
    dest = root.joinpath(*rel.parts)
    dest.parent.mkdir(parents=True, exist_ok=True)
    size = int(entry["size"])
    if valid_file(dest, entry):
        return entry["path"], size, "already_verified"
    part = dest.with_name(dest.name + ".part")
    url = entry.get("bytes_url") or entry["url"]
    for attempt in range(retries):
        offset = part.stat().st_size if part.exists() else 0
        if offset > size:
            part.unlink()
            offset = 0
        headers = {"User-Agent": "TKS-ObservableGeometry/0.1 (research dataset acquisition)"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=180) as response:
                code = getattr(response, "status", 200)
                append = offset > 0 and code == 206
                if offset > 0 and not append:
                    offset = 0
                mode = "ab" if append else "wb"
                with part.open(mode) as stream:
                    while block := response.read(CHUNK):
                        stream.write(block)
            if part.stat().st_size != size:
                raise IOError(f"size mismatch: expected {size}, found {part.stat().st_size}")
            actual = checksum(part, entry["checksum_algorithm"], size)
            if actual != entry["checksum"]:
                raise IOError(f"checksum mismatch: expected {entry['checksum']}, found {actual}")
            os.replace(part, dest)
            return entry["path"], size, "downloaded_verified"
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            if attempt + 1 == retries:
                raise RuntimeError(f"failed {entry['path']} after {retries} attempts: {exc}") from exc
            time.sleep(min(2**attempt, 20))
    raise AssertionError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 12:
        parser.error("--workers must be between 1 and 12")
    root = args.output.resolve()
    data_root = (Path(__file__).resolve().parents[2] / "data" / "track_b").resolve()
    if data_root not in root.parents:
        parser.error(f"output must be inside {data_root}")
    entries = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    if not isinstance(entries, list) or not entries:
        parser.error("manifest must be a nonempty JSON list")
    for entry in entries:
        path = entry.get("path", "")
        if not path.startswith("sub-") or not any(f"/{modality}/" in path for modality in ("eeg", "ieeg")):
            parser.error(f"manifest contains a non-raw EEG/iEEG path: {path}")
    root.mkdir(parents=True, exist_ok=True)
    args.status.parent.mkdir(parents=True, exist_ok=True)
    completed = 0
    total = sum(int(entry["size"]) for entry in entries)
    with args.status.open("a", encoding="utf-8") as log:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(download_one, root, entry) for entry in entries]
            for future in as_completed(futures):
                path, size, state = future.result()
                completed += 1
                log.write(json.dumps({"path": path, "bytes": size, "status": state}) + "\n")
                log.flush()
                print(f"{completed}/{len(entries)} {state} {path} ({size} bytes)", flush=True)
    verified_bytes = sum(int(entry["size"]) for entry in entries)
    if verified_bytes != total:
        raise RuntimeError("internal byte-accounting mismatch")
    print(json.dumps({"files": len(entries), "verified_bytes": verified_bytes,
                      "output": str(root), "status_log": str(args.status)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
