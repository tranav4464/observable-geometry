"""Audit downloaded Localize-MI forward models without opening neural recordings.

The audit checks annex-manifest hashes, MNE forward-file structure, finite
leadfield values, common channel ordering, source-grid dimensions, and
consistency between each forward solution's MRI-to-head transform and the
inverse of the accompanying head-to-surface HDF5 transform. It does not
validate anatomical registration accuracy or physiological source recovery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import h5py
import mne
import numpy as np
from mne.io.constants import FIFF


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_annex_key(text: str) -> tuple[int, str]:
    """Read size and MD5 from a GIN git-annex pointer surrogate."""
    match = re.fullmatch(r"/annex/objects/MD5-s(\d+)--([0-9a-f]{32})", text.strip())
    if match is None:
        raise ValueError("Malformed or unsupported GIN MD5 annex pointer")
    return int(match.group(1)), match.group(2)


def inverse_transform_error(mri_to_head: np.ndarray, head_to_surface: np.ndarray) -> float:
    """Return max absolute disagreement with the inverse homogeneous transform."""
    mri_to_head = np.asarray(mri_to_head, dtype=np.float64)
    head_to_surface = np.asarray(head_to_surface, dtype=np.float64)
    if mri_to_head.shape != (4, 4) or head_to_surface.shape != (4, 4):
        raise ValueError("Both transforms must be 4x4 homogeneous matrices")
    if not np.isfinite(mri_to_head).all() or not np.isfinite(head_to_surface).all():
        raise ValueError("Transforms must contain only finite values")
    if not np.allclose(mri_to_head[3], [0, 0, 0, 1], atol=1e-12, rtol=0):
        raise ValueError("MRI-to-head transform has an invalid homogeneous row")
    if not np.allclose(head_to_surface[3], [0, 0, 0, 1], atol=1e-12, rtol=0):
        raise ValueError("Head-to-surface transform has an invalid homogeneous row")
    for name, matrix in (("MRI-to-head", mri_to_head), ("head-to-surface", head_to_surface)):
        rotation = matrix[:3, :3]
        if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-6, rtol=0):
            raise ValueError(f"{name} transform rotation is not orthonormal")
        if not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-6, rtol=0):
            raise ValueError(f"{name} transform rotation is not proper (determinant must be +1)")
    try:
        inverse = np.linalg.inv(head_to_surface)
    except np.linalg.LinAlgError as exc:
        raise ValueError("Head-to-surface transform is singular") from exc
    return float(np.max(np.abs(inverse - mri_to_head)))


def audit(bundle: Path, sourcemodelling: Path, metadata_root: Path) -> dict[str, Any]:
    manifest_path = bundle / "acquisition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    expected = {f"sub-{i:02d}" for i in range(1, 8)}
    by_subject = {Path(row["local_path"]).name[:6]: row for row in records}
    if set(by_subject) != expected:
        raise ValueError(f"Expected seven subject records, got {sorted(by_subject)}")

    rows: list[dict[str, Any]] = []
    common_names: list[str] | None = None
    all_pass = True
    for subject in sorted(expected):
        record = by_subject[subject]
        fwd_path = bundle / record["local_path"]
        transform_path = sourcemodelling / subject / "xfm" / f"{subject}_from-head_to-surface.h5"
        pointer_path = metadata_root / "derivatives" / "sourcemodelling" / subject / "fwd" / f"{subject}_fwd.fif"
        failures: list[str] = []
        actual_size = fwd_path.stat().st_size
        actual_sha = sha256_file(fwd_path)
        pointer_size, pointer_md5 = parse_annex_key(pointer_path.read_text(encoding="ascii"))
        actual_md5 = md5_file(fwd_path)
        if actual_size != record["size_bytes"]:
            failures.append("file_size_mismatch")
        if actual_size != pointer_size:
            failures.append("annex_pointer_size_mismatch")
        if actual_sha != record["sha256"]:
            failures.append("sha256_mismatch")
        if actual_md5 != pointer_md5 or record.get("annex_md5") != pointer_md5:
            failures.append("annex_md5_mismatch")
        if not record.get("verified", False):
            failures.append("acquisition_manifest_not_verified")

        fwd = mne.read_forward_solution(fwd_path, verbose="ERROR")
        leadfield = fwd["sol"]["data"]
        channel_names = list(fwd["sol"]["row_names"])
        source_spaces = fwd["src"]
        n_sources = int(sum(space["nuse"] for space in source_spaces))
        all_eeg = all(mne.channel_type(fwd["info"], index) == "eeg" for index in range(len(channel_names)))
        sensor_locations = np.asarray([channel["loc"][:3] for channel in fwd["info"]["chs"]], dtype=np.float64)
        source_locations = np.vstack([space["rr"][space["vertno"]] for space in source_spaces])
        if leadfield.shape[0] != len(channel_names):
            failures.append("leadfield_row_count_does_not_match_channels")
        if fwd["info"]["ch_names"] != channel_names:
            failures.append("forward_row_names_do_not_match_info_order")
        if not np.isfinite(sensor_locations).all():
            failures.append("nonfinite_sensor_coordinates")
        if not np.isfinite(source_locations).all():
            failures.append("nonfinite_source_coordinates")
        if int(fwd["source_ori"]) != FIFF.FIFFV_MNE_FREE_ORI:
            failures.append("unexpected_source_orientation")
        if int(fwd["source_ori"]) == FIFF.FIFFV_MNE_FREE_ORI and leadfield.shape[1] != 3 * n_sources:
            failures.append("free_orientation_column_count_does_not_match_source_grid")
        if not all_eeg:
            failures.append("non_eeg_channel_in_forward_solution")
        if not np.isfinite(leadfield).all():
            failures.append("nonfinite_leadfield")
        if len(channel_names) != len(set(channel_names)):
            failures.append("duplicate_channel_names")
        if common_names is None:
            common_names = channel_names
        elif channel_names != common_names:
            failures.append("channel_order_differs_from_sub-01")

        with h5py.File(transform_path, "r") as h5:
            head_to_surface = np.asarray(h5["trans"], dtype=np.float64)
        mri_to_head = np.asarray(fwd["mri_head_t"]["trans"], dtype=np.float64)
        transform_error = inverse_transform_error(mri_to_head, head_to_surface)
        if transform_error > 1e-6:
            failures.append("forward_transform_does_not_match_h5_inverse")
        source_frames = sorted({int(space["coord_frame"]) for space in source_spaces})
        row = {
            "subject": subject,
            "file_size_bytes": actual_size,
            "sha256": actual_sha,
            "annex_md5": actual_md5,
            "channels": len(channel_names),
            "all_channels_are_eeg": all_eeg,
            "sensor_coordinates_all_finite": bool(np.isfinite(sensor_locations).all()),
            "source_coordinates_all_finite": bool(np.isfinite(source_locations).all()),
            "source_locations": n_sources,
            "leadfield_shape": [int(v) for v in leadfield.shape],
            "source_orientation": int(fwd["source_ori"]),
            "forward_coordinate_frame": int(fwd["coord_frame"]),
            "source_coordinate_frames": source_frames,
            "leadfield_all_finite": bool(np.isfinite(leadfield).all()),
            "mri_head_vs_inverse_h5_max_abs_error": transform_error,
            "status": "PASS" if not failures else "FAIL",
            "failures": failures,
        }
        rows.append(row)
        all_pass &= not failures

    return {
        "audit": "Localize-MI forward-model bundle structural and transform-consistency audit",
        "dataset_commit": manifest.get("dataset_version_commit"),
        "scope": "forward-model and transform metadata only; neural recording arrays were not accessed",
        "passed": all_pass,
        "subjects": rows,
        "cross_subject_channel_order_identical": all(
            row["status"] != "FAIL" or "channel_order_differs_from_sub-01" not in row["failures"]
            for row in rows
        ),
        "interpretation_limit": (
            "Passing establishes file integrity, internal model structure, and transform consistency only. "
            "It does not independently validate anatomical registration accuracy, measured-source recovery, "
            "or generalization."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Downloaded forward-model bundle")
    parser.add_argument("--sourcemodelling", type=Path, required=True, help="Localize-MI sourcemodelling derivative root")
    parser.add_argument("--metadata-root", type=Path, required=True, help="Dataset metadata root containing annex pointers")
    parser.add_argument("--output", type=Path, required=True, help="New JSON output path; existing files are never overwritten")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Refusing to overwrite existing output: {args.output}")
    result = audit(args.bundle, args.sourcemodelling, args.metadata_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS" if result["passed"] else "FAIL")
    print(f"subjects={len(result['subjects'])}; output={args.output}")
    for row in result["subjects"]:
        print(f"{row['subject']}: {row['status']} channels={row['channels']} sources={row['source_locations']} transform_error={row['mri_head_vs_inverse_h5_max_abs_error']:.3g}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
