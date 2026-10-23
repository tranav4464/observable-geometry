"""Compare a regenerated candidate BEM forward to the released forward.

This checks solver/coordinate plausibility using anatomy and forward matrices.
It reads no EEG epochs. Agreement is not validation of pulse-injection physics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from copy import deepcopy

import mne
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "data" / "payload" / "derivatives" / "sourcemodelling" / "sub-01" / "fwd" / "sub-01_fwd.fif"
VERTICES = (0, 1000, 2000, 4000, 6000, 8195)


def orthonormal_basis(matrix: np.ndarray) -> np.ndarray:
    basis, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    if singular[-1] < 1e-10 * singular[0]:
        raise ValueError("Leadfield triplet is rank deficient")
    return basis[:, :3]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ico", type=int, choices=[3, 4], default=3)
    args = parser.parse_args()
    base = ROOT / "outputs" / "track_b" / "development" / "sub01_bem_feasibility"
    candidate = base / f"bem_ico{args.ico}_solution.fif"
    destination = base / f"forward_comparison_ico{args.ico}.json"
    if destination.exists():
        raise FileExistsError(destination)
    original = mne.read_forward_solution(ORIGINAL, verbose="ERROR")
    original_positions = np.vstack([space["rr"][space["vertno"]] for space in original["src"]])
    selected_positions = original_positions[list(VERTICES)]
    source_space = mne.setup_volume_source_space(
        pos={"rr": selected_positions, "nn": np.tile([0.0, 0.0, 1.0], (len(VERTICES), 1))},
        verbose="ERROR")
    # FIF forward files contain a reduced info dictionary, not a full Info.
    # Reconstruct required measurement fields while retaining the published
    # ordered EEG channel geometry exactly.
    info = mne.create_info(original["info"]["ch_names"], 8000.0, "eeg")
    with info._unlock():
        info["chs"] = deepcopy(original["info"]["chs"])
    regenerated = mne.make_forward_solution(
        info, trans=original["mri_head_t"], src=source_space,
        bem=candidate, meg=False, eeg=True, mindist=0.0,
        on_inside="raise", verbose="ERROR")
    selected_positions_head = mne.transforms.apply_trans(original["mri_head_t"], selected_positions)
    kept_positions = regenerated["src"][0]["rr"][regenerated["src"][0]["vertno"]]
    kept_selected_indices = [int(np.argmin(np.linalg.norm(selected_positions_head - point, axis=1)))
                             for point in kept_positions]
    if (regenerated["sol"]["row_names"] != original["sol"]["row_names"]
            or regenerated["sol"]["data"].shape != (original["nchan"], 3 * len(kept_positions))
            or len(set(kept_selected_indices)) != len(kept_selected_indices)
            or any(np.linalg.norm(selected_positions_head[j] - point) > 1e-6
                   for j, point in zip(kept_selected_indices, kept_positions))):
        raise ValueError(f"Regenerated sensor identity, source count or source coordinates differ: "
                         f"shape={regenerated['sol']['data'].shape}, "
                         f"kept={kept_selected_indices}, "
                         f"coord_errors={[float(np.linalg.norm(selected_positions_head[j] - point)) for j, point in zip(kept_selected_indices, kept_positions)]}, "
                         f"src_frame={regenerated['src'][0]['coord_frame']}")
    reference = np.eye(original["nchan"]) - np.ones((original["nchan"], original["nchan"])) / original["nchan"]
    rows = []
    for i, selected_index in enumerate(kept_selected_indices):
        vertex = VERTICES[selected_index]
        published = reference @ original["sol"]["data"][:, 3 * vertex:3 * vertex + 3]
        candidate_leadfield = reference @ regenerated["sol"]["data"][:, 3 * i:3 * i + 3]
        correlations = np.linalg.svd(orthonormal_basis(published).T @
                                     orthonormal_basis(candidate_leadfield), compute_uv=False)
        rows.append({"source_index": vertex, "position_mri_m": selected_positions[selected_index].tolist(),
                     "canonical_correlations": correlations.tolist(),
                     "min_canonical_correlation": float(correlations.min())})
    report = {"status": "forward/coordinate feasibility only; no EEG outcomes read",
              "candidate_bem": str(candidate.relative_to(ROOT)), "ico": args.ico,
              "reference": "average reference applied to both forwards",
              "vertices": rows,
              "dropped_source_indices": [vertex for i, vertex in enumerate(VERTICES)
                                         if i not in kept_selected_indices],
              "minimum_correlation": min(row["min_canonical_correlation"] for row in rows),
              "limitations": ["The published forward may use different conductivity or mesh resolution",
                              "A dipole forward subspace does not establish bipolar-current injection physics"]}
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "sources": len(rows),
                      "minimum_canonical_correlation": report["minimum_correlation"]}, indent=2))


if __name__ == "__main__":
    main()
