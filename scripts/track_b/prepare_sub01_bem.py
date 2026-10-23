"""Check whether Localize-MI sub-01 meshes support a layered EEG BEM.

The source GIFTI meshes are converted to FreeSurfer geometry in a new output
directory. This is anatomy-only. No EEG sample values or test data are read.
The output is a candidate conductor geometry with assumed conductivities;
it is not a validated bipolar-injection forward model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mne
import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "Localize-MI" / "derivatives" / "sourcemodelling" / "sub-01" / "anat"
OUTPUT = ROOT / "outputs" / "track_b" / "development" / "sub01_bem_feasibility"
SHELLS = ("inner_skull", "outer_skull", "outer_skin")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mesh_contract(coords: np.ndarray, faces: np.ndarray, name: str) -> dict:
    if (coords.ndim != 2 or coords.shape[1] != 3 or faces.ndim != 2
            or faces.shape[1] != 3 or not np.isfinite(coords).all()
            or faces.min() < 0 or faces.max() >= len(coords)):
        raise ValueError(f"Invalid mesh arrays: {name}")
    edges = np.sort(faces[:, [[0, 1], [1, 2], [2, 0]]].reshape(-1, 2), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    if np.any(counts != 2):
        raise ValueError(f"Nonclosed/nonmanifold mesh edges: {name}")
    # Oriented volume flags inward winding but does not prove nested surfaces.
    signed_volume = float(np.einsum(
        "ij,ij->i", coords[faces[:, 0]],
        np.cross(coords[faces[:, 1]], coords[faces[:, 2]])).sum() / 6)
    return {"vertices": len(coords), "triangles": len(faces),
            "closed_manifold": True, "signed_volume_mm3": signed_volume,
            "min_mm": coords.min(axis=0).tolist(), "max_mm": coords.max(axis=0).tolist()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ico", type=int, default=3, choices=[2, 3, 4, 5])
    parser.add_argument("--solve", action="store_true", help="compute and save the BEM solution")
    args = parser.parse_args()
    subject_dir = OUTPUT / "fs_subjects" / "sub-01" / "bem"
    subject_dir.mkdir(parents=True, exist_ok=True)
    sources = {}
    for shell in SHELLS:
        source = SOURCE / f"sub-01_{shell}.surf.gii"
        image = nib.load(str(source))
        coords = np.asarray(image.darrays[0].data, dtype=float)
        faces = np.asarray(image.darrays[1].data, dtype=np.int32)
        details = mesh_contract(coords, faces, shell)
        target = subject_dir / f"{shell}.surf"
        if target.exists():
            existing_coords, existing_faces = nib.freesurfer.read_geometry(str(target))
            if not np.array_equal(existing_coords, coords.astype(np.float32)) or not np.array_equal(existing_faces, faces):
                raise ValueError(f"Existing converted mesh differs: {target}")
        else:
            nib.freesurfer.write_geometry(str(target), coords.astype(np.float32), faces)
        sources[shell] = {"source": str(source.relative_to(ROOT)), "sha256": sha256(source),
                          "converted": str(target.relative_to(ROOT)), **details}
    conductivities = (.3, .006, .3)  # Assumed S/m: brain, skull, scalp.
    model = mne.make_bem_model("sub-01", ico=args.ico, conductivity=conductivities,
                               subjects_dir=OUTPUT / "fs_subjects", verbose="ERROR")
    summary = {"status": "candidate BEM geometry only", "participant": "sub-01",
               "no_eeg_values_read": True, "ico": args.ico,
               "assumed_conductivities_s_per_m": conductivities,
               "sources": sources,
               "downsampled_vertices": [len(surface["rr"]) for surface in model],
               "downsampled_triangles": [len(surface["tris"]) for surface in model]}
    out = OUTPUT / (f"bem_ico{args.ico}_solution_report.json" if args.solve
                    else f"bem_ico{args.ico}_geometry.json")
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite BEM geometry report: {out}")
    if args.solve:
        solution_path = OUTPUT / f"bem_ico{args.ico}_solution.fif"
        if solution_path.exists():
            raise FileExistsError(f"Refusing to overwrite BEM solution: {solution_path}")
        solution = mne.make_bem_solution(model, verbose="ERROR")
        mne.write_bem_solution(solution_path, solution, overwrite=False, verbose="ERROR")
        summary["solution"] = str(solution_path.relative_to(ROOT))
        summary["status"] = "candidate BEM solution; source physics unvalidated"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "ico": args.ico,
                      "vertices": summary["downsampled_vertices"],
                      "triangles": summary["downsampled_triangles"]}, indent=2))


if __name__ == "__main__":
    main()
