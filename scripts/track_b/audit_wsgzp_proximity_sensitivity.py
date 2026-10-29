"""Check whether coarse WSGZP MRI-proximity triage depends on intensity threshold.

This is a coordinate-only screen. It is not scalp segmentation or registration
validation and never reads EEG/iEEG sample arrays.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_wsgzp_electrode_mri_proximity import audit_subject


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--subjects", nargs="+", default=["sub-01", "sub-32"])
    parser.add_argument("--thresholds", nargs="+", type=float, default=[10, 25, 50, 100, 200])
    parser.add_argument("--step", type=int, default=2)
    args = parser.parse_args()

    if args.step < 1 or not args.thresholds:
        parser.error("--step must be positive and at least one threshold is required")
    rows = []
    for subject in args.subjects:
        for threshold in args.thresholds:
            result = audit_subject(
                args.dataset_root,
                subject,
                threshold=threshold,
                step=args.step,
            )
            rows.append({
                "subject": subject,
                "threshold_intensity": threshold,
                "voxel_sampling_step": args.step,
                "eeg_distance_quantiles_mm": result["distance_quantiles_mm"],
                "seeg_control_distance_quantiles_mm": result["seeg_positive_control"]["distance_quantiles_mm"],
                "input_sha256": result["input_sha256"],
            })

    report = {
        "audit_id": "WSGZP-PROXIMITY-THRESHOLD-SENSITIVITY-2026-10-28-v1",
        "status": "SCREEN_ONLY_REVIEW_REQUIRED",
        "signal_samples_read": False,
        "dataset_root": str(args.dataset_root.resolve()),
        "subjects": args.subjects,
        "thresholds": args.thresholds,
        "voxel_sampling_step": args.step,
        "interpretation": [
            "Distances are approximate distances to sampled MRI voxels above a global intensity threshold.",
            "Threshold stability is sensitivity evidence only; it is not scalp segmentation or coregistration validation.",
            "SEEG contacts are a positive control for the native MRI coordinate interpretation, not for scalp-electrode registration.",
            "No EEG or iEEG sample arrays are accessed.",
        ],
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
