"""Audit real development trial windows for finite/constant EEG and iEEG data."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import mne
import numpy as np
import scipy
from scipy.signal import resample_poly


SUBJECTS = ("sub-01", "sub-02", "sub-03")
MICROVOLT_UNITS = {"μV", "µV", "uV"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def verify_channel_units(path: Path, channel_names: list[str]) -> None:
    rows = read_tsv(path)
    if [row.get("name") for row in rows] != channel_names:
        raise ValueError(f"Channel order differs between EDF and channels.tsv: {path}")
    bad = [(row.get("name"), row.get("units")) for row in rows
           if row.get("units") not in MICROVOLT_UNITS]
    if bad:
        raise ValueError(f"Missing or non-microvolt channel units in {path}: {bad[:5]}")


def summary(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "q05_uv": float(np.quantile(array, 0.05)),
        "median_uv": float(np.quantile(array, 0.50)),
        "q95_uv": float(np.quantile(array, 0.95)),
    }


def audit(dataset_root: Path) -> dict[str, Any]:
    stats: dict[str, dict[str, dict[str, Any]]] = {
        subject: {
            modality: {
                "channel_trial_count": 0,
                "nonfinite_channel_trials": 0,
                "zero_variance_channel_trials": 0,
                "std_uv": [],
                "absolute_peak_uv": [],
            }
            for modality in ("eeg", "ieeg")
        }
        for subject in SUBJECTS
    }
    session_count = 0
    eligible_trials = {subject: 0 for subject in SUBJECTS}
    channel_schemas: dict[str, dict[str, list[str]]] = {
        subject: {"eeg": [], "ieeg": []} for subject in SUBJECTS
    }

    for subject in SUBJECTS:
        for session in sorted((dataset_root / subject).glob("ses-*")):
            eeg_dir, ieeg_dir = session / "eeg", session / "ieeg"
            eeg_edf = list(eeg_dir.glob("*_eeg.edf"))
            ieeg_edf = list(ieeg_dir.glob("*_ieeg.edf"))
            eeg_events = list(eeg_dir.glob("*_events.tsv"))
            ieeg_events = list(ieeg_dir.glob("*_events.tsv"))
            if any(len(paths) != 1 for paths in (eeg_edf, ieeg_edf, eeg_events, ieeg_events)):
                raise ValueError(f"Expected one paired EDF/events table in {session}")
            eeg_rows, ieeg_rows = read_tsv(eeg_events[0]), read_tsv(ieeg_events[0])
            if len(eeg_rows) != len(ieeg_rows):
                raise ValueError(f"Paired event counts differ in {session}")

            eeg_raw = mne.io.read_raw_edf(eeg_edf[0], preload=False, units="uV", verbose="ERROR")
            ieeg_raw = mne.io.read_raw_edf(ieeg_edf[0], preload=False, units="uV", verbose="ERROR")
            try:
                verify_channel_units(
                    eeg_dir / eeg_edf[0].name.replace("_eeg.edf", "_channels.tsv"), eeg_raw.ch_names
                )
                verify_channel_units(
                    ieeg_dir / ieeg_edf[0].name.replace("_ieeg.edf", "_channels.tsv"), ieeg_raw.ch_names
                )
                if eeg_raw.info["sfreq"] != 200.0 or ieeg_raw.info["sfreq"] != 2000.0:
                    raise ValueError(f"Unexpected sample rates in {session}")
                for modality, names in (("eeg", eeg_raw.ch_names), ("ieeg", ieeg_raw.ch_names)):
                    if channel_schemas[subject][modality] and channel_schemas[subject][modality] != names:
                        raise ValueError(f"Within-participant {modality} channel schema changed in {session}")
                    channel_schemas[subject][modality] = list(names)

                for eeg_event, ieeg_event in zip(eeg_rows, ieeg_rows):
                    if (eeg_event.get("nTrial") != ieeg_event.get("nTrial")
                            or eeg_event.get("SetSize") != ieeg_event.get("SetSize")):
                        raise ValueError(f"Paired event identity differs in {session}")
                    if eeg_event.get("Artifact") != "0" or ieeg_event.get("Artifact") != "0":
                        continue
                    eeg_start = int(eeg_event["begSample"]) - 1
                    eeg_stop = int(eeg_event["endSample"])
                    ieeg_start = int(ieeg_event["begSample"]) - 1
                    ieeg_stop = int(ieeg_event["endSample"])
                    eeg_epoch = eeg_raw.get_data(start=eeg_start, stop=eeg_stop) * 1e6
                    ieeg_epoch = ieeg_raw.get_data(start=ieeg_start, stop=ieeg_stop) * 1e6
                    if eeg_epoch.shape[1] != 1600 or ieeg_epoch.shape[1] != 16000:
                        raise ValueError(f"Unexpected 8-s epoch shape in {session}, trial {eeg_event['nTrial']}")
                    # Match the declared 200/2000 -> 50-Hz whole-epoch polyphase recipe.
                    eeg50 = resample_poly(eeg_epoch, up=1, down=4, axis=1)
                    ieeg50 = resample_poly(ieeg_epoch, up=1, down=40, axis=1)
                    for modality, signal in (("eeg", eeg50), ("ieeg", ieeg50)):
                        window = signal[:, 200:300]
                        result = stats[subject][modality]
                        finite = np.isfinite(window).all(axis=1)
                        result["nonfinite_channel_trials"] += int((~finite).sum())
                        channel_std = np.std(window, axis=1, ddof=1)
                        result["zero_variance_channel_trials"] += int((channel_std == 0).sum())
                        finite_std = channel_std[np.isfinite(channel_std)]
                        finite_peak = np.max(np.abs(window[finite]), axis=1) if finite.any() else np.array([])
                        result["channel_trial_count"] += len(channel_std)
                        result["std_uv"].extend(finite_std.tolist())
                        result["absolute_peak_uv"].extend(finite_peak.tolist())
                    eligible_trials[subject] += 1
                session_count += 1
            finally:
                eeg_raw.close()
                ieeg_raw.close()

    summarized: dict[str, dict[str, dict[str, Any]]] = {}
    for subject, modalities in stats.items():
        summarized[subject] = {}
        for modality, record in modalities.items():
            summarized[subject][modality] = {
                key: value for key, value in record.items()
                if key not in ("std_uv", "absolute_peak_uv")
            }
            summarized[subject][modality]["std_uv_quantiles"] = summary(record["std_uv"])
            summarized[subject][modality]["absolute_peak_uv_quantiles"] = summary(record["absolute_peak_uv"])

    return {
        "audit_type": "real_development_signal_quality_in_candidate_window",
        "dataset": "NEMAR on004752 v1.0.0 / OpenNeuro ds004752",
        "development_subjects_only": list(SUBJECTS),
        "paired_sessions_read": session_count,
        "artifact_zero_trial_counts": eligible_trials,
        "sample_rates_hz": {"eeg": 200, "ieeg": 2000, "common": 50},
        "candidate_window": {"seconds_from_epoch_start": "[4,6)", "indices_at_50_hz": "[200:300]"},
        "unit_handling": "EDF physical-dimension fields are absent; MNE read_raw_edf receives units='uV' based on paired channels.tsv, and SI volts are converted to microvolts for summaries.",
        "checks": {
            "finite_samples": "Count channel-trial windows with any non-finite value.",
            "zero_variance": "Count channel-trial windows whose sample SD is exactly zero after the candidate resampling recipe.",
            "amplitudes": "Report descriptive sample-SD and absolute-peak quantiles only; no threshold or exclusion is inferred.",
        },
        "channel_schemas": channel_schemas,
        "results": summarized,
        "software": {"mne": mne.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
        "signal_values_saved": False,
        "model_fit_performed": False,
        "confirmation_participants_accessed": [],
        "synthetic_data_created": False,
        "interpretation_limit": "Artifact==0 is the dataset label and is not proof that all artifacts are removed. A finite and nonconstant window does not establish physiological quality, valid acquisition filtering, prediction performance, or correct noise covariance.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.dataset_root)
    for modalities in result["results"].values():
        for record in modalities.values():
            if record["nonfinite_channel_trials"] or record["zero_variance_channel_trials"]:
                raise RuntimeError(f"Candidate quality check failed: {record}")
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite prior result: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "paired_sessions_read": result["paired_sessions_read"],
        "artifact_zero_trial_counts": result["artifact_zero_trial_counts"],
        "quality_counts": {
            subject: {
                modality: {
                    "channel_trial_count": record["channel_trial_count"],
                    "nonfinite_channel_trials": record["nonfinite_channel_trials"],
                    "zero_variance_channel_trials": record["zero_variance_channel_trials"],
                }
                for modality, record in modalities.items()
            }
            for subject, modalities in result["results"].items()
        },
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
