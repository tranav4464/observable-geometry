"""B1 participant geometry audit using metadata and forward files, no EEG values."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import h5py
import mne
import numpy as np
from scipy.spatial import cKDTree

from fetch_localize import META, PAYLOAD, ROOT


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def positions(path: Path) -> dict[str, np.ndarray]:
    return {row["name"]: np.array([float(row[key]) for key in ("x", "y", "z")])
            for row in tsv(path)}


def contacts_for(label: str) -> tuple[str, str]:
    first, second_number = label.split()[0].split("-")
    prefix = "".join(char for char in first if not char.isdigit())
    return first, prefix + second_number


def audit(subject: str) -> dict:
    sid = f"sub-{subject}"
    fwd_path = PAYLOAD / "derivatives" / "sourcemodelling" / sid / "fwd" / f"{sid}_fwd.fif"
    forward = mne.read_forward_solution(fwd_path, verbose="ERROR")
    eeg_dir = META / "derivatives" / "epochs" / sid / "eeg"
    metadata_eeg = positions(eeg_dir / f"{sid}_task-seegstim_electrodes.tsv")
    forward_eeg = {ch["ch_name"]: np.asarray(ch["loc"][:3], dtype=float)
                   for ch in forward["info"]["chs"]}
    if set(metadata_eeg) != set(forward_eeg):
        raise ValueError(f"EEG electrode names differ from forward in {sid}")
    sensor_error_mm = np.array([np.linalg.norm(metadata_eeg[name] - forward_eeg[name]) * 1000
                                for name in forward["sol"]["row_names"]])
    if not np.isfinite(sensor_error_mm).all() or sensor_error_mm.max() > .1:
        raise ValueError(f"Forward/metadata EEG position mismatch in {sid}: {sensor_error_mm.max():.3f} mm")

    xfm_path = META / "derivatives" / "sourcemodelling" / sid / "xfm" / f"{sid}_from-head_to-surface.h5"
    with h5py.File(xfm_path) as stream:
        head_to_surface = np.asarray(stream["trans"][()], dtype=float)
    if head_to_surface.shape != (4, 4) or not np.allclose(head_to_surface[3], [0, 0, 0, 1], atol=1e-10):
        raise ValueError(f"Invalid head-to-surface affine in {sid}")
    inverse = np.linalg.inv(head_to_surface)
    src_head = np.vstack([space["rr"][space["vertno"]] for space in forward["src"]])
    src_surface = mne.transforms.apply_trans(head_to_surface, src_head)
    tree = cKDTree(src_surface)

    contact_file = META / "derivatives" / "epochs" / sid / "ieeg" / f"{sid}_task-seegstim_space-surface_electrodes.tsv"
    contact_xyz = positions(contact_file)
    eeg_units = json.loads((eeg_dir / f"{sid}_task-seegstim_coordsystem.json").read_text(encoding="utf-8"))
    ieeg_units = json.loads((contact_file.with_name(f"{sid}_task-seegstim_space-surface_coordsystem.json")).read_text(encoding="utf-8"))
    if eeg_units.get("EEGCoordinateUnits") != "m" or ieeg_units.get("iEEGCoordinateUnits") != "m":
        raise ValueError(f"Unexpected coordinate units in {sid}")

    pair_to_runs: dict[tuple[str, str], list[str]] = {}
    epoch_paths = sorted(eeg_dir.glob(f"{sid}_task-seegstim_run-*_epochs.tsv"))
    for path in epoch_paths:
        events = tsv(path)
        labels = {row["trial_type"] for row in events}
        if len(labels) != 1:
            raise ValueError(f"Mixed stimulation pair in {path}")
        label = next(iter(labels))
        pair_to_runs.setdefault(contacts_for(label), []).append(path.name)

    pair_rows = []
    for (first, second), runs in sorted(pair_to_runs.items()):
        if first not in contact_xyz or second not in contact_xyz:
            raise ValueError(f"Unknown contact pair in {sid}: {first}, {second}")
        contacts = np.vstack([contact_xyz[first], contact_xyz[second]])
        back = mne.transforms.apply_trans(head_to_surface, mne.transforms.apply_trans(inverse, contacts))
        roundtrip_mm = float(np.max(np.linalg.norm(back - contacts, axis=1)) * 1000)
        if roundtrip_mm > 1e-6:
            raise ValueError(f"Contact transform roundtrip failed in {sid}")
        separation_mm = float(np.linalg.norm(contacts[1] - contacts[0]) * 1000)
        midpoint_mm, nearest = tree.query(contacts.mean(axis=0))
        pair_rows.append({"contacts": [first, second], "runs": runs,
                          "separation_mm": separation_mm,
                          "midpoint_to_nearest_cortical_vertex_mm": float(midpoint_mm * 1000),
                          "nearest_source_index": int(nearest),
                          "nearest_source_surface_mm": (src_surface[int(nearest)] * 1000).tolist(),
                          "roundtrip_mm": roundtrip_mm})
    offsets = np.array([row["midpoint_to_nearest_cortical_vertex_mm"] for row in pair_rows])
    proxy_separations = []
    for left_index, left in enumerate(pair_rows):
        for right in pair_rows[left_index + 1:]:
            distance = float(np.linalg.norm(
                np.asarray(left["nearest_source_surface_mm"])
                - np.asarray(right["nearest_source_surface_mm"])
            ))
            proxy_separations.append({
                "contacts_a": left["contacts"],
                "contacts_b": right["contacts"],
                "source_proxy_separation_mm": distance,
                "eligible_at_20mm": distance >= 20.0,
            })
    input_paths = [
        fwd_path,
        xfm_path,
        eeg_dir / f"{sid}_task-seegstim_electrodes.tsv",
        eeg_dir / f"{sid}_task-seegstim_coordsystem.json",
        contact_file,
        contact_file.with_name(f"{sid}_task-seegstim_space-surface_coordsystem.json"),
        *epoch_paths,
    ]
    return {"participant": sid, "scope": "metadata and forward geometry only; no EEG waveform values",
            "input_sha256": {path.relative_to(ROOT).as_posix(): file_sha256(path)
                             for path in sorted(input_paths)},
            "sensor_position_error_mm": {"max": float(sensor_error_mm.max()),
                                         "median": float(np.median(sensor_error_mm))},
            "n_forward_sources": forward["nsource"], "n_contact_pairs": len(pair_rows),
            "midpoint_offset_mm": {"median": float(np.median(offsets)), "max": float(offsets.max()),
                                   "count_over_10mm": int(np.sum(offsets > 10)),
                                   "count_over_20mm": int(np.sum(offsets > 20))},
            "contact_pairs": pair_rows,
            "source_proxy_pairwise_separation": {
                "distance_definition": "Euclidean distance between nearest fixed-orientation cortical source proxy coordinates in the surface frame",
                "minimum_eligible_mm": 20.0,
                "candidate_pair_count": len(proxy_separations),
                "eligible_pair_count": sum(item["eligible_at_20mm"] for item in proxy_separations),
                "pairs": proxy_separations,
            }}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="+", choices=[f"{i:02d}" for i in range(1, 8)], required=True)
    args = parser.parse_args()
    reports = [audit(subject) for subject in args.subjects]
    report = {"status": "PASS", "scope": "geometry metadata only, no EEG outcomes", "participants": reports}
    out = ROOT / "outputs" / "track_b" / "data_acquisition"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("geometry_sub-" + "_".join(args.subjects) + ".json")
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "participants": [r["participant"] for r in reports],
                      "max_sensor_error_mm": max(r["sensor_position_error_mm"]["max"] for r in reports),
                      "offsets_over_20mm": sum(r["midpoint_offset_mm"]["count_over_20mm"] for r in reports),
                      "report": str(path)}, indent=2))


if __name__ == "__main__":
    main()
