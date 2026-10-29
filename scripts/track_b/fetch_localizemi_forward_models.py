"""Fetch only the Localize-MI participant forward FIFs from public GIN annex URLs.

Dataset files remain outside Git. Downloads are written to a new output folder,
checked against the size and MD5 in each git-annex pointer, and hashed with
SHA-256. This script does not open EEG/SEEG signal arrays.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_DATASET_ROOT = Path(__file__).resolve().parents[2] / "data" / "Localize-MI"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "outputs" / "track_b" / "localizemi_forward_models"
GIN_ROOT = "https://gin.g-node.org/ezemikulan/Localize-MI/raw/master"
SAFETY_MARGIN_BYTES = 512 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024


@dataclass(frozen=True)
class AnnexPointer:
    relative_path: str
    size_bytes: int
    md5_hex: str


def parse_annex_pointer(path: Path, relative_path: str | None = None) -> AnnexPointer:
    """Parse a GIN symlink surrogate such as ``/annex/objects/MD5-s42--<md5>``."""
    text = path.read_text(encoding="ascii").strip()
    prefix = "/annex/objects/MD5-s"
    if not text.startswith(prefix) or "--" not in text:
        raise ValueError(f"Not a supported GIN MD5 annex pointer: {path}")
    size_part, md5_hex = text[len(prefix):].split("--", 1)
    if not size_part.isdecimal() or len(md5_hex) != 32 or any(c not in "0123456789abcdef" for c in md5_hex):
        raise ValueError(f"Malformed GIN annex key: {path}")
    return AnnexPointer(
        relative_path=relative_path or path.as_posix(),
        size_bytes=int(size_part),
        md5_hex=md5_hex,
    )


def forward_pointer_paths(dataset_root: Path, subjects: Iterable[str]) -> list[AnnexPointer]:
    """Resolve requested subject IDs to exact forward-model annex pointers."""
    pointers: list[AnnexPointer] = []
    for subject in subjects:
        if not (subject.startswith("sub-") and subject[4:].isdigit() and len(subject) == 6):
            raise ValueError(f"Invalid Localize-MI subject ID: {subject!r}")
        relative = Path("derivatives") / "sourcemodelling" / subject / "fwd" / f"{subject}_fwd.fif"
        path = dataset_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        pointers.append(parse_annex_pointer(path, relative.as_posix()))
    return pointers


def source_url(relative_path: str) -> str:
    """Return the public GIN raw URL for one annex-backed file."""
    return f"{GIN_ROOT}/{relative_path}"


def head_content_length(url: str, timeout: float = 30.0) -> int:
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"Unexpected HTTP status for HEAD {url}: {response.status}")
        raw_length = response.headers.get("Content-Length")
        if raw_length is None or not raw_length.isdecimal():
            raise ValueError(f"Missing valid Content-Length for {url}")
        return int(raw_length)


def fetch_and_verify(pointer: AnnexPointer, destination: Path, timeout: float = 120.0) -> dict[str, object]:
    """Stream one file to a new path and verify size and annex MD5 key."""
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing path: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".partial")
    if partial.exists():
        raise FileExistsError(f"Refusing to overwrite partial download: {partial}")

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    count = 0
    try:
        with urllib.request.urlopen(source_url(pointer.relative_path), timeout=timeout) as response:
            if response.status != 200:
                raise ValueError(f"Unexpected HTTP status for GET {pointer.relative_path}: {response.status}")
            with partial.open("xb") as stream:
                while block := response.read(CHUNK_BYTES):
                    stream.write(block)
                    md5.update(block)
                    sha256.update(block)
                    count += len(block)
        if count != pointer.size_bytes:
            raise ValueError(f"Downloaded size {count} != annex size {pointer.size_bytes} for {pointer.relative_path}")
        actual_md5 = md5.hexdigest()
        if actual_md5 != pointer.md5_hex:
            raise ValueError(f"Downloaded MD5 {actual_md5} != annex key {pointer.md5_hex} for {pointer.relative_path}")
        partial.replace(destination)
    except Exception:
        partial.unlink(missing_ok=True)
        raise

    return {
        "relative_path": pointer.relative_path,
        "source_url": source_url(pointer.relative_path),
        "size_bytes": count,
        "annex_md5": actual_md5,
        "sha256": sha256.hexdigest(),
        "local_path": destination.name,
        "verified": True,
    }


def dataset_revision(dataset_root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(dataset_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run(dataset_root: Path, output: Path, subjects: list[str]) -> dict[str, object]:
    dataset_root = dataset_root.resolve()
    output = output.resolve()
    if not dataset_root.is_dir():
        raise FileNotFoundError(f"Dataset root does not exist: {dataset_root}")
    if output.exists():
        raise FileExistsError(f"Output already exists; choose a new run directory: {output}")
    if output == dataset_root or dataset_root in output.parents or output in dataset_root.parents:
        raise ValueError("Output must be outside the dataset repository to preserve annex placeholders")

    pointers = forward_pointer_paths(dataset_root, subjects)
    head_sizes = {pointer.relative_path: head_content_length(source_url(pointer.relative_path)) for pointer in pointers}
    mismatches = {
        item.relative_path: {"annex_size": item.size_bytes, "server_size": head_sizes[item.relative_path]}
        for item in pointers if head_sizes[item.relative_path] != item.size_bytes
    }
    if mismatches:
        raise ValueError(f"Remote sizes disagree with annex keys: {mismatches}")

    required_bytes = sum(pointer.size_bytes for pointer in pointers) + SAFETY_MARGIN_BYTES
    free_bytes = shutil.disk_usage(output.parent).free
    if free_bytes < required_bytes:
        raise OSError(
            f"Insufficient disk space: need {required_bytes} bytes including safety margin, have {free_bytes}"
        )

    output.mkdir(parents=True, exist_ok=False)
    try:
        records = []
        for pointer in pointers:
            destination = output / Path(pointer.relative_path).name
            records.append(fetch_and_verify(pointer, destination))
        manifest = {
            "dataset": "Localize-MI",
            "dataset_version_commit": dataset_revision(dataset_root),
            "dataset_license": "CC BY-NC-SA 4.0; cite the dataset and honor noncommercial/share-alike terms",
            "acquisition_source": GIN_ROOT,
            "acquisition_scope": "participant forward FIF files only; no EEG/SEEG sample arrays downloaded or read by this script",
            "signal_arrays_accessed": False,
            "subjects": subjects,
            "records": records,
            "disk_preflight": {
                "available_before_download_bytes": free_bytes,
                "download_bytes": sum(int(record["size_bytes"]) for record in records),
                "safety_margin_bytes": SAFETY_MARGIN_BYTES,
            },
        }
        manifest_path = output / "acquisition_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return manifest
    except Exception:
        # Preserve the exact failure state and already verified files for review.
        (output / "ACQUISITION_INCOMPLETE.txt").write_text(
            "Acquisition did not finish. Inspect any verified files and retry in a new directory.\n",
            encoding="utf-8",
        )
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--subjects", nargs="+", default=[f"sub-{i:02d}" for i in range(1, 8)])
    args = parser.parse_args()
    try:
        result = run(args.dataset_root, args.output, args.subjects)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "status": "PASS_ACQUIRED_AND_HASH_VERIFIED",
        "output": str(args.output.resolve()),
        "subjects": result["subjects"],
        "download_bytes": result["disk_preflight"]["download_bytes"],
        "signal_arrays_accessed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
