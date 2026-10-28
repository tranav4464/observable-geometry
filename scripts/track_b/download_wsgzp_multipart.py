"""Download the public WSGZP multipart archive without extracting signal files.

The archive is preserved as downloaded so the embedded license can be checked
before any neural recording is opened or used.  Every part is hashed after
download.  This script does not infer reuse permission from public visibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FILES = [
    ("ccepcoreg-bids.z01", "https://osf.io/download/7h5pj/", 4294967296),
    ("ccepcoreg-bids.z02", "https://osf.io/download/cktnz/", 4294967296),
    ("ccepcoreg-bids.z03", "https://osf.io/download/9g7kw/", 4294967296),
    ("ccepcoreg-bids.z04", "https://osf.io/download/d4g9j/", 4294967296),
    ("ccepcoreg-bids.z05", "https://osf.io/download/ghtb2/", 4294967296),
    ("ccepcoreg-bids.zip", "https://osf.io/download/agw23/", 2698060289),
]


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def fetch(item: tuple[str, str, int], root: Path) -> dict:
    name, url, expected = item
    target = root / name
    for attempt in range(6):
        existing = target.stat().st_size if target.exists() else 0
        if existing == expected:
            break
        request = Request(url, headers={"Range": f"bytes={existing}-"} if existing else {})
        try:
            with urlopen(request, timeout=180) as response:
                append = bool(existing and response.headers.get("Content-Range"))
                with target.open("ab" if append else "wb") as stream:
                    while True:
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        stream.write(block)
            if target.stat().st_size == expected:
                break
        except (HTTPError, URLError):
            if attempt == 5:
                raise
            time.sleep(2 ** attempt)
    if target.stat().st_size != expected:
        raise RuntimeError(f"size mismatch for {name}: {target.stat().st_size} != {expected}")
    return {"name": name, "url": url, "bytes": expected, "sha256": sha256(target)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    records = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch, item, root) for item in FILES]
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            print(f"verified {record['name']} ({record['bytes']} bytes)", flush=True)
    records.sort(key=lambda record: record["name"])
    (root / "WSGZP_DOWNLOAD_MANIFEST.json").write_text(
        json.dumps({"project": "wsgzp", "files": records}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
