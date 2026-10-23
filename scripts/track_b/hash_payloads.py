"""Record immutable payload identities without interpreting EEG values.

This is a file-integrity operation only. It reads bytes to calculate hashes,
but does not decode samples, compute features, or inspect test outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from fetch_localize import PAYLOAD, ROOT, expected_files, parse_pointer


def file_hashes(path: Path) -> tuple[int, str, str]:
    md5 = hashlib.md5()  # Compare against the dataset's published annex pointer.
    sha256 = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            size += len(chunk)
            md5.update(chunk)
            sha256.update(chunk)
    return size, md5.hexdigest(), sha256.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="+", choices=[f"{i:02d}" for i in range(1, 8)], required=True)
    args = parser.parse_args()
    if len(args.subjects) != len(set(args.subjects)):
        raise ValueError("Duplicate participant")
    rows = []
    for subject in args.subjects:
        for relative in expected_files(subject, "both"):
            expected_size, expected_md5 = parse_pointer(relative)
            target = PAYLOAD / relative
            if not target.is_file():
                raise FileNotFoundError(target)
            size, md5, sha256 = file_hashes(target)
            if size != expected_size or md5 != expected_md5:
                raise ValueError(f"Dataset pointer mismatch: {relative}")
            rows.append({"path": relative.as_posix(), "bytes": size,
                         "dataset_md5": md5, "sha256": sha256})
            print(f"verified {relative}", flush=True)
    report = {"status": "PASS", "scope": "byte integrity only; no EEG samples decoded",
              "subjects": args.subjects, "files": len(rows),
              "total_bytes": sum(row["bytes"] for row in rows), "payloads": rows}
    out = ROOT / "outputs" / "track_b" / "data_acquisition"
    out.mkdir(parents=True, exist_ok=True)
    name = "sha256_sub-" + "_".join(args.subjects) + ".json"
    destination = out / name
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite integrity inventory: {destination}")
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "files": len(rows),
                      "total_bytes": report["total_bytes"], "report": str(destination)}, indent=2))


if __name__ == "__main__":
    main()
