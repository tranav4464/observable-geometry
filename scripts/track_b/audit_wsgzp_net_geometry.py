"""Compare WSGZP scalp-net pairwise geometry with the MNE HydroCel-256 template.

This coordinate-only check is invariant to translation and rotation. It tests
net-shape consistency, not electrode-to-MRI coregistration or source accuracy.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import mne
import numpy as np
from scipy.spatial.distance import pdist

from audit_wsgzp_coregistration import resolve_subjects


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pairwise_shape_fit(actual_mm: np.ndarray, reference_m: np.ndarray) -> dict:
    actual = np.asarray(actual_mm, dtype=np.float64)
    reference = np.asarray(reference_m, dtype=np.float64)
    if actual.ndim != 2 or reference.shape != actual.shape or actual.shape[1] != 3:
        raise ValueError("Actual and reference coordinates must have the same N x 3 shape")
    if len(actual) < 4 or not np.isfinite(actual).all() or not np.isfinite(reference).all():
        raise ValueError("At least four finite electrode coordinates are required")
    d_actual = pdist(actual)
    d_reference_mm = pdist(reference) * 1000.0
    den = float(d_reference_mm @ d_reference_mm)
    if den <= 0:
        raise ValueError("Reference layout has degenerate pairwise geometry")
    scale = float((d_reference_mm @ d_actual) / den)
    residual = d_actual - scale * d_reference_mm
    corr = float(np.corrcoef(d_reference_mm, d_actual)[0, 1])
    return {
        "n_electrodes": int(len(actual)),
        "n_pairs": int(len(d_actual)),
        "isotropic_scale_actual_over_template": scale,
        "pairwise_distance_correlation": corr,
        "pairwise_distance_rmse_mm_after_scale": float(np.sqrt(np.mean(residual**2))),
        "pairwise_distance_abs_error_p95_mm_after_scale": float(np.quantile(np.abs(residual), 0.95)),
        "pairwise_shape_only": True,
        "pose_alignment_tested": False,
    }


def audit_subject(root: Path, subject: str, reference_positions: dict[str, np.ndarray]) -> dict:
    table = root / "derivatives" / "epochs" / subject / "eeg" / f"{subject}_task-ccepcoreg_electrodes.tsv"
    coordsystem = table.with_name(f"{subject}_task-ccepcoreg_coordsystem.json")
    if not table.is_file() or not coordsystem.is_file():
        raise FileNotFoundError(table if not table.is_file() else coordsystem)
    contract = json.loads(coordsystem.read_text(encoding="utf-8"))
    if contract.get("EEGCoordinateSystem") != "T1w" or contract.get("EEGCoordinateUnits") != "mm":
        raise ValueError(f"Unexpected WSGZP EEG coordinate contract for {subject}")
    with table.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    names = [row["name"].upper() for row in rows]
    if len(names) != len(set(names)):
        raise ValueError(f"Duplicate channel names for {subject}")
    missing = [name for name in names if name not in reference_positions]
    if missing:
        raise ValueError(f"Electrode labels missing from HydroCel-256 reference: {missing}")
    actual = np.asarray([[float(row[key]) for key in ("x", "y", "z")] for row in rows])
    reference = np.asarray([reference_positions[name] for name in names])
    result = pairwise_shape_fit(actual, reference)
    return {
        "subject": subject,
        **result,
        "input_sha256": {"electrodes": sha256(table), "coordsystem": sha256(coordsystem)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--subjects", nargs="*", default=None)
    args = parser.parse_args()
    root = args.dataset_root.resolve()
    try:
        subjects = resolve_subjects(root, args.subjects)
    except ValueError as exc:
        parser.error(str(exc))

    montage = mne.channels.make_standard_montage("GSN-HydroCel-256")
    reference_positions = {
        name.upper(): np.asarray(position, dtype=np.float64)
        for name, position in montage.get_positions()["ch_pos"].items()
    }
    reports, failures = [], []
    for subject in subjects:
        try:
            reports.append(audit_subject(root, subject, reference_positions))
        except Exception as exc:
            failures.append({"subject": subject, "error": f"{type(exc).__name__}: {exc}"})
    result = {
        "audit_id": "WSGZP-HYDROCEL-NET-SHAPE-2026-10-28-v1",
        "mne_version": mne.__version__,
        "reference_montage": "MNE built-in GSN-HydroCel-256",
        "dataset_root": str(root),
        "status": "SHAPE_SCREEN_ONLY",
        "signal_samples_read": False,
        "subject_count_requested": len(subjects),
        "subject_count_audited": len(reports),
        "subject_count_failed": len(failures),
        "limitations": [
            "Pairwise-distance agreement is invariant to rigid pose; it cannot verify translation, rotation, MRI registration, or head-model accuracy.",
            "The MNE HydroCel-256 positions are a standard template and are not participant-specific ground truth.",
            "The fit allows one isotropic scale factor and is a geometric consistency check, not a sensor calibration.",
            "No EEG/iEEG sample arrays are accessed.",
        ],
        "subjects": reports,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "subjects"}, indent=2))


if __name__ == "__main__":
    main()
