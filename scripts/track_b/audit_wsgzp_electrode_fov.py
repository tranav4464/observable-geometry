"""Audit whether declared WSGZP scalp coordinates fall inside each T1w FOV.

This checks coordinate/image coverage only. It does not validate
coregistration and never reads EEG/iEEG sample arrays.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np

from audit_wsgzp_coregistration import resolve_subjects


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_subject(root: Path, subject: str) -> dict:
    mri = root / subject / "anat" / f"{subject}_T1w.nii"
    electrodes = root / "derivatives" / "epochs" / subject / "eeg" / f"{subject}_task-ccepcoreg_electrodes.tsv"
    coordsystem = root / "derivatives" / "epochs" / subject / "eeg" / f"{subject}_task-ccepcoreg_coordsystem.json"
    for path in (mri, electrodes, coordsystem):
        if not path.is_file():
            raise FileNotFoundError(path)
    contract = json.loads(coordsystem.read_text(encoding="utf-8"))
    if contract.get("EEGCoordinateSystem") != "T1w" or contract.get("EEGCoordinateUnits") != "mm":
        raise ValueError(f"Unexpected scalp coordinate contract for {subject}")
    with electrodes.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    names = [row["name"] for row in rows]
    points = np.asarray([[float(row[k]) for k in ("x", "y", "z")] for row in rows], dtype=np.float64)
    if not names or len(names) != len(set(names)) or not np.isfinite(points).all():
        raise ValueError(f"Invalid electrode coordinates for {subject}")

    image = nib.load(str(mri))
    if len(image.shape) != 3 or image.header.get_xyzt_units()[0] != "mm":
        raise ValueError(f"Expected 3-D MRI with mm units for {subject}")
    affine = np.asarray(image.affine, dtype=np.float64)
    if not np.isfinite(affine).all() or abs(np.linalg.det(affine[:3, :3])) < 1e-12:
        raise ValueError(f"Invalid MRI affine for {subject}")

    voxel = nib.affines.apply_affine(np.linalg.inv(affine), points)
    upper = np.asarray(image.shape, dtype=np.float64) - 0.5
    lower = np.full(3, -0.5)
    inside = np.all((voxel >= lower) & (voxel <= upper), axis=1)
    nearest = np.clip(voxel, lower, upper)
    # NIfTI voxel axes are orthogonal in the released MRIs; check before using
    # coordinate clipping as the closest point on the image parallelepiped.
    basis = affine[:3, :3]
    gram = basis.T @ basis
    off_diagonal = gram - np.diag(np.diag(gram))
    if np.max(np.abs(off_diagonal)) > 1e-6:
        raise ValueError(f"Non-orthogonal voxel axes require a constrained projection for {subject}")
    nearest_world = nib.affines.apply_affine(affine, nearest)
    distance_mm = np.linalg.norm(points - nearest_world, axis=1)

    return {
        "subject": subject,
        "n_electrodes": len(names),
        "inside_fov_count": int(inside.sum()),
        "outside_fov_count": int((~inside).sum()),
        "outside_fov_fraction": float((~inside).mean()),
        "max_distance_to_fov_mm": float(distance_mm.max()),
        "mri_shape_voxels": list(image.shape),
        "electrodes": {
            name: {
                "t1w_mm": point.tolist(),
                "voxel_coordinates": voxel_point.tolist(),
                "inside_fov": bool(is_inside),
                "distance_to_fov_mm": float(distance),
            }
            for name, point, voxel_point, is_inside, distance in zip(names, points, voxel, inside, distance_mm)
        },
        "input_sha256": {
            "mri": sha256(mri),
            "electrodes": sha256(electrodes),
            "coordsystem": sha256(coordsystem),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--subjects", nargs="+")
    args = parser.parse_args()
    subjects = resolve_subjects(args.dataset_root, args.subjects)
    reports = [audit_subject(args.dataset_root, subject) for subject in subjects]
    result = {
        "audit_id": "WSGZP-ELECTRODE-MRI-FOV-2026-10-28-v1",
        "status": "COVERAGE_SCREEN_ONLY",
        "signal_samples_read": False,
        "coordinate_world_assumption": "Declared T1w millimetres interpreted as NIfTI scanner-RAS world millimetres; this convention is not independently proven by the release.",
        "dataset_root": str(args.dataset_root.resolve()),
        "subject_count": len(reports),
        "interpretation": [
            "The calculation assumes declared T1w coordinates are expressed in the NIfTI scanner-RAS world frame; the release provenance does not independently prove this.",
            "Outside the NIfTI FOV means the coordinate lies beyond the image bounds; it does not by itself imply a bad transform.",
            "A scalp sensor may legitimately be outside a tightly cropped MRI field of view.",
            "Inside the FOV does not establish scalp-surface alignment or registration accuracy.",
            "No EEG or iEEG sample arrays are accessed.",
        ],
        "subjects": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
