"""Development-only physical adequacy diagnostic for six sub-01 pulse artifacts.

Fits amplitudes/orientation on alternating training trials and scores held-out
trials at a training-selected pulse time. Never accesses Track B test outcomes.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from copy import deepcopy

import h5py
import mne
import numpy as np
from scipy.spatial import cKDTree

from observable_geometry.track_b.physical import (
    bipolar_line_quadrature, homogeneous_bipolar_signature)


ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "data" / "Localize-MI"
PAYLOAD = ROOT / "data" / "payload"
RUNS = (1, 3, 5, 6, 8, 10)
SUBJECT = "sub-01"


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def contact_names(label: str) -> tuple[str, str]:
    first, number = label.split()[0].split("-")
    prefix = "".join(char for char in first if not char.isdigit())
    return first, prefix + number


def score(test: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    denominator = float(test @ test)
    if denominator <= 0:
        raise ValueError("Zero-energy held-out topography")
    return {"heldout_whitened_r2": float(1 - np.sum((test - predicted) ** 2) / denominator),
            "heldout_abs_cosine": float(abs(test @ predicted) /
                                         (np.linalg.norm(test) * np.linalg.norm(predicted)))}


def residual_repeatability(train: np.ndarray, test: np.ndarray,
                           predicted: np.ndarray) -> dict[str, float]:
    """Signed split-half cosine of unmodelled whitened sensor topography.

    A high value suggests a reproducible omitted component, but split halves
    share a run and this quantity is not a calibrated significance test.
    """
    train_residual = train - predicted
    test_residual = test - predicted
    scale = np.linalg.norm(train_residual) * np.linalg.norm(test_residual)
    return {"train_test_residual_cosine": float(train_residual @ test_residual / scale)
            if scale > 0 else float("nan"),
            "train_residual_energy_fraction": float(train_residual @ train_residual / (train @ train)),
            "test_residual_energy_fraction": float(test_residual @ test_residual / (test @ test))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["alternating", "contiguous"], default="alternating")
    parser.add_argument("--layered", action="store_true", help="add candidate three-layer BEM source-sink line model")
    args = parser.parse_args()
    output = ROOT / "outputs" / "track_b" / "development"
    output_name = (f"sub01_layered_adequacy_{args.split}.json" if args.layered else
                   "sub01_dipole_adequacy.json" if args.split == "alternating"
                   else "sub01_dipole_adequacy_contiguous.json")
    destination = output / output_name
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite a development result: {destination}")
    eeg = META / "derivatives" / "epochs" / SUBJECT / "eeg"
    payload_eeg = PAYLOAD / "derivatives" / "epochs" / SUBJECT / "eeg"
    contact_path = META / "derivatives" / "epochs" / SUBJECT / "ieeg" / f"{SUBJECT}_task-seegstim_space-surface_electrodes.tsv"
    contacts = {row["name"]: np.array([float(row[key]) for key in ("x", "y", "z")])
                for row in tsv(contact_path)}

    # Match the Track A channel contract, including runs that are not primary.
    good = None
    for run in range(1, 12):
        path = eeg / f"{SUBJECT}_task-seegstim_run-{run:02d}_channels.tsv"
        current = {row["name"] for row in tsv(path) if row["status"] == "good" and row["type"] == "EEG"}
        good = current if good is None else good & current
    first_channels = tsv(eeg / f"{SUBJECT}_task-seegstim_run-01_channels.tsv")
    names = [row["name"] for row in first_channels if row["name"] in good]
    if len(names) < 100:
        raise ValueError("Insufficient common good EEG channels")

    forward_path = PAYLOAD / "derivatives" / "sourcemodelling" / SUBJECT / "fwd" / f"{SUBJECT}_fwd.fif"
    free = mne.read_forward_solution(forward_path, verbose="ERROR")
    free = mne.pick_channels_forward(free, include=names, ordered=True, copy=True, verbose="ERROR")
    if free["surf_ori"] or free["sol"]["row_names"] != names:
        raise ValueError("Free forward is not in ordered Cartesian head coordinates")
    sensor_head = np.vstack([channel["loc"][:3] for channel in free["info"]["chs"]])
    if args.layered:
        bem_path = (ROOT / "outputs" / "track_b" / "development" / "sub01_bem_feasibility"
                    / "bem_ico3_solution.fif")
        info = mne.create_info(names, sfreq=8000.0, ch_types="eeg")
        with info._unlock():
            info["chs"] = deepcopy(free["info"]["chs"])
    fixed = mne.convert_forward_solution(free, surf_ori=True, force_fixed=True, use_cps=True, verbose="ERROR")
    source_head = np.vstack([space["rr"][space["vertno"]] for space in free["src"]])
    transform_path = META / "derivatives" / "sourcemodelling" / SUBJECT / "xfm" / f"{SUBJECT}_from-head_to-surface.h5"
    with h5py.File(transform_path) as stream:
        head_to_surface = np.asarray(stream["trans"][()], dtype=float)
    source_surface = mne.transforms.apply_trans(head_to_surface, source_head)
    tree = cKDTree(source_surface)

    count = 0
    sum_x = np.zeros(len(names))
    sum_xx = np.zeros((len(names), len(names)))
    cases = []
    sfreq, zero_time = 8000.0, 0.25
    for run in RUNS:
        stem = f"{SUBJECT}_task-seegstim_run-{run:02d}"
        channel_rows = tsv(eeg / f"{stem}_channels.tsv")
        event_rows = tsv(eeg / f"{stem}_epochs.tsv")
        array = np.load(payload_eeg / f"{stem}_epochs.npy", mmap_mode="r", allow_pickle=False)
        if len(event_rows) != array.shape[0] or array.shape[1] != len(channel_rows):
            raise ValueError(f"Run {run} header/metadata disagreement")
        if {float(row["zero_time"]) for row in event_rows} != {zero_time}:
            raise ValueError(f"Run {run} event zero differs")
        labels = {row["trial_type"] for row in event_rows}
        if len(labels) != 1 or array.shape[0] < 6:
            raise ValueError(f"Run {run} has mixed label or too few trials")
        indices = [next(i for i, row in enumerate(channel_rows) if row["name"] == name) for name in names]
        times = -zero_time + np.arange(array.shape[-1]) / sfreq
        baseline = (times >= -.20) & (times <= -.05)
        pulse = (times >= -.002) & (times <= .002)
        selected = np.asarray(array[:, indices, :], dtype=np.float64)
        if not np.isfinite(selected).all():
            raise ValueError(f"Run {run} has nonfinite EEG")
        if args.split == "alternating":
            training, testing = selected[::2], selected[1::2]
        else:
            midpoint_trial = len(selected) // 2
            training, testing = selected[:midpoint_trial], selected[midpoint_trial:]
        base = training[:, :, baseline].transpose(1, 0, 2).reshape(len(names), -1)
        count += base.shape[1]
        sum_x += base.sum(axis=1)
        sum_xx += base @ base.T
        cases.append({"run": run, "label": next(iter(labels)), "train": training.mean(axis=0),
                      "test": testing.mean(axis=0), "times": times, "pulse": pulse,
                      "training_trials": len(training), "heldout_trials": len(testing)})
        del selected, array

    reference = np.eye(len(names)) - np.ones((len(names), len(names))) / len(names)
    covariance = (sum_xx - np.outer(sum_x, sum_x) / count) / (count - 1)
    covariance = reference @ covariance @ reference.T
    covariance = .9 * covariance + .1 * np.trace(covariance) / (len(names) - 1) * reference
    values, vectors = np.linalg.eigh((covariance + covariance.T) / 2)
    keep = values > 1e-10 * values.max()
    whitener = vectors[:, keep].T / np.sqrt(values[keep])[:, None]
    rows = []
    methods = ["contact_axis", "fixed_cortical_normal",
               "homogeneous_bipolar_point_source", "free_orientation"]
    if args.layered:
        methods.extend(("layered_bipolar_3", "layered_bipolar_9"))
    residuals_by_model = {key: [] for key in methods}
    for case in cases:
        c1, c2 = contact_names(case["label"])
        midpoint = (contacts[c1] + contacts[c2]) / 2
        offset, vertex = tree.query(midpoint)
        axis_surface = contacts[c2] - contacts[c1]
        axis_head = np.linalg.solve(head_to_surface[:3, :3], axis_surface)
        axis_head /= np.linalg.norm(axis_head)
        train = reference @ case["train"]
        test = reference @ case["test"]
        pulse_indices = np.flatnonzero(case["pulse"])
        sample = int(pulse_indices[np.argmax(np.linalg.norm(train[:, case["pulse"]], axis=0))])
        y_train = whitener @ train[:, sample]
        y_test = whitener @ test[:, sample]
        free_columns = whitener @ reference @ free["sol"]["data"][:, 3 * vertex:3 * vertex + 3]
        fixed_column = whitener @ reference @ fixed["sol"]["data"][:, vertex]
        axis_column = free_columns @ axis_head
        # Infinite homogeneous-volume conductor: a positive and negative
        # monopolar current source at the two contacts. Conductivity and
        # current scale are absorbed by the fitted amplitude. This is an
        # intentionally crude physical comparator, not a realistic head FEM.
        contact_head = mne.transforms.apply_trans(
            np.linalg.inv(head_to_surface), np.vstack((contacts[c1], contacts[c2])))
        bipolar_raw = homogeneous_bipolar_signature(sensor_head, contact_head)
        bipolar_column = whitener @ reference @ bipolar_raw

        predictions = {}
        for name, column in (("contact_axis", axis_column),
                             ("fixed_cortical_normal", fixed_column),
                             ("homogeneous_bipolar_point_source", bipolar_column)):
            amplitude = float((column @ y_train) / (column @ column))
            predicted = amplitude * column
            predictions[name] = score(y_test, predicted)
            predictions[name].update(residual_repeatability(y_train, y_test, predicted))
            predictions[name]["training_amplitude"] = amplitude
            residuals_by_model[name].append(y_test - predicted)
        fitted_orientation, *_ = np.linalg.lstsq(free_columns, y_train, rcond=None)
        predicted = free_columns @ fitted_orientation
        predictions["free_orientation"] = score(y_test, predicted)
        predictions["free_orientation"].update(residual_repeatability(y_train, y_test, predicted))
        residuals_by_model["free_orientation"].append(y_test - predicted)
        predictions["free_orientation"]["angle_to_contact_axis_deg"] = float(np.degrees(np.arccos(
            np.clip(abs(fitted_orientation @ axis_head) / np.linalg.norm(fitted_orientation), 0, 1))))
        if args.layered:
            # The electrode TSV stores surface-RAS coordinates in metres.
            # A previous development run divided these again by 1000; that
            # invalid result is retained with an INVALID_UNITS filename.
            contacts_mri = np.vstack((contacts[c1], contacts[c2]))
            gap_m = float(np.linalg.norm(contacts_mri[1] - contacts_mri[0]))
            if (not .001 <= gap_m <= .02 or
                    not .01 <= np.linalg.norm(contacts_mri.mean(axis=0)) <= .2):
                raise ValueError(f"Implausible contact coordinates/units in run {case['run']}: "
                                 f"gap={gap_m} m")
            for nodes in (3, 9):
                positions, moments_mri = bipolar_line_quadrature(contacts_mri, nodes)
                discrete = mne.setup_volume_source_space(
                    pos={"rr": positions, "nn": np.tile([0.0, 0.0, 1.0], (nodes, 1))},
                    verbose="ERROR")
                layered = mne.make_forward_solution(
                    info, trans=free["mri_head_t"], src=discrete, bem=bem_path,
                    meg=False, eeg=True, mindist=0.0, on_inside="raise", verbose="ERROR")
                if layered["nsource"] != nodes or layered["sol"]["row_names"] != names:
                    raise ValueError(f"Layered forward dropped source points or reordered sensors, run {case['run']}")
                rotation = free["mri_head_t"]["trans"][:3, :3]
                moments_head = moments_mri @ rotation.T
                raw_column = sum(layered["sol"]["data"][:, 3 * i:3 * i + 3] @ moments_head[i]
                                 for i in range(nodes))
                column = whitener @ reference @ raw_column
                amplitude = float((column @ y_train) / (column @ column))
                predicted = amplitude * column
                key = f"layered_bipolar_{nodes}"
                predictions[key] = score(y_test, predicted)
                predictions[key].update(residual_repeatability(y_train, y_test, predicted))
                predictions[key]["training_amplitude"] = amplitude
                residuals_by_model[key].append(y_test - predicted)
        rows.append({"run": case["run"], "condition": case["label"], "training_trials": case["training_trials"],
                     "heldout_trials": case["heldout_trials"], "selected_time_ms": float(case["times"][sample] * 1000),
                     "midpoint_to_grid_mm": float(offset * 1000), "predictions": predictions})

    cross_site_residuals = {}
    for method, residuals in residuals_by_model.items():
        normalized = [vector / np.linalg.norm(vector) for vector in residuals]
        pair_cosines = [float(normalized[i] @ normalized[j])
                        for i in range(len(normalized)) for j in range(i + 1, len(normalized))]
        cross_site_residuals[method] = {"median_signed_cosine": float(np.median(pair_cosines)),
                                        "min_signed_cosine": float(min(pair_cosines)),
                                        "max_signed_cosine": float(max(pair_cosines)),
                                        "site_pairs": len(pair_cosines)}

    result = {"status": "development diagnostic; not held-out participant validation",
              "task": "bipolar stimulation pulse artifact", "participant": SUBJECT,
              "split": f"{args.split} trials; peak time and parameters chosen on training trials only",
              "residual_diagnostic": "signed cosine between train and test whitened residual scalp patterns; descriptive only",
              "cross_site_residual_diagnostic": cross_site_residuals,
              "layered_candidate": {"enabled": args.layered,
                                    "bem": str(bem_path.relative_to(ROOT)) if args.layered else None,
                                    "conductivities_s_per_m": [0.3, 0.006, 0.3] if args.layered else None,
                                    "quadrature_nodes": [3, 9] if args.layered else None},
              "channels": names, "noise_rank": int(keep.sum()), "sites": rows,
              "median_heldout_r2": {method: float(np.median([row["predictions"][method]["heldout_whitened_r2"]
                                                       for row in rows]))
                                    for method in methods},
              "limitations": ["Equivalent dipole at nearest cortical vertex, not a physical bipolar injection solution",
                              "Homogeneous bipolar point-source comparator ignores layered head boundaries and anisotropic tissue conductivity",
                              "Free orientation has three fitted parameters; comparison is descriptive",
                              "Within-run trial halves share participant, site and session; this is not an independent participant test"]}
    output.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite a development result: {destination}")
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "sites": len(rows),
                      "median_heldout_r2": result["median_heldout_r2"]}, indent=2))


if __name__ == "__main__":
    main()
