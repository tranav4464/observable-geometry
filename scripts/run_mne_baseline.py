"""Run a conventional fixed-orientation MNE minimum-norm comparison."""
from pathlib import Path
import json
import sys
import numpy as np
import mne

ROOT = Path(__file__).resolve().parents[1]
from tracka_paths import OUT


def main():
    with np.load(OUT / "prepared_bundle.npz", allow_pickle=False) as b:
        data, covariance = b["data"], b["noise_cov_single_trial"]
    meta = json.loads((OUT / "prepared_bundle.json").read_text(encoding="utf-8"))
    case = json.loads((OUT / "case_validation.json").read_text(encoding="utf-8"))
    sfreq = float(case["sampling_rate_hz"])
    tmin = float(case["epoch_range_s"][0])
    fwd_path = ROOT / "data/payload/derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif"
    fwd = mne.read_forward_solution(fwd_path, verbose=False)
    fwd = mne.pick_channels_forward(fwd, include=meta["channel_names"], ordered=True,
                                    copy=True, verbose=False)
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True,
                                       use_cps=True, verbose=False)
    info = mne.create_info(meta["channel_names"], sfreq, ch_types="eeg")
    evoked = mne.EvokedArray(data, info, tmin=tmin, verbose=False)
    evoked.nave = int(meta["averaging_count"])
    evoked.set_eeg_reference(ref_channels="average", projection=True, verbose=False)
    info = evoked.info
    noise_cov = mne.Covariance(covariance, meta["channel_names"], [], info["projs"],
                               nfree=meta["baseline_degrees_of_freedom"], method="empirical", verbose=False)
    inverse = mne.minimum_norm.make_inverse_operator(
        info, fwd, noise_cov, loose=0.0, depth=None, fixed=True,
        rank="info", verbose=False)
    stc = mne.minimum_norm.apply_inverse(
        evoked, inverse, lambda2=1.0/9.0, method="MNE", pick_ori=None, verbose=False)
    times = evoked.times
    pre = np.flatnonzero(times < 0)[::max(1, int(np.sum(times < 0) / 18))]
    post = np.flatnonzero(times >= 0)[::max(1, int(np.sum(times >= 0) / 32))]
    frame_indices = np.unique(np.r_[pre, post, len(times)-1]).astype(int)
    np.savez_compressed(OUT / "mne_minimum_norm_preview.npz",
                        frame_indices=frame_indices, times=times[frame_indices],
                        source=stc.data[:, frame_indices])
    summary = {
        "status": "conventional source-imaging baseline computed",
        "method": "MNE minimum norm (MNE), fixed cortical orientation",
        "settings": {"loose": 0.0, "depth_weighting": None, "lambda2": 1.0/9.0,
                     "noise_covariance": "pooled single-trial baseline covariance; MNE scales it by the Evoked nave",
                     "reference": "average EEG reference projector; same selected channel order"},
        "n_channels": int(data.shape[0]), "n_sources": int(stc.data.shape[0]),
        "displayed_time_frames": int(len(frame_indices)),
        "limitations": ["Map is illustrative for an epoch containing an intracranial stimulation pulse.",
                        "No source-location accuracy can be evaluated from this single event.",
                        "MNE was selected as a conventional visual comparator; no hyperparameter tuning was performed."],
    }
    (OUT / "mne_minimum_norm.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
