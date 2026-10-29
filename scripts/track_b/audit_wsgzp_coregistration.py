"""Audit WSGZP MRI-space scalp coordinates using supplied fiducials.

Reads anatomical image headers and coordinate metadata only. It does not open
EEG/iEEG sample arrays and does not build or validate an EEG forward model.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from mne.transforms import apply_trans, get_ras_to_neuromag_trans
import nibabel as nib
import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_tsv_xyz(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    names = [row["name"] for row in rows]
    xyz = np.asarray([[float(row[k]) for k in ("x", "y", "z")] for row in rows], dtype=np.float64)
    if not names or len(names) != len(set(names)) or xyz.shape != (len(names), 3):
        raise ValueError(f"Invalid or duplicate coordinate rows: {path}")
    if not np.isfinite(xyz).all():
        raise ValueError(f"Nonfinite coordinate in {path}")
    return names, xyz


def make_t1w_to_head(fiducials_mm: dict[str, list[float]]) -> np.ndarray:
    """Return MNE RAS-to-head transform from MRI-space NAS/LPA/RPA in mm."""
    required = {"NAS", "LPA", "RPA"}
    if not required.issubset(fiducials_mm):
        raise ValueError(f"Missing fiducials: {sorted(required - set(fiducials_mm))}")
    nas, lpa, rpa = (np.asarray(fiducials_mm[k], dtype=np.float64) / 1000.0
                     for k in ("NAS", "LPA", "RPA"))
    if any(p.shape != (3,) or not np.isfinite(p).all() for p in (nas, lpa, rpa)):
        raise ValueError("Fiducials must be finite 3-vectors in millimetres")
    if np.linalg.norm(rpa - lpa) < 0.04 or np.linalg.norm(nas - (lpa + rpa) / 2) < 0.04:
        raise ValueError("Fiducials are degenerate or implausibly close")
    return get_ras_to_neuromag_trans(nas, lpa, rpa)


def audit_subject(root: Path, subject: str) -> dict:
    subject_dir = root / subject
    eeg_dir = root / "derivatives" / "epochs" / subject / "eeg"
    eeg_prefix = f"{subject}_task-ccepcoreg"
    mri_path = subject_dir / "anat" / f"{subject}_T1w.nii"
    coord_path = eeg_dir / f"{eeg_prefix}_coordsystem.json"
    electrode_path = eeg_dir / f"{eeg_prefix}_electrodes.tsv"
    for path in (mri_path, coord_path, electrode_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    coords = json.loads(coord_path.read_text(encoding="utf-8"))
    if coords.get("EEGCoordinateSystem") != "T1w" or coords.get("EEGCoordinateUnits") != "mm":
        raise ValueError(f"Unexpected scalp coordinate contract for {subject}")
    if coords.get("AnatomicalLandmarkCoordinateSystem") != "T1w" or coords.get("AnatomicalLandmarkCoordinateUnits") != "mm":
        raise ValueError(f"Unexpected fiducial coordinate contract for {subject}")
    fid = coords.get("AnatomicalLandmarkCoordinates", {})
    transform = make_t1w_to_head(fid)
    names, eeg_mm = load_tsv_xyz(electrode_path)
    eeg_head_m = apply_trans(transform, eeg_mm / 1000.0)
    fid_order = ("NAS", "LPA", "RPA")
    fid_head_m = apply_trans(
        transform, np.asarray([fid[k] for k in fid_order], dtype=np.float64) / 1000.0
    )

    image = nib.load(str(mri_path))
    spatial_units = image.header.get_xyzt_units()[0]
    if spatial_units != "mm":
        raise ValueError(f"Expected NIfTI spatial units in mm for {subject}, got {spatial_units!r}")
    affine = np.asarray(image.affine, dtype=np.float64)
    if affine.shape != (4, 4) or not np.isfinite(affine).all() or abs(np.linalg.det(affine[:3, :3])) < 1e-12:
        raise ValueError(f"Invalid NIfTI affine for {subject}")
    # This is a consistency check under the interpretation that the sidecar's
    # T1w coordinates are the NIfTI's scanner-RAS world coordinates.
    fid_voxel = nib.affines.apply_affine(np.linalg.inv(affine), np.asarray([fid[k] for k in fid_order]))
    shape = np.asarray(image.shape[:3], dtype=np.float64)
    fiducials_inside_image = bool(np.all((fid_voxel >= -0.5) & (fid_voxel <= shape - 0.5)))

    # MNE's transform should put the defined fiducials on the expected axes.
    fid_zero_axis_error_m = float(np.max(np.abs(np.asarray([
        fid_head_m[0, 0], fid_head_m[0, 2],
        fid_head_m[1, 1], fid_head_m[1, 2],
        fid_head_m[2, 1], fid_head_m[2, 2],
    ]))))
    fiducial_axis_order_valid = bool(
        fid_head_m[0, 1] > 0 and fid_head_m[1, 0] < 0 and fid_head_m[2, 0] > 0
    )
    fid_axis_error_m = fid_zero_axis_error_m if fiducial_axis_order_valid else float("inf")
    return {
        "subject": subject,
        # The BIDS sidecar and acquisition paper support MRI-coregistered
        # coordinates, but the source .hpts file and transform are absent. A
        # fiducial-derived transform does not replace overlay review.
        "status": "REVIEW_REQUIRED_VISUAL_OVERLAY",
        "fiducial_transform_check": "CONSTRUCTION_CHECK_ONLY_NOT_INDEPENDENT_VALIDATION",
        "coordinate_interpretation": "T1w millimetres interpreted as NIfTI scanner-RAS world coordinates; requires visual overlay before forward modeling",
        "n_eeg_electrodes": len(names),
        "nifti_spatial_units": spatial_units,
        "fiducials_inside_nifti_volume": fiducials_inside_image,
        "fiducial_voxel_coordinates": fid_voxel.tolist(),
        "fiducial_head_coordinates_m": fid_head_m.tolist(),
        "fiducial_head_axis_max_error_m": fid_axis_error_m,
        "eeg_head_coordinates_m": {name: point.tolist() for name, point in zip(names, eeg_head_m)},
        "eeg_head_radius_range_m": [float(np.min(np.linalg.norm(eeg_head_m, axis=1))),
                                    float(np.max(np.linalg.norm(eeg_head_m, axis=1)))],
        "t1w_to_head_transform": transform.tolist(),
        "input_sha256": {"mri": sha256(mri_path), "coordsystem": sha256(coord_path),
                         "electrodes": sha256(electrode_path)},
        "limitations": [
            "The source .hpts digitization file and exact export transform are not included, so the declared MRI registration cannot be replayed.",
            "The fiducial axes are imposed by constructing the transform from those same fiducials; this is not independent validation.",
            "Fiducials inside the NIfTI bounding box do not establish scalp/MRI coregistration; a visual electrode-to-MRI overlay remains required.",
            "This does not construct scalp/skull/brain surfaces, a source space, covariance, or a forward model.",
            "No EEG or iEEG sample values are read.",
        ],
    }


def resolve_subjects(root: Path, requested: list[str] | None = None) -> list[str]:
    """Validate the root and resolve a non-empty participant list.

    A misspelled dataset path must never produce a successful-looking
    zero-participant audit.
    """
    if not root.is_dir():
        raise ValueError(f"Dataset root does not exist or is not a directory: {root}")
    subjects = requested if requested else sorted(
        p.name for p in root.glob("sub-*") if p.is_dir()
    )
    if not subjects:
        raise ValueError(f"No sub-* participant directories found in dataset root: {root}")
    missing = [name for name in subjects if not (root / name).is_dir()]
    if missing:
        raise ValueError(f"Requested participant directories are missing: {missing}")
    return subjects


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--subjects", nargs="*", default=None)
    args = parser.parse_args()
    root = args.dataset_root.resolve()
    try:
        subjects = resolve_subjects(root, args.subjects)
    except ValueError as exc:
        parser.error(str(exc))
    reports = []
    failures = []
    for subject in subjects:
        try:
            reports.append(audit_subject(root, subject))
        except Exception as exc:  # Keep a per-participant failure ledger.
            failures.append({"subject": subject, "error": f"{type(exc).__name__}: {exc}"})
    result = {
        "audit_id": "WSGZP-COORD-OVERLAY-REVIEW-2026-10-28-v3",
        "dataset_root": str(root),
        "coordinate_data_only": True,
        "subject_count_requested": len(subjects),
        "subject_count_audited": len(reports),
        "subject_count_failed": len(failures),
        "status": "REVIEW_REQUIRED_VISUAL_COREGISTRATION",
        "subjects": reports,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "subjects"}, indent=2))


if __name__ == "__main__":
    main()
