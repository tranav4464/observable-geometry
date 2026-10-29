"""Audit whether released WSGZP scalp coordinates are compatible with MRI space.

This metadata/image-geometry check reads only EEG electrode TSVs, their
coordinate sidecars, participant T1w MRI files, and root BIDS metadata. It does
not open EEG/iEEG recording arrays, fit a registration transform, or alter the
dataset. Distance to nonzero MRI voxels is only a coarse compatibility check,
not scalp-surface segmentation or registration QC.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def points_to_voxel(points_mm: np.ndarray, voxel_to_world: np.ndarray) -> np.ndarray:
    """Map points in a hypothesized world frame to continuous voxel indices."""
    points = np.asarray(points_mm, dtype=np.float64)
    affine = np.asarray(voxel_to_world, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError("points_mm must be a finite n-by-3 array")
    if affine.shape != (4, 4) or not np.isfinite(affine).all():
        raise ValueError("voxel_to_world must be a finite 4-by-4 affine")
    if abs(float(np.linalg.det(affine[:3, :3]))) < 1e-12:
        raise ValueError("voxel_to_world affine is singular")
    homogeneous = np.column_stack((points, np.ones(len(points))))
    return (homogeneous @ np.linalg.inv(affine).T)[:, :3]


def summarize_voxel_locations(
    voxel_points: np.ndarray,
    image_shape: tuple[int, int, int],
    distance_to_nonzero_mm: np.ndarray,
) -> dict[str, object]:
    """Summarize frame compatibility without clipping out-of-volume points."""
    points = np.asarray(voxel_points, dtype=np.float64)
    shape = np.asarray(image_shape, dtype=np.int64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("voxel_points must be an n-by-3 array")
    if shape.shape != (3,) or np.any(shape <= 0):
        raise ValueError("image_shape must contain three positive dimensions")
    if distance_to_nonzero_mm.shape != tuple(shape):
        raise ValueError("distance map shape must match image_shape")
    # The NIfTI field of view is the union of voxel cells, not only the voxel
    # centres. Use half-open bounds so points within half a voxel of the first
    # or last centre are not spuriously counted outside.
    inside = np.all((points >= -0.5) & (points < (shape - 0.5)), axis=1)
    inside_indices = np.floor(points[inside] + 0.5).astype(np.int64)
    if len(inside_indices):
        distances = distance_to_nonzero_mm[
            inside_indices[:, 0], inside_indices[:, 1], inside_indices[:, 2]
        ]
    else:
        distances = np.empty(0, dtype=np.float64)
    quantiles = (
        np.quantile(distances, [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]).tolist()
        if len(distances) else None
    )
    return {
        "point_count": int(len(points)),
        "inside_image_count": int(inside.sum()),
        "outside_image_count": int((~inside).sum()),
        "nearest_nonzero_mri_voxel_distance_mm_quantiles": quantiles,
        "inside_points_within_5mm_of_nonzero_mri_voxel": (
            int((distances <= 5.0).sum()) if len(distances) else None
        ),
        "inside_points_within_10mm_of_nonzero_mri_voxel": (
            int((distances <= 10.0).sum()) if len(distances) else None
        ),
    }


def _read_electrode_points(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    names: list[str] = []
    points: list[list[float]] = []
    for row in rows:
        names.append(row["name"])
        points.append([float(row[axis]) for axis in ("x", "y", "z")])
    values = np.asarray(points, dtype=np.float64)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError(f"electrode table has no finite XYZ rows: {path}")
    return names, values


def validate_t1w_mm_contract(sidecar: dict[str, object]) -> None:
    """Require the declared coordinate contract this targeted audit tests."""
    expected = {
        "EEGCoordinateSystem": "T1w",
        "EEGCoordinateUnits": "mm",
        "AnatomicalLandmarkCoordinateSystem": "T1w",
        "AnatomicalLandmarkCoordinateUnits": "mm",
    }
    mismatches = [
        f"{key}={sidecar.get(key)!r} (expected {value!r})"
        for key, value in expected.items()
        if sidecar.get(key) != value
    ]
    if mismatches:
        raise ValueError("unexpected WSGZP coordinate contract: " + "; ".join(mismatches))


def audit_participant(dataset_root: Path, participant: str) -> dict[str, object]:
    # Imported only when the audit is run; the package itself does not depend
    # on neuroimaging libraries.
    import nibabel as nib
    from scipy.ndimage import distance_transform_edt

    eeg_dir = dataset_root / "derivatives" / "epochs" / participant / "eeg"
    prefix = f"{participant}_task-ccepcoreg"
    coordinates_path = eeg_dir / f"{prefix}_electrodes.tsv"
    sidecar_path = eeg_dir / f"{prefix}_coordsystem.json"
    mri_path = dataset_root / participant / "anat" / f"{participant}_T1w.nii"
    required = (coordinates_path, sidecar_path, mri_path)
    absent = [str(path) for path in required if not path.is_file()]
    if absent:
        raise FileNotFoundError("missing participant geometry file(s): " + ", ".join(absent))

    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    validate_t1w_mm_contract(sidecar)
    image = nib.load(str(mri_path))
    if len(image.shape) != 3:
        raise ValueError(f"expected a three-dimensional T1w MRI, got {image.shape}: {mri_path}")
    qform_code = int(image.header["qform_code"])
    if qform_code == 0:
        raise ValueError(f"MRI qform code is unset: {mri_path}")
    affine = image.get_qform(coded=False)
    spatial_units = image.header.get_xyzt_units()[0]
    if spatial_units != "mm":
        raise ValueError(f"expected MRI spatial units in mm, got {spatial_units!r}: {mri_path}")

    # Image data are MRI voxels, not neural recordings. Thresholding at >0
    # is deliberately only a crude non-background occupancy proxy.
    mri_data = np.asarray(image.dataobj)
    occupied = mri_data > 0
    voxel_sizes = np.linalg.norm(np.asarray(affine)[:3, :3], axis=0)
    distance_map = distance_transform_edt(~occupied, sampling=voxel_sizes)

    electrode_names, electrode_points = _read_electrode_points(coordinates_path)
    electrode_voxels = points_to_voxel(electrode_points, affine)
    electrode_summary = summarize_voxel_locations(
        electrode_voxels, tuple(int(v) for v in image.shape[:3]), distance_map
    )

    fiducials = sidecar.get("AnatomicalLandmarkCoordinates", {})
    fiducial_names = [name for name in ("LPA", "NAS", "RPA") if name in fiducials]
    fiducial_points = np.asarray([fiducials[name] for name in fiducial_names], dtype=np.float64)
    if len(fiducial_points):
        fiducial_voxels = points_to_voxel(fiducial_points, affine)
        fiducial_summary = summarize_voxel_locations(
            fiducial_voxels, tuple(int(v) for v in image.shape[:3]), distance_map
        )
    else:
        fiducial_summary = {"point_count": 0, "status": "NO_STANDARD_FIDUCIALS"}

    lpa, nas, rpa = (fiducials.get(name) for name in ("LPA", "NAS", "RPA"))
    orientation_checks = {
        "left_right_landmark_order_x": bool(lpa is not None and rpa is not None and lpa[0] < rpa[0]),
        "nasion_anterior_to_preauricular_mean_y": bool(
            nas is not None and lpa is not None and rpa is not None
            and nas[1] > (lpa[1] + rpa[1]) / 2
        ),
    }

    return {
        "participant": participant,
        "coordinate_hypothesis": {
            "declared_eeg_coordinate_system": sidecar.get("EEGCoordinateSystem"),
            "declared_eeg_units": sidecar.get("EEGCoordinateUnits"),
            "declared_landmark_coordinate_system": sidecar.get("AnatomicalLandmarkCoordinateSystem"),
            "hypothesis_tested": "electrode and fiducial XYZ values are millimetres in the MRI qform world frame",
            "this_is_a_test_hypothesis_not_a_verified_transform": True,
        },
        "mri": {
            "file": mri_path.name,
            "sha256": sha256(mri_path),
            "shape": [int(v) for v in image.shape[:3]],
            "qform_code": qform_code,
            "sform_code": int(image.header["sform_code"]),
            "spatial_units": spatial_units,
            "voxel_to_world_qform_mm": np.asarray(affine).tolist(),
            "occupied_voxel_rule": "MRI intensity > 0; coarse image occupancy only",
        },
        "electrode_table": {
            "file": coordinates_path.name,
            "sha256": sha256(coordinates_path),
            "sidecar": sidecar_path.name,
            "sidecar_sha256": sha256(sidecar_path),
            "electrode_names": electrode_names,
            **electrode_summary,
        },
        "fiducials": {
            "names": fiducial_names,
            "orientation_sanity_checks": orientation_checks,
            **fiducial_summary,
        },
        "interpretation_limit": (
            "This checks only a declared-coordinate-to-NIfTI-qform hypothesis. MRI nonzero voxels are not a scalp segmentation. "
            "The result cannot establish digitizer provenance, a saved transform, sensor-to-scalp accuracy, or reviewed registration QC. "
            "Do not use this audit alone to approve a forward model or source analysis."
        ),
    }


def compact_audit(full: dict[str, object], full_audit_sha256: str) -> dict[str, object]:
    """Keep replay-relevant hashes and summaries without electrode name lists."""
    compact_participants = []
    for item in full["participants"]:
        electrodes = item["electrode_table"]
        fiducials = item["fiducials"]
        mri = item["mri"]
        compact_participants.append({
            "participant": item["participant"],
            "mri": {
                "file": mri["file"],
                "sha256": mri["sha256"],
                "qform_code": mri["qform_code"],
                "sform_code": mri["sform_code"],
            },
            "electrode_table": {
                "file": electrodes["file"],
                "sha256": electrodes["sha256"],
                "sidecar": electrodes["sidecar"],
                "sidecar_sha256": electrodes["sidecar_sha256"],
                "point_count": electrodes["point_count"],
                "inside_image_count": electrodes["inside_image_count"],
                "outside_image_count": electrodes["outside_image_count"],
                "nearest_nonzero_mri_voxel_distance_mm_quantiles": (
                    electrodes["nearest_nonzero_mri_voxel_distance_mm_quantiles"]
                ),
                "within_5mm": electrodes[
                    "inside_points_within_5mm_of_nonzero_mri_voxel"
                ],
                "within_10mm": electrodes[
                    "inside_points_within_10mm_of_nonzero_mri_voxel"
                ],
            },
            "fiducials": {
                "names": fiducials["names"],
                "inside_image_count": fiducials["inside_image_count"],
                "outside_image_count": fiducials["outside_image_count"],
                "orientation_sanity_checks": fiducials[
                    "orientation_sanity_checks"
                ],
            },
        })
    return {
        "audit_id": full["audit_id"],
        "dataset_bids_version": full["dataset_bids_version"],
        "scope": full["scope"],
        "coordinate_frame_hypothesis": full["coordinate_frame_hypothesis"],
        "audit_script_sha256": full["audit_script_sha256"],
        "full_audit_sha256": full_audit_sha256,
        "participant_count": len(compact_participants),
        "participants": compact_participants,
        "interpretation_limit": full["global_limit"],
    }


def run(
    dataset_root: Path, output: Path, summary_output: Path | None = None
) -> dict[str, object]:
    dataset_root = dataset_root.resolve(strict=True)
    output = output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"refusing to overwrite audit output: {output}")
    if output == dataset_root or output.is_relative_to(dataset_root):
        raise ValueError("audit output must be outside the source dataset")
    if summary_output is not None:
        summary_output = summary_output.resolve()
        if summary_output == output:
            raise ValueError("full audit and compact summary outputs must differ")
        if summary_output.exists() or summary_output.is_symlink():
            raise FileExistsError(
                f"refusing to overwrite compact summary: {summary_output}"
            )
        if summary_output == dataset_root or summary_output.is_relative_to(dataset_root):
            raise ValueError("compact summary must be outside the source dataset")
    description = json.loads((dataset_root / "dataset_description.json").read_text(encoding="utf-8"))
    participants_file = dataset_root / "participants.tsv"
    with participants_file.open("r", encoding="utf-8-sig", newline="") as stream:
        participants = [row["participant_id"] for row in csv.DictReader(stream, delimiter="\t")]
    reports = [audit_participant(dataset_root, participant) for participant in participants]
    output.parent.mkdir(parents=True, exist_ok=True)
    full_audit = {
        "audit_id": "WSGZP_EEG_MRI_COORDINATE_COMPATIBILITY_2026-10-29-v2",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "audit_script_sha256": sha256(Path(__file__)),
        "scope": "Metadata and T1w MRI only; no EEG/iEEG recordings or epoch arrays opened.",
        "dataset_bids_version": description.get("BIDSVersion"),
        "coordinate_frame_hypothesis": "declared T1w XYZ millimetres are directly in the participant MRI qform world frame",
        "participant_count": len(reports),
        "participants": reports,
        "global_limit": (
            "This is a coarse compatibility screen, not a registration, scalp segmentation, or independent QC. "
            "Even a plausible result does not replace the original transform and reviewed sensor-to-scalp overlays."
        ),
    }
    serialized = json.dumps(full_audit, indent=2) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized, encoding="utf-8")
    result = {
        "status": "COMPLETE_CONDITIONAL_FRAME_SCREEN",
        "participant_count": len(reports),
        "output": str(output),
    }
    if summary_output is not None:
        summary = compact_audit(full_audit, sha256(output))
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        result["summary_output"] = str(summary_output)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--summary-output",
        type=Path,
        help="optional compact, hash-linked per-participant evidence JSON",
    )
    args = parser.parse_args()
    print(json.dumps(run(args.dataset_root, args.output, args.summary_output), indent=2))


if __name__ == "__main__":
    main()
