"""Check nominal signature summaries under two reference/covariance choices."""
from pathlib import Path
import csv
import json
import sys
import numpy as np
import mne

ROOT = Path(__file__).resolve().parents[1]
from tracka_paths import OUT
sys.path.insert(0, str(ROOT / "src"))
from observable_geometry.nominal import nearest_distant_signatures


def main():
    meta_root = ROOT / "data/Localize-MI"
    payload = ROOT / "data/payload"
    prefix = "derivatives/epochs/sub-01/eeg/sub-01_task-seegstim_run-01"
    channels = list(csv.DictReader((meta_root / f"{prefix}_channels.tsv").open(encoding="utf-8"), delimiter="\t"))
    events = list(csv.DictReader((meta_root / f"{prefix}_epochs.tsv").open(encoding="utf-8"), delimiter="\t"))
    sfreq = float(channels[0]["sampling_frequency"])
    tmin = -float(events[0]["zero_time"])
    epochs = np.load(payload / f"{prefix}_epochs.npy", mmap_mode="r")
    times = tmin + np.arange(epochs.shape[2]) / sfreq
    good = [r["name"] for r in channels if r["status"] == "good"]
    ids = [next(i for i, row in enumerate(channels) if row["name"] == name) for name in good]
    selected = np.asarray(epochs[:, ids, :])
    fwd = mne.read_forward_solution(payload / "derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif", verbose=False)
    fwd = mne.pick_channels_forward(fwd, include=good, ordered=True, copy=True, verbose=False)
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True, use_cps=True, verbose=False)
    lead = fwd["sol"]["data"]
    coords = np.vstack([s["rr"][s["vertno"]] for s in fwd["src"]])
    baseline = (times >= -.20) & (times <= -.05)
    baseline_data = selected[:, :, baseline].transpose(1, 0, 2).reshape(len(good), -1)
    empirical = np.cov(baseline_data)
    target = np.trace(empirical) / len(good) * np.eye(len(good))
    ref_avg = np.eye(len(good)) - np.ones((len(good), len(good))) / len(good)
    ref_e1 = np.eye(len(good)) - np.ones((len(good), 1)) @ np.eye(len(good))[0:1, :]

    variants = {
        "average_reference_10pct_shrinkage": (ref_avg, .10),
        "single_e1_reference_10pct_shrinkage": (ref_e1, .10),
        "average_reference_50pct_shrinkage": (ref_avg, .50),
    }
    results = {}
    for label, (reference, shrinkage) in variants.items():
        covariance = (1-shrinkage) * empirical + shrinkage * target
        referenced_covariance = reference @ covariance @ reference.T
        referenced_lead = reference @ lead
        result = nearest_distant_signatures(referenced_lead, referenced_covariance, coords,
                                            min_distance_mm=20.0, top_k=1, block_size=256)
        results[label] = {**result["summary"], "reference": "average" if reference is ref_avg else "single electrode e1",
                          "shrinkage_fraction": shrinkage,
                          "noise_rank": int(np.linalg.matrix_rank(referenced_covariance, tol=1e-10*np.linalg.norm(referenced_covariance, 2)))}
    comparison = {
        "status": "single-case nominal sensitivity checks complete",
        "common_settings": {"participant": "sub-01", "run": "run-01", "distant_source_exclusion_mm": 20,
                            "source_space": "fixed-orientation 8,196-vertex cortical mesh",
                            "covariance_source": "pre-event interval -200 to -50 ms, pooled over 38 epochs"},
        "variants": results,
        "limitations": ["Alternative reference and shrinkage settings are sensitivity probes, not justified physical uncertainty distributions.",
                        "One participant and run only; no confidence intervals or population inference.",
                        "A thresholded signature similarity remains nominal and uncalibrated."],
    }
    (OUT / "sensitivity_report.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
