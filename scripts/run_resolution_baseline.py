"""Compute source point-spread summaries for the MNE minimum-norm inverse."""
from pathlib import Path
import json
import sys
import time
import numpy as np
import mne

ROOT = Path(__file__).resolve().parents[1]
from tracka_paths import OUT


def main():
    start_time = time.perf_counter()
    with np.load(OUT / "prepared_bundle.npz", allow_pickle=False) as b:
        lead, cov = b["leadfield"], b["noise_cov"]
    with np.load(OUT / "recorded_estimates.npz", allow_pickle=False) as e:
        coordinates = e["source_coordinates"]
    meta = json.loads((OUT / "prepared_bundle.json").read_text(encoding="utf-8"))
    names = meta["channel_names"]
    fwd = mne.read_forward_solution(
        ROOT / "data/payload/derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif",
        verbose=False)
    fwd = mne.pick_channels_forward(fwd, include=names, ordered=True, copy=True, verbose=False)
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True,
                                       use_cps=True, verbose=False)
    case = json.loads((OUT / "case_validation.json").read_text(encoding="utf-8"))
    info = mne.create_info(names, float(case["sampling_rate_hz"]), ch_types="eeg")
    dummy = mne.EvokedArray(np.zeros((len(names), 1)), info, tmin=0, verbose=False)
    dummy.set_eeg_reference(ref_channels="average", projection=True, verbose=False)
    info = dummy.info
    noise_cov = mne.Covariance(cov, names, [], info["projs"],
                               nfree=meta["averaging_count"], method="empirical", verbose=False)
    inverse = mne.minimum_norm.make_inverse_operator(
        info, fwd, noise_cov, loose=0.0, depth=None, fixed=True,
        rank="info", verbose=False)
    # Applying the same inverse to sensor identity columns constructs its kernel
    # while preserving MNE's own projections, whitening and source convention.
    impulses = mne.EvokedArray(np.eye(len(names)), info, tmin=0, verbose=False)
    kernel = mne.minimum_norm.apply_inverse(
        impulses, inverse, lambda2=1.0/9.0, method="MNE", pick_ori=None,
        verbose=False).data
    if kernel.shape != (len(coordinates), len(names)):
        raise ValueError("MNE inverse kernel and focal source dimensions disagree")

    n = len(coordinates)
    peak_error = np.empty(n, dtype=np.float32)
    mean_spread = np.empty(n, dtype=np.float32)
    local_energy_10mm = np.empty(n, dtype=np.float32)
    peak_offset = np.empty(n, dtype=np.float32)
    diagonal_fraction = np.empty(n, dtype=np.float32)
    indices = np.arange(n)
    block = 128
    for start in range(0, n, block):
        stop = min(start + block, n)
        psf = np.abs(kernel @ lead[:, start:stop])
        total = psf.sum(axis=0)
        if (total <= 0).any() or not np.isfinite(psf).all():
            raise ValueError("invalid MNE point-spread response")
        peaks = np.argmax(psf, axis=0)
        dxyz = coordinates[:, None, :] - coordinates[None, start:stop, :]
        distances = np.linalg.norm(dxyz, axis=2)
        peak_error[start:stop] = distances[peaks, np.arange(stop-start)] * 1000
        mean_spread[start:stop] = (psf * distances).sum(axis=0) / total * 1000
        local_energy_10mm[start:stop] = (psf * (distances <= .010)).sum(axis=0) / total
        max_response = psf.max(axis=0)
        diagonal = psf[indices[start:stop], np.arange(stop-start)]
        diagonal_fraction[start:stop] = diagonal / np.maximum(max_response, np.finfo(float).tiny)
        peak_offset[start:stop] = psf[peaks, np.arange(stop-start)] / total

    summary = {
        "status": "nominal MNE resolution-matrix / point-spread comparison computed",
        "method": "MNE minimum norm, fixed orientation, lambda2=1/9, no depth weighting",
        "source_count": int(n), "channel_count": int(lead.shape[0]),
        "reference": "average EEG projector", "noise_covariance": "same evoked covariance as nominal signatures",
        "median_peak_location_error_mm": float(np.median(peak_error)),
        "p90_peak_location_error_mm": float(np.quantile(peak_error, .9)),
        "fraction_peak_within_10mm": float(np.mean(peak_error <= 10)),
        "median_absolute_psf_weighted_distance_mm": float(np.median(mean_spread)),
        "median_psf_l1_mass_within_10mm": float(np.median(local_energy_10mm)),
        "median_diagonal_to_peak_response_ratio": float(np.median(diagonal_fraction)),
        "interpretation": "Nominal inverse resolution summary under this one forward model and regularization; not empirical localization accuracy or calibrated uncertainty.",
        "runtime_seconds": time.perf_counter() - start_time,
    }
    np.savez_compressed(OUT / "mne_resolution_summary.npz", peak_location_error_mm=peak_error,
                        absolute_psf_weighted_distance_mm=mean_spread,
                        psf_l1_mass_within_10mm=local_energy_10mm,
                        diagonal_to_peak_response_ratio=diagonal_fraction,
                        peak_amplitude_fraction=peak_offset)
    (OUT / "mne_resolution_report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
