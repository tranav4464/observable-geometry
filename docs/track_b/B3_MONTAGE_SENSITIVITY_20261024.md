# B3 model-only sensor-montage sensitivity check

**Date:** 24 October 2026
**Disposition:** Descriptive robustness supplement; it does not change B4–B7 gate decisions.
**Question:** How much do the B3 nominal pair rankings and scores change when the same participant-specific forward model is restricted from 236 EEG sensors to the 224 channels retained across the exposed sub-01 runs?

## Design and data boundary

The analysis begins with the sealed 236-channel Track A leadfield and noise covariance. It selects the 224 channel names recorded in the existing all-run common-channel audit, then applies the corresponding common-average-reference projection to both the selected leadfield rows and the selected covariance submatrix. It reuses the same 8,196 fixed-orientation source locations, 20 mm Euclidean exclusion, and top-five candidate rule. The full 236-channel recomputation is first required to reproduce the sealed ranking, valid-source mask, candidate counts, scores, and whitened norms under the B3 tolerances.

Only model arrays, source coordinates and IDs, sealed score-comparison arrays, and the already-recorded channel-intersection metadata are read. The script requests only `leadfield` and `noise_cov` from `prepared_bundle.npz`, plus the required comparison keys from `nominal_signature_library.npz`. It does not access the recorded EEG `data` member or any participant outcome. It writes a new ignored output folder and refuses to overwrite an existing run.

For the subset, let (R) select the 224 sensors and let (P_{224}=I-\mathbf{1}\mathbf{1}^{\mathsf T}/224) impose the common-average reference. The transformed arrays are

\[
L_{224}=P_{224}RL_{236}, \qquad
C_{224}=P_{224}RC_{236}R^{\mathsf T}P_{224}^{\mathsf T}.
\]

This is a deterministic projection of an existing model and covariance. It is not a simulated EEG recording, a new head model, or a simulation of neural activity.

## Results

The full-model parity check passed: the 236-channel recomputation exactly reproduced the stored candidate rankings, validity mask, and candidate counts; score and whitened-norm differences met the registered B3 tolerances. Covariance rank was 235 for the full reference and 223 after the 224-channel projection.

| Summary | 236 channels | 224-channel common subset |
|---|---:|---:|
| Median best distant absolute cosine | 0.915557 | 0.916109 |
| 90th percentile | 0.945346 | 0.945709 |
| Fraction with best cosine ≥ 0.95 | 6.04% | 6.19% |
| Fraction with best cosine ≥ 0.99 | 0% | 0% |

Across 8,196 source rows, the per-source best-similarity rankings had Spearman \(\rho=0.9958\). The exact top alternative was retained for 93.36% of rows. The mean top-five set Jaccard overlap was 0.9236, with median 1.0. The median change in best similarity (224 minus 236 channels) was +0.000132; the 5th–95th percentile range was −0.002237 to +0.005463. The best similarity increased for 57.87% of source rows.

These results indicate that the nominal source-pair summaries are largely stable under this particular channel-quality restriction, while the top alternative changes for 6.64% of source rows. They do not show that the score predicts which source is physiologically active or localized correctly.

## Interpretation and limits

This is one within-participant, model-only comparison. The 224 sensors were retained because they were common across the already exposed sub-01 runs; this is not a standard low-density montage and is not an independent sample. The projected covariance inherits the single model's assumptions and estimates. No EEG measurement was evaluated, no localization error was tested, and no participant-level or population uncertainty can be inferred from the 8,196 spatially dependent vertices.

The check strengthens software robustness evidence for B3 but does not establish forward-model uncertainty robustness, researcher decision value, empirical source distinguishability, or a novel mathematical method. B4 remains pivoted because the available measured outcome is a pulse artifact, and B7 remains pivoted because decision benefit was not tested.

## Reproduction

From the repository root, with NumPy, SciPy, and the project test dependencies installed:

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m pytest -q tests\test_track_b_montage_sensitivity.py
.\.venv\Scripts\python.exe scripts\track_b\audit_b3_sensor_montage_sensitivity.py --run-id 20261024_b3_montage_sensitivity
```

The command writes `sensitivity_report.json`, `run_access_log.json`, and `run_manifest.json` under `outputs/track_b/20261024_b3_montage_sensitivity/`. Input and output hashes, selected/removed channel counts, covariance ranks, baseline parity, and claim limits are recorded in these files.
