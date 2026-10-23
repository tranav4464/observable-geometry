"""Validate the Localize-MI sub-01/run-01 data, channel and geometry contract."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import h5py
import mne
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data/Localize-MI"
PAYLOAD = ROOT / "data/payload"
from tracka_paths import OUT
SUBJECT = "sub-01"
RUN = "01"
TOL_MM = 0.1


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xyz_by_name(path: Path) -> dict[str, np.ndarray]:
    return {
        row["name"]: np.array([float(row[axis]) for axis in ("x", "y", "z")])
        for row in read_tsv(path)
    }


def main() -> None:
    stem = f"{SUBJECT}_task-seegstim_run-{RUN}"
    base = META / "derivatives/epochs" / SUBJECT / "eeg" / stem
    epochs_path = PAYLOAD / "derivatives/epochs" / SUBJECT / "eeg" / f"{stem}_epochs.npy"
    fwd_path = PAYLOAD / "derivatives/sourcemodelling" / SUBJECT / "fwd" / f"{SUBJECT}_fwd.fif"
    transform_path = META / "derivatives/sourcemodelling" / SUBJECT / "xfm" / f"{SUBJECT}_from-head_to-surface.h5"
    if not all(p.is_file() for p in (epochs_path, fwd_path, transform_path)):
        raise SystemExit("Required epoch, forward or head-to-surface transform is missing")

    channels = read_tsv(base.with_name(stem + "_channels.tsv"))
    events = read_tsv(base.with_name(stem + "_epochs.tsv"))
    epoch_meta = json.loads(base.with_name(stem + "_epochs.json").read_text(encoding="utf-8"))
    eeg_positions = xyz_by_name(base.with_name(stem.replace("_run-01", "") + "_electrodes.tsv"))
    surface_contacts = xyz_by_name(
        META / "derivatives/epochs" / SUBJECT / "ieeg" /
        f"{SUBJECT}_task-seegstim_space-surface_electrodes.tsv"
    )
    eeg_coordsystem = json.loads(
        (META / "derivatives/epochs" / SUBJECT / "eeg" /
         f"{SUBJECT}_task-seegstim_coordsystem.json").read_text(encoding="utf-8")
    )
    ieeg_coordsystem = json.loads(
        (META / "derivatives/epochs" / SUBJECT / "ieeg" /
         f"{SUBJECT}_task-seegstim_space-surface_coordsystem.json").read_text(encoding="utf-8")
    )
    epochs = np.load(epochs_path, mmap_mode="r")
    sfreqs = {float(row["sampling_frequency"]) for row in channels}
    zero_times = {float(row["zero_time"]) for row in events}
    if len(sfreqs) != 1 or len(zero_times) != 1:
        raise SystemExit("Sampling rate or event-zero metadata disagree within the run")
    sfreq = sfreqs.pop()
    tmin = -zero_times.pop()
    times = tmin + np.arange(epochs.shape[-1]) / sfreq
    if epochs.ndim != 3 or epochs.shape[:2] != (len(events), len(channels)):
        raise SystemExit("Epoch array dimensions disagree with events/channels TSVs")
    good_names = [row["name"] for row in channels if row["status"] == "good"]
    if len(set(good_names)) != len(good_names):
        raise SystemExit("Duplicate channel names in good-channel list")

    fwd = mne.read_forward_solution(fwd_path, verbose="ERROR")
    fwd = mne.pick_channels_forward(fwd, include=good_names, ordered=True, copy=True, verbose="ERROR")
    if fwd["sol"]["row_names"] != good_names:
        raise SystemExit("Good EEG channels do not align exactly to forward rows")
    fwd_xyz = {ch["ch_name"]: np.asarray(ch["loc"][:3], float) for ch in fwd["info"]["chs"]}
    absent_positions = sorted(set(good_names) - set(eeg_positions))
    if absent_positions:
        raise SystemExit("EEG electrode coordinate table is missing channels: " + ", ".join(absent_positions[:8]))
    # The dataset authors' adapter constructs this table as a head-frame MNE montage.
    # Compare it directly to the supplied forward sensor coordinates; applying the
    # head-to-surface transform here would be a frame error.
    sensor_errors_mm = np.array([np.linalg.norm(fwd_xyz[n] - eeg_positions[n]) * 1000 for n in good_names])
    if float(sensor_errors_mm.max()) > TOL_MM:
        raise SystemExit(f"Forward and recorded sensor positions differ by {sensor_errors_mm.max():.3f} mm")

    with h5py.File(transform_path, "r") as h5:
        head_to_surface = np.asarray(h5["trans"][()], dtype=float)
    if head_to_surface.shape != (4, 4) or not np.allclose(head_to_surface[3], [0, 0, 0, 1], atol=1e-10):
        raise SystemExit("Head-to-surface transform is not a valid homogeneous affine matrix")
    surface_to_head = np.linalg.inv(head_to_surface)
    contacts = np.vstack([surface_contacts[n] for n in ("K13", "K14")])
    contacts_head = mne.transforms.apply_trans(surface_to_head, contacts)
    contacts_roundtrip = mne.transforms.apply_trans(head_to_surface, contacts_head)
    roundtrip_mm = float(np.max(np.linalg.norm(contacts_roundtrip - contacts, axis=1)) * 1000)
    if roundtrip_mm > 1e-6:
        raise SystemExit(f"Contact coordinate transform round-trip error {roundtrip_mm:g} mm")
    src_head = np.vstack([s["rr"][s["vertno"]] for s in fwd["src"]])
    src_surface = mne.transforms.apply_trans(head_to_surface, src_head)
    tree = cKDTree(src_surface)
    midpoint = contacts.mean(axis=0)
    contact_distances_mm = {name: float(tree.query(surface_contacts[name])[0] * 1000) for name in ("K13", "K14")}
    midpoint_distance_mm = float(tree.query(midpoint)[0] * 1000)
    contact_separation_mm = float(np.linalg.norm(contacts[0] - contacts[1]) * 1000)

    good_idx = [next(i for i, row in enumerate(channels) if row["name"] == name) for name in good_names]
    selected = np.asarray(epochs[:, good_idx, :])
    pre = (times >= -0.20) & (times <= -0.05)
    if not pre.any() or times.min() > -0.20 or times.max() < 0:
        raise SystemExit("Declared pre-event noise window is not covered by the epoch")
    baseline_residual = selected[:, :, pre].mean(axis=(0, 2))
    event_types = sorted({row["trial_type"] for row in events})
    if not epoch_meta.get("BaselineCorrection") or epoch_meta.get("BaselinePeriod") != [-0.3, -0.05]:
        raise SystemExit("Baseline correction metadata differ from the pinned dataset contract")
    if eeg_coordsystem.get("EEGCoordinateUnits") != "m" or ieeg_coordsystem.get("iEEGCoordinateUnits") != "m":
        raise SystemExit("Unexpected coordinate units")

    report = {
        "status": "PASS",
        "case": f"{SUBJECT}/run-{RUN}",
        "task": "localization of the measured intracranial stimulation artifact; not spontaneous neural activity",
        "events": len(events), "event_types": event_types, "sampling_rate_hz": sfreq,
        "epoch_range_s": [float(times[0]), float(times[-1])],
        "baseline_correction": {"applied_by_dataset": True, "period_s": epoch_meta["BaselinePeriod"],
                                "analysis_noise_window_s": [-0.20, -0.05]},
        "channel_contract": {"good_channels": len(good_names), "exact_name_order_match": True,
                             "forward_vs_electrode_position_max_error_mm": float(sensor_errors_mm.max()),
                             "forward_vs_electrode_position_median_error_mm": float(np.median(sensor_errors_mm)),
                             "reference_for_analysis": "average of selected good EEG channels; same projection applied to data, leadfield and covariance"},
        "source_target": {"kind": "known bipolar stimulation-contact pair; midpoint used as a declared cortical surface reference",
                          "contacts": ["K13", "K14"], "contact_pair_surface_separation_mm": contact_separation_mm,
                          "contact_to_nearest_cortical_vertex_mm": contact_distances_mm,
                          "midpoint_to_nearest_cortical_vertex_mm": midpoint_distance_mm,
                          "transform_roundtrip_error_mm": roundtrip_mm,
                          "coordinate_frames": {"contact_file": "native FreeSurfer surface coordinates, metres",
                                                "forward source file": "head coordinates; transformed with the dataset head-to-surface affine"},
                          "interpretation": "The pair midpoint is a benchmark reference for the pulse artifact. It is not exact ground truth for a distributed physiological response."},
        "hashes_sha256": {"epochs": sha256(epochs_path), "forward": sha256(fwd_path),
                          "head_to_surface": sha256(transform_path)},
        "dataset_license": "CC-BY-NC-SA 4.0",
        "baseline_window_mean_abs_uv": float(np.mean(np.abs(baseline_residual)) * 1e6),
        "limitations": ["One participant and one stimulation condition; development/integration case only.",
                        "The task is specifically the pulse artifact localization benchmark.",
                        "Cortical midpoint projection is an explicit approximation; do not infer physiological source localization."]
    }
    dest = OUT / "case_validation.json"
    dest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
