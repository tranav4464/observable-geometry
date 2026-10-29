"""Screen declared WSGZP T1w electrode coordinates against MRI tissue voxels.

This is a coarse geometry triage only. It is not a scalp segmentation,
coregistration validation, forward model, or neural-signal analysis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.spatial import cKDTree

from audit_wsgzp_coregistration import resolve_subjects


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nearest_tissue_distances_mm(
    volume: np.ndarray,
    affine: np.ndarray,
    electrode_xyz_mm: np.ndarray,
    *,
    threshold: float = 10.0,
    step: int = 2,
) -> np.ndarray:
    """Approximate distances to sampled voxels above an intensity threshold.

    Coordinates are interpreted in the NIfTI world frame. Sampling every
    ``step`` voxels bounds runtime and makes these distances approximate.
    """
    if volume.ndim != 3 or not np.isfinite(affine).all() or affine.shape != (4, 4):
        raise ValueError("Expected a 3-D volume and finite 4x4 affine")
    points = np.asarray(electrode_xyz_mm, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError("Electrode coordinates must be a finite N x 3 array")
    if step < 1 or not np.isfinite(threshold):
        raise ValueError("step must be positive and threshold finite")

    sampled = np.asarray(volume[::step, ::step, ::step])
    voxels = np.argwhere(sampled > threshold).astype(np.float64) * step
    if len(voxels) == 0:
        raise ValueError("No MRI voxels exceed the requested intensity threshold")
    world = nib.affines.apply_affine(affine, voxels)
    return cKDTree(world).query(points, k=1, workers=-1)[0]


def audit_subject(root: Path, subject: str, *, threshold: float, step: int) -> dict:
    mri = root / subject / "anat" / f"{subject}_T1w.nii"
    eeg = root / "derivatives" / "epochs" / subject / "eeg"
    prefix = f"{subject}_task-ccepcoreg"
    electrodes = eeg / f"{prefix}_electrodes.tsv"
    coordsystem = eeg / f"{prefix}_coordsystem.json"
    ieeg_dir = root / "derivatives" / "epochs" / subject / "ieeg"
    ieeg_electrodes = ieeg_dir / f"{prefix}_space-T1w_electrodes.tsv"
    ieeg_coordsystem = ieeg_dir / f"{prefix}_space-T1w_coordsystem.json"
    for path in (mri, electrodes, coordsystem, ieeg_electrodes, ieeg_coordsystem):
        if not path.is_file():
            raise FileNotFoundError(path)

    contract = json.loads(coordsystem.read_text(encoding="utf-8"))
    if contract.get("EEGCoordinateSystem") != "T1w" or contract.get("EEGCoordinateUnits") != "mm":
        raise ValueError(f"Unexpected electrode coordinate contract for {subject}")
    with electrodes.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    names = [row["name"] for row in rows]
    points = np.asarray([[float(row[key]) for key in ("x", "y", "z")] for row in rows])
    if not names or len(names) != len(set(names)) or not np.isfinite(points).all():
        raise ValueError(f"Invalid electrode table for {subject}")

    ieeg_contract = json.loads(ieeg_coordsystem.read_text(encoding="utf-8"))
    if (ieeg_contract.get("iEEGCoordinateSystem") != "Other"
            or ieeg_contract.get("iEEGCoordinateUnits") != "m"
            or "Native MRI" not in ieeg_contract.get("iEEGCoordinateSystemDescription", "")):
        raise ValueError(f"Unexpected native-MRI SEEG coordinate contract for {subject}")
    with ieeg_electrodes.open(encoding="utf-8", newline="") as stream:
        ieeg_rows = list(csv.DictReader(stream, delimiter="\t"))
    ieeg_names = [row["name"] for row in ieeg_rows]
    ieeg_points_mm = np.asarray(
        [[float(row[key]) for key in ("x", "y", "z")] for row in ieeg_rows],
        dtype=np.float64,
    ) * 1000.0
    if not ieeg_names or len(ieeg_names) != len(set(ieeg_names)) or not np.isfinite(ieeg_points_mm).all():
        raise ValueError(f"Invalid native-MRI SEEG coordinate table for {subject}")

    image = nib.load(str(mri))
    spatial_units = image.header.get_xyzt_units()[0]
    if spatial_units != "mm":
        raise ValueError(f"Expected NIfTI spatial units in mm for {subject}, got {spatial_units!r}")
    volume = np.asarray(image.dataobj)
    affine = np.asarray(image.affine, dtype=np.float64)
    distances = nearest_tissue_distances_mm(
        volume, affine, points,
        threshold=threshold, step=step,
    )
    ieeg_distances = nearest_tissue_distances_mm(
        volume, affine, ieeg_points_mm,
        threshold=threshold, step=step,
    )
    quantiles = (0, 0.1, 0.5, 0.9, 0.95, 1)

    def summarize(values: np.ndarray) -> dict:
        return {str(q): float(v) for q, v in zip(quantiles, np.quantile(values, quantiles))}

    return {
        "subject": subject,
        "n_electrodes": len(names),
        "threshold_intensity": threshold,
        "voxel_sampling_step": step,
        "nifti_spatial_units": spatial_units,
        "distances_are_approximate": True,
        "distance_quantiles_mm": summarize(distances),
        "electrodes": {
            name: {"xyz_t1w_mm": point.tolist(), "nearest_thresholded_tissue_mm": float(distance)}
            for name, point, distance in zip(names, points, distances)
        },
        "seeg_positive_control": {
            "n_contacts": len(ieeg_names),
            "coordinate_system": "native T1w MRI space, metres converted to millimetres",
            "distance_quantiles_mm": summarize(ieeg_distances),
            "contacts": {
                name: {"xyz_t1w_mm": point.tolist(), "nearest_thresholded_tissue_mm": float(distance)}
                for name, point, distance in zip(ieeg_names, ieeg_points_mm, ieeg_distances)
            },
        },
        "input_sha256": {
            "mri": sha256(mri), "electrodes": sha256(electrodes), "coordsystem": sha256(coordsystem),
            "seeg_electrodes": sha256(ieeg_electrodes), "seeg_coordsystem": sha256(ieeg_coordsystem),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--subjects", nargs="*", default=None)
    parser.add_argument("--threshold", type=float, default=10.0)
    parser.add_argument("--step", type=int, default=2)
    args = parser.parse_args()
    root = args.dataset_root.resolve()
    try:
        subjects = resolve_subjects(root, args.subjects)
    except ValueError as exc:
        parser.error(str(exc))

    reports, failures = [], []
    for subject in subjects:
        try:
            reports.append(audit_subject(root, subject, threshold=args.threshold, step=args.step))
        except Exception as exc:
            failures.append({"subject": subject, "error": f"{type(exc).__name__}: {exc}"})
    result = {
        "audit_id": "WSGZP-ELECTRODE-MRI-PROXIMITY-2026-10-28-v2",
        "dataset_root": str(root),
        "status": "SCREEN_ONLY_REVIEW_REQUIRED",
        "signal_samples_read": False,
        "subject_count_requested": len(subjects),
        "subject_count_audited": len(reports),
        "subject_count_failed": len(failures),
        "limitations": [
            "The T1w coordinate interpretation is assumed, not independently recovered from the absent source digitizer files.",
            "A global intensity threshold is not a scalp segmentation; distances are approximate and do not establish coregistration.",
            "This screen cannot replace reviewed MRI/electrode overlays or validate a forward model.",
            "Native-MRI SEEG contacts serve only as a positive control for the MRI coordinate interpretation; they are not evidence that scalp EEG coordinates are correct.",
            "No EEG/iEEG sample arrays are accessed.",
        ],
        "subjects": reports,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "subjects"}, indent=2))


if __name__ == "__main__":
    main()
