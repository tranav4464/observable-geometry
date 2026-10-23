from __future__ import annotations

"""Development-only audit of 2 kHz to 200 Hz iEEG resampling.

Reads one real trial from each paired development session (sub-01..03) and
stores only aggregate diagnostics. Reserved participants are never opened.
"""

import csv
import hashlib
import json
from pathlib import Path

import mne
import numpy as np
import scipy
from scipy.signal import freqz, firwin, resample_poly

ROOT = Path("data/track_b/on004752_v1.0.0")
OUT = Path("outputs/track_b/20261023T_b2_preprocessing_contract_audit_v2/resampling_audit.json")


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    # Match SciPy 1.18.1 resample_poly's source-defined default FIR design.
    # half_len = 10 * max(up, down); numtaps = 2 * half_len + 1.
    # For up=1, down=10 this is 201 taps, not 101. The old v1 report
    # incorrectly computed the response of a separate 101-tap filter.
    up_factor, down_factor = 1, 10
    max_rate = max(up_factor, down_factor)
    half_len = 10 * max_rate
    taps = firwin(2 * half_len + 1, 1 / max_rate, window=("kaiser", 5.0))
    freq, response = freqz(taps, worN=32768, fs=2000.0)
    db = 20 * np.log10(np.maximum(np.abs(response), 1e-15))
    bands = {}
    for name, lo, hi in (("0.5_50_hz", 0.5, 50.0), ("90_100_hz", 90.0, 100.0), ("110_200_hz", 110.0, 200.0), ("400_1000_hz", 400.0, 1000.0)):
        sel = (freq >= lo) & (freq <= hi)
        bands[name] = {"min_db": float(db[sel].min()), "max_db": float(db[sel].max()), "mean_db": float(db[sel].mean())}

    results = []
    for sub in ("sub-01", "sub-02", "sub-03"):
        for sess in sorted((ROOT / sub).glob("ses-*")):
            eegdir, idir = sess / "eeg", sess / "ieeg"
            eeg_file = next(eegdir.glob("*_eeg.edf"))
            ieeg_file = next(idir.glob("*_ieeg.edf"))
            eeg_events = next(eegdir.glob("*_events.tsv"))
            ieeg_events = next(idir.glob("*_events.tsv"))
            erow, irow = rows(eeg_events)[0], rows(ieeg_events)[0]
            # Full 8-s trial filtering/resampling before the prespecified [4,6) task crop.
            eb, ee = int(erow["begSample"]) - 1, int(erow["endSample"])
            ib, ie = int(irow["begSample"]) - 1, int(irow["endSample"])
            # The EDF physical-dimension fields are blank; pinned BIDS channels.tsv
            # declares microvolts. Use MNE's explicit override as audited in B2.
            eraw = mne.io.read_raw_edf(eeg_file, preload=False, units="uV", verbose="ERROR")
            iraw = mne.io.read_raw_edf(ieeg_file, preload=False, units="uV", verbose="ERROR")
            try:
                x = eraw.get_data(start=eb, stop=ee)
                z = iraw.get_data(start=ib, stop=ie)
                z200 = resample_poly(z, up=up_factor, down=down_factor, axis=1, window=("kaiser", 5.0), padtype="constant", cval=0.0)
                if x.shape[1] != 1600 or z.shape[1] != 16000 or z200.shape[1] != 1600:
                    raise RuntimeError(f"unexpected epoch shapes for {sub}/{sess.name}")
                # Task crop [4,6) s. Compare filtering on the full trial vs filtering
                # only the crop, to quantify edge handling without saving samples.
                full_crop = z200[:, 800:1200]
                crop_only = resample_poly(z[:, 8000:12000], up=up_factor, down=down_factor, axis=1, window=("kaiser", 5.0), padtype="constant", cval=0.0)
                rel = float(np.linalg.norm(full_crop - crop_only) / max(np.linalg.norm(full_crop), 1e-30))
                results.append({
                    "participant": sub,
                    "session": sess.name,
                    "trial": int(erow["nTrial"]),
                    "eeg_shape": list(x.shape),
                    "ieeg_native_shape": list(z.shape),
                    "ieeg_200hz_shape": list(z200.shape),
                    "task_crop_shape": list(full_crop.shape),
                    "all_finite": bool(np.isfinite(x).all() and np.isfinite(z).all() and np.isfinite(z200).all()),
                    "task_crop_relative_difference_if_resampled_after_crop": rel,
                    "eeg_edf_sha256": sha256(eeg_file),
                    "ieeg_edf_sha256": sha256(ieeg_file),
                })
            finally:
                eraw.close()
                iraw.close()

    report = {
        "run_id": "20261023T_b2_preprocessing_contract_audit_v2",
        "decision": "Does a documented, deterministic polyphase anti-aliasing path produce the correct real-data 200 Hz late-maintenance target, and what paper-fidelity gaps remain?",
        "dataset": "NEMAR on004752 v1.0.0 / OpenNeuro ds004752 v1.0.1",
        "scope": "one real first trial per paired session, development participants sub-01..03 only; no reserved participant events or signal samples opened; no synthetic data; no model fitting",
        "software": {"python_packages": {"mne": mne.__version__, "numpy": np.__version__, "scipy": scipy.__version__}},
        "resampler": {"function": "scipy.signal.resample_poly", "up": up_factor, "down": down_factor, "default_window": "Kaiser beta=5", "fir_taps": int(len(taps)), "firwin_normalized_cutoff": 1 / max_rate, "sampling_rate_hz": 2000.0, "task_crop": "[4,6) seconds from trial onset, after resampling the full 8-second trial", "filter_response_db": bands},
        "session_count": len(results),
        "all_pass": len(results) == 14 and all(r["all_finite"] and r["ieeg_200hz_shape"][1] == 1600 and r["task_crop_shape"][1] == 400 for r in results),
        "mean_relative_difference_from_crop_only_filtering": float(np.mean([r["task_crop_relative_difference_if_resampled_after_crop"] for r in results])),
        "max_relative_difference_from_crop_only_filtering": float(np.max([r["task_crop_relative_difference_if_resampled_after_crop"] for r in results])),
        "paper_fidelity_findings": {
            "paper_explicitly_specifies": ["sym4 three-level DWT denoising; MAD-based universal threshold on detail coefficients", "zero-phase anti-alias low-pass before iEEG downsampling to 200 Hz", "1-second windows and segment-wise z-score normalization", "frequency evaluation primarily in 0.5-50 Hz"],
            "paper_does_not_fully_specify": ["numeric anti-alias cutoff/transition/attenuation and exact filter coefficients", "exact polyphase routine and boundary handling", "how denoising interacts with trial/window splits and the timing of the sliding windows", "how a segment-wise normalized prediction is converted to physical units without target segment mean/scale"],
            "implication": "This audit verifies a transparent common-grid adaptation, not exact NeuroFlowNet preprocessing reproduction. The model contract must define a fixed target transform and report the endpoint as denoised/band-limited if target-derived denoising is used; physical-amplitude recovery cannot be claimed from segment-z-scored targets unless scale is inferred without test targets.",
        },
        "sessions": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "sessions": len(results), "all_pass": report["all_pass"], "mean_task_crop_relative_edge_difference": report["mean_relative_difference_from_crop_only_filtering"], "max_task_crop_relative_edge_difference": report["max_relative_difference_from_crop_only_filtering"], "reserved_participants_opened": False, "synthetic_data_used": False, "model_fitted": False}, indent=2))


if __name__ == "__main__":
    main()
