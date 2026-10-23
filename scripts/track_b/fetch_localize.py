"""Plan or fetch selected Localize-MI numerical payloads without reading outcomes.

The metadata checkout supplies Git-annex MD5/size pointers. Payloads are saved
outside that checkout, validated before atomic replacement, and never redistributed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "data" / "Localize-MI"
PAYLOAD = ROOT / "data" / "payload"
POINTER = re.compile(r"^/annex/objects/MD5-s(?P<size>\d+)--(?P<md5>[0-9a-f]{32})$")


def expected_files(subject: str, kind: str) -> list[Path]:
    base = Path("derivatives")
    forward = base / "sourcemodelling" / f"sub-{subject}" / "fwd" / f"sub-{subject}_fwd.fif"
    scans = META / base / "epochs" / f"sub-{subject}" / f"sub-{subject}_scans.tsv"
    epochs = []
    if kind in {"epochs", "both"}:
        lines = scans.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "filename":
            raise ValueError(f"Unexpected scans table: {scans}")
        for line in lines[1:]:
            item = Path(line)
            if item.is_absolute() or ".." in item.parts or item.suffix != ".npy":
                raise ValueError(f"Unsafe epoch path in {scans}: {line}")
            epochs.append(base / "epochs" / f"sub-{subject}" / item)
    return ([forward] if kind in {"forward", "both"} else []) + epochs


def parse_pointer(relative: Path) -> tuple[int, str]:
    match = POINTER.fullmatch((META / relative).read_text(encoding="utf-8").strip())
    if not match:
        raise ValueError(f"Not a recognized MD5 annex pointer: {relative}")
    return int(match["size"]), match["md5"]


def digest_file(path: Path) -> str:
    digest = hashlib.md5()  # Dataset-provided integrity hash, not a security signature.
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(relative: Path, expected_size: int, expected_md5: str) -> dict:
    destination = PAYLOAD / relative
    url = "https://gin.g-node.org/ezemikulan/Localize-MI/raw/master/" + relative.as_posix()
    if destination.is_file():
        if destination.stat().st_size != expected_size or digest_file(destination) != expected_md5:
            raise ValueError(f"Existing payload has wrong size/hash; refusing overwrite: {destination}")
        return {"path": relative.as_posix(), "bytes": expected_size, "md5": expected_md5, "status": "verified-existing"}
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".partial")
    if temporary.exists():
        temporary.unlink()  # No verified HTTP resume support; restart this one file.
    received = 0
    digest = hashlib.md5()
    try:
        with urllib.request.urlopen(url, timeout=90) as response, temporary.open("xb") as output:
            if response.status != 200:
                raise ValueError(f"Unexpected HTTP {response.status}: {url}")
            while chunk := response.read(1024 * 1024):
                received += len(chunk)
                if received > expected_size:
                    raise ValueError(f"Download exceeded pointer size: {relative}")
                digest.update(chunk)
                output.write(chunk)
        if received != expected_size or digest.hexdigest() != expected_md5:
            raise ValueError(f"Pointer size/hash mismatch: {relative}, got {received} bytes")
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"path": relative.as_posix(), "bytes": expected_size, "md5": expected_md5, "status": "downloaded", "url": url}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="+", choices=[f"{i:02d}" for i in range(1, 8)], required=True)
    parser.add_argument("--kind", choices=["forward", "epochs", "both"], default="both")
    parser.add_argument("--fetch", action="store_true", help="download and verify; omission only prints the plan")
    args = parser.parse_args()
    paths = [path for subject in args.subjects for path in expected_files(subject, args.kind)]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate requested payload path")
    rows = []
    for path in paths:
        size, md5 = parse_pointer(path)
        row = fetch(path, size, md5) if args.fetch else {
            "path": path.as_posix(), "bytes": size, "md5": md5,
            "status": "present" if (PAYLOAD / path).is_file() else "missing",
        }
        rows.append(row)
        print(json.dumps(row), flush=True)
    summary = {"subjects": args.subjects, "kind": args.kind, "files": len(rows),
               "total_bytes": sum(row["bytes"] for row in rows), "fetched": args.fetch}
    print(json.dumps(summary), flush=True)
    if args.fetch:
        out = ROOT / "outputs" / "track_b" / "data_acquisition"
        out.mkdir(parents=True, exist_ok=True)
        name = "sub-" + "_".join(args.subjects) + "_" + args.kind + ".json"
        (out / name).write_text(json.dumps({"summary": summary, "files": rows}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
