"""Create a synthetic-only, geometry-derived operator from the licensed fwd file.

Only the anatomical forward solution is read. No epochs, EEG, iEEG, labels, or
participant outcomes are opened. The resulting operator is local development
material derived from CC BY-NC-SA data and must not be redistributed without
following that license.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import mne
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from observable_geometry.track_b.physical_synthetic import geometric_regional_leadfield


FORWARD = ROOT / "data" / "payload" / "derivatives" / "sourcemodelling" / "sub-01" / "fwd" / "sub-01_fwd.fif"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forward", type=Path, default=FORWARD)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=20261022)
    args = parser.parse_args()
    forward_path = args.forward.resolve()
    out_dir = args.out_dir.resolve()
    if out_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {out_dir}")
    if not forward_path.is_file():
        raise SystemExit(f"Forward solution not found: {forward_path}")

    forward = mne.read_forward_solution(forward_path, verbose="ERROR")
    channel_names = list(forward["sol"]["row_names"])
    channel_types = [mne.channel_type(forward["info"], i) for i in range(len(channel_names))]
    if not channel_names or any(kind != "eeg" for kind in channel_types):
        raise SystemExit("Expected an EEG-only forward solution")
    if len(forward["src"]) != 2 or any(space["type"] != "surf" for space in forward["src"]):
        raise SystemExit("Expected two cortical surface source spaces")
    counts = [len(space["vertno"]) for space in forward["src"]]
    if sum(counts) != forward["nsource"]:
        raise SystemExit("Forward source spaces do not match solution dimensions")

    # Fixed orientation maps each cortical node's scalar normal dipole to scalp
    # voltage. This changes orientation representation only; it reads no signals.
    fixed = mne.convert_forward_solution(forward, surf_ori=True, force_fixed=True,
                                        use_cps=True, verbose="ERROR")
    if fixed["sol"]["data"].shape != (len(channel_names), forward["nsource"]):
        raise SystemExit("Fixed-orientation conversion returned an unexpected matrix")
    positions = np.vstack([space["rr"][space["vertno"]] for space in fixed["src"]])
    hemisphere = np.concatenate([np.full(counts[0], 0, dtype=np.int8),
                                 np.full(counts[1], 1, dtype=np.int8)])
    regional = geometric_regional_leadfield(
        fixed["sol"]["data"], positions, hemisphere,
        regions_per_hemisphere=(35, 34), seed=args.seed,
        average_reference=True,
    )
    out_dir.mkdir(parents=True, exist_ok=False)
    operator_path = out_dir / "sub01_geometric_leadfield.npz"
    np.savez_compressed(operator_path,
                        scalp_operator=regional.operator,
                        node_positions_m=regional.node_positions_m,
                        hemisphere=regional.hemisphere,
                        parcel_sizes=regional.parcel_sizes,
                        source_to_node=regional.source_to_node,
                        reference_operator=regional.reference_operator)
    operator_hash = sha256(operator_path)
    report = {
        "status": "PASS: synthetic geometry operator built; no participant signals read",
        "run_role": "development_geometry_only",
        "participant_geometry": "sub-01",
        "participant_signal_arrays_read": False,
        "source_file": str(forward_path.relative_to(ROOT)) if forward_path.is_relative_to(ROOT) else str(forward_path),
        "source_file_sha256": sha256(forward_path),
        "dataset_license": "CC BY-NC-SA 4.0; derived operator is local and not cleared for redistribution",
        "mne_version": mne.__version__,
        "channels": len(channel_names),
        "source_vertices": int(forward["nsource"]),
        "hemisphere_source_counts": counts,
        "leadfield_units": "V per A m, inherited from MNE EEG forward solution",
        "operator_shape": list(regional.operator.shape),
        "node_count": int(regional.operator.shape[1]),
        "node_construction": "separate deterministic 3D Euclidean k-means patches on left/right cortical meshes; equal-weight average of fixed-normal lead fields",
        "node_interpretation": "geometric simulation nodes only; not Harvard-Oxford labels or validated anatomical regions",
        "average_reference": "applied as I - 11^T/M to the forward operator",
        "operator_rank": int(np.linalg.matrix_rank(regional.operator)),
        "parcel_sizes": regional.parcel_sizes.tolist(),
        "leadfield_column_norms": {
            "minimum": float(np.min(np.linalg.norm(regional.operator, axis=0))),
            "median": float(np.median(np.linalg.norm(regional.operator, axis=0))),
            "maximum": float(np.max(np.linalg.norm(regional.operator, axis=0))),
        },
        "operator_file": operator_path.name,
        "operator_sha256": operator_hash,
        "limitations": [
            "The operator uses one participant's released head geometry and the provided forward, not an independently validated universal head model.",
            "The equal-weight Euclidean parcels are a synthetic spatial basis, not an anatomical atlas.",
            "The iEEG observation operator in the paired benchmark will remain idealized direct state selection, not electrode-level iEEG physics.",
            "The data are CC BY-NC-SA 4.0; do not redistribute the forward solution or derived operator without license review.",
        ],
    }
    report_path = out_dir / "operator_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "operator": str(operator_path),
                      "sha256": operator_hash, "operator_shape": report["operator_shape"],
                      "operator_rank": report["operator_rank"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
