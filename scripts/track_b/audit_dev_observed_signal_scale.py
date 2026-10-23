"""Summarize real development-recording scales by task phase; no model fit or synthetic data."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import mne
import numpy as np
import scipy
from scipy.signal import resample_poly


ROOT = Path("data/track_b/on004752_v1.0.0")
OUT = Path("outputs/track_b/20261023T231500Z_b2_observed_signal_scale_audit_v3/signal_scale_audit.json")


def read_events(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def assert_bids_microvolt_units(path: Path, channel_names: list[str]) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        table = list(csv.DictReader(f, delimiter="\t"))
    if [row["name"] for row in table] != channel_names:
        raise RuntimeError(f"EDF channel order does not match {path}")
    accepted = {"μV", "µV", "uV"}
    bad = [(row["name"], row.get("units")) for row in table if row.get("units") not in accepted]
    if bad:
        raise RuntimeError(f"Channel units are missing or not microvolts in {path}: {bad[:3]}")


def assert_edf_dimensions_blank(path: Path) -> None:
    with path.open("rb") as f:
        fixed = f.read(256)
        if len(fixed) != 256:
            raise RuntimeError(f"Truncated EDF fixed header: {path}")
        header_bytes = int(fixed[184:192].decode("ascii").strip())
        n_signals = int(fixed[252:256].decode("ascii").strip())
        f.seek(0)
        header = f.read(header_bytes)
    unit_start = 256 + n_signals * (16 + 80)
    units = [header[unit_start + 8 * i : unit_start + 8 * (i + 1)].decode("ascii").strip()
             for i in range(n_signals)]
    if len(units) != n_signals or any(units):
        raise RuntimeError(f"Expected blank EDF physical-dimension fields in {path}: {units[:3]}")


def quantiles(values: list[float]) -> dict[str, float]:
    a = np.asarray(values, dtype=np.float64)
    return {
        "q05_uv": float(np.quantile(a, 0.05)),
        "median_uv": float(np.quantile(a, 0.50)),
        "q95_uv": float(np.quantile(a, 0.95)),
    }


def main() -> None:
    rows: dict[str, dict[str, dict[str, list[float]]]] = {}
    trial_counts: dict[str, int] = {}
    pair_count = 0
    for subject in ("sub-01", "sub-02", "sub-03"):
        rows[subject] = {
            mod: {phase: [] for phase in ("fixation_0_1s", "maintenance_4_6s")}
            for mod in ("eeg", "ieeg")
        }
        trial_counts[subject] = 0
        for session in sorted((ROOT / subject).glob("ses-*")):
            eeg_dir, ieeg_dir = session / "eeg", session / "ieeg"
            eeg_edfs, ieeg_edfs = list(eeg_dir.glob("*.edf")), list(ieeg_dir.glob("*.edf"))
            eeg_tables, ieeg_tables = list(eeg_dir.glob("*_events.tsv")), list(ieeg_dir.glob("*_events.tsv"))
            if any(len(paths) != 1 for paths in (eeg_edfs, ieeg_edfs, eeg_tables, ieeg_tables)):
                raise RuntimeError(f"Expected one paired EDF and event file in {session}")
            eeg_events, ieeg_events = read_events(eeg_tables[0]), read_events(ieeg_tables[0])
            if len(eeg_events) != len(ieeg_events):
                raise RuntimeError(f"Paired event counts differ in {session}")
            assert_edf_dimensions_blank(eeg_edfs[0])
            assert_edf_dimensions_blank(ieeg_edfs[0])
            eeg_raw = mne.io.read_raw_edf(eeg_edfs[0], preload=False, units="uV", verbose="ERROR")
            ieeg_raw = mne.io.read_raw_edf(ieeg_edfs[0], preload=False, units="uV", verbose="ERROR")
            try:
                assert_bids_microvolt_units(eeg_dir / eeg_edfs[0].name.replace("_eeg.edf", "_channels.tsv"), eeg_raw.ch_names)
                assert_bids_microvolt_units(ieeg_dir / ieeg_edfs[0].name.replace("_ieeg.edf", "_channels.tsv"), ieeg_raw.ch_names)
                if float(eeg_raw.info["sfreq"]) != 200.0 or float(ieeg_raw.info["sfreq"]) != 2000.0:
                    raise RuntimeError(f"Unexpected sample rate in {session}")
                for er, ir in zip(eeg_events, ieeg_events):
                    if er["nTrial"] != ir["nTrial"] or er["SetSize"] != ir["SetSize"]:
                        raise RuntimeError(f"Paired trial identity differs in {session}")
                    if er.get("Artifact") == "1" or ir.get("Artifact") == "1":
                        continue
                    eeg_start, eeg_stop = int(er["begSample"]) - 1, int(er["endSample"])
                    ieeg_start, ieeg_stop = int(ir["begSample"]) - 1, int(ir["endSample"])
                    # EDF physical-dimension strings are blank; the BIDS channel table declares μV.
                    # Tell MNE the stored units explicitly; get_data returns SI volts, converted here to μV.
                    eeg = eeg_raw.get_data(start=eeg_start, stop=eeg_stop) * 1e6
                    ieeg = ieeg_raw.get_data(start=ieeg_start, stop=ieeg_stop) * 1e6
                    if eeg.shape[1] != 1600 or ieeg.shape[1] != 16000:
                        raise RuntimeError(f"Trial is not an 8-second epoch in {session}")
                    eeg50 = resample_poly(eeg, up=1, down=4, axis=1)
                    ieeg50 = resample_poly(ieeg, up=1, down=40, axis=1)
                    if eeg50.shape[1] != 400 or ieeg50.shape[1] != 400:
                        raise RuntimeError(f"Resampled trial is not 400 points in {session}")
                    for modality, signal in (("eeg", eeg50), ("ieeg", ieeg50)):
                        for phase, slc in (("fixation_0_1s", slice(0, 50)), ("maintenance_4_6s", slice(200, 300))):
                            phase_data = signal[:, slc]
                            if not np.isfinite(phase_data).all():
                                raise RuntimeError(f"Non-finite data in {session}, trial {er['nTrial']}")
                            rows[subject][modality][phase].extend(np.std(phase_data, axis=1, ddof=1).tolist())
                    trial_counts[subject] += 1
                pair_count += 1
            finally:
                eeg_raw.close()
                ieeg_raw.close()

    summaries = {
        subject: {
            modality: {
                phase: {"channel_trial_count": len(values), **quantiles(values)}
                for phase, values in phases.items()
            }
            for modality, phases in modalities.items()
        }
        for subject, modalities in rows.items()
    }
    report = {
        "run_id": "20261023T231500Z_b2_observed_signal_scale_audit_v3",
        "dataset": "NEMAR on004752 v1.0.0 / OpenNeuro ds004752",
        "purpose": "Check the observed microvolt scale of actual development recordings so WBEN's undocumented noise scale mapping is not guessed.",
        "scope": "Real, artifact-unflagged event epochs from development-only sub-01 through sub-03; no confirmation participant files opened.",
        "paired_session_count": pair_count,
        "artifact_unflagged_trial_counts": trial_counts,
        "sample_rate_hz": {"eeg": 200, "ieeg": 2000, "common_grid": 50},
        "phase_windows_at_50hz": {"fixation_0_1s": "[0:50]", "maintenance_4_6s": "[200:300]"},
        "summary_statistic": "Per channel and trial temporal sample standard deviation after default scipy.signal.resample_poly, in microvolts; quantiles aggregate channel-trial values within participant/modality/phase.",
        "unit_crosswalk": "EDF physical-dimension fields are blank and paired channels.tsv declares μV for every channel. MNE read_raw_edf is called with units='uV'; returned SI volt values are converted to μV for the summary.",
        "results": summaries,
        "software": {"mne": mne.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
        "mne_edf_unit_override": "uV, verified against the official read_raw_edf units argument for missing EDF units",
        "synthetic_data_used": False,
        "model_fit_performed": False,
        "confirmation_outcomes_accessed": False,
        "signal_values_saved": False,
        "interpretation_limit": "These are observed biological-plus-instrument recording scales, not estimates of sensor measurement noise. They cannot validate WBEN's assumed noise standard deviations or determine the correct observation covariance.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=False)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "paired_sessions": pair_count, "unflagged_trials": trial_counts, "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
