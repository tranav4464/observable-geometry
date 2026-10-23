# Track A Foundation Protocol

> **Frozen Track A record.** This protocol and its planned follow-on research language document the sealed foundation experiment. The active Track B route was subsequently narrowed to the GBFs software build; see [`track_b/PROJECT_DEFINITION.md`](track_b/PROJECT_DEFINITION.md) and [`track_b/GATE_REGISTER.json`](track_b/GATE_REGISTER.json).

**Version 1.1 | Frozen for the first development case and Track A evaluation | 22 October 2026**

## Purpose and claim boundary

Track A establishes a reproducible GBFs-based source-reconstruction workflow and measures how similar candidate cortical sources look in scalp sensor space under one participant-specific forward model. It is an engineering and mathematical foundation. It is not a new validated inverse solution, a calibrated source-localization method, or evidence that EEG uniquely identifies brain activity.

The central estimand is the **nominal noise-whitened topographic similarity** between two focal cortical source columns, allowing unknown amplitude and polarity, given the supplied subject-specific leadfield, average reference, and evoked noise covariance. We ask whether distinct source locations can yield nearly the same predicted scalp pattern under those assumptions.

## Data and case selection

- Dataset: Localize-MI, metadata snapshot `d7a123d3067213281f106b343c71f28c30e4dd60`, CC-BY-NC-SA 4.0.
- Development case: participant `sub-01`, run `run-01`, selected before inspecting the new ambiguity scores.
- EEG: 38 recorded epochs, 236 good channels after channel-status filtering, 8 kHz, epoch −250 ms to +10 ms.
- Event: metadata specify intracranial bipolar stimulation of K13–K14 at 1 mA.
- Anatomy: supplied participant forward solution with 8,196 fixed-orientation cortical source vertices and 20 GBF geometric modes per hemisphere.
- The dataset authors define the midpoint of K13/K14 as the stimulation-site reference for pulse-artifact localization. After applying the recorded head-to-surface transform, the pair is 3.22 mm apart; the midpoint is 1.88 mm from the nearest modeled cortical vertex (K13 and K14 individually are 0.82 mm and 0.92 mm from their nearest source vertices). These grid offsets are reported as approximation error, not as failure of the known stimulation-site reference. The contact pair is not ground truth for a distributed physiological response.

This single run is a development/integration example, not a held-out validation participant. Track A's frozen empirical task is localization of the known intracranial pulse artifact, the task for which the dataset provides stimulation-contact ground truth. It does not validate localization of the physiological response after stimulation. Reconstructed activity from the full epoch is displayed to demonstrate the pipeline and viewer.

## Preprocessing and fixed choices

Channels are aligned by name to the forward solution, bad channels are excluded, and the data, leadfield, and covariance receive the same average-reference projection. The event epoch metadata provide the time axis and sampling rate. A pooled pre-event interval from −200 ms to −50 ms estimates channel noise; 10% diagonal shrinkage is used to stabilize covariance estimation. For an evoked average of 38 trials, this covariance is divided by 38 under an independent-trials assumption. That assumption is not tested in this one-case foundation run and is a sensitivity item for later research.

GBFs uses 20 surface geometric modes per hemisphere for this participant. The linear-Gaussian comparison uses an isotropic mode-space prior scaled by the median nonzero singular value. Both the mode count and prior scale are declared development choices, not optimized or calibrated hyperparameters. The original upstream GBFs recorded-data routine is executed separately and its output is retained with its native scale.

## Nominal ambiguity calculation

For source candidate `i`, let `g_i` be the corresponding leadfield column and `C` the evoked noise covariance after average reference. Whiten and normalize each sensor pattern:

`u_i = C^(-1/2) g_i / ||C^(-1/2) g_i||`.

For each cortical vertex, search for its most similar source signatures at least 20 mm away in the supplied surface coordinates. Similarity is:

`rho_ij = |u_i^T u_j|`.

The absolute value profiles out polarity; normalization profiles out amplitude. For unit whitened signal amplitude, the remaining residual after fitting an alternative amplitude is `sqrt(1 - rho_ij^2)`. A high `rho` means the nominal model predicts similar scalp topographies for these two locations. It does not mean that the brain actually used either source, nor does it provide a calibrated probability or spatial confidence interval.

All 8,196 source vertices are evaluated in memory-bounded blocks. The deliverable stores the top five alternatives per vertex, the nearest distant matches, source coordinates and IDs, validity flags, and summary statistics. The 20 mm exclusion prevents the reported ambiguity headline from merely reflecting immediately adjacent mesh vertices; results depend on this chosen distance threshold.

## GBFs implementation audit and execution

The untouched GBFs checkout is pinned at `99fc7c6e8afbd2e3e68a700c5f1fa1483b90f49e`. The Localize-MI analysis-code checkout is pinned at `1bfed2384b523c8ffcc98b09faad3e94b3e0b138`. Participant-specific geometric modes are computed from the supplied source meshes; the unchanged upstream `calc_eig_from_src` and `process_evoked` functions are extracted and run without importing unrelated demos. A separate conditional linear-Gaussian solver supplies uncertainty conditional on its prior and noise model.

The unchanged GBFs output was independently re-evaluated from the saved data, forward, basis, covariance, eigenvalues and `Lambda=1.2`; relative Frobenius difference was `2.23e-13` (maximum absolute difference `2.82e-12`). The independent implementation uses a direct linear solve where upstream explicitly forms a matrix inverse. This is an algebraic parity check on the same Localize-MI inputs, not reproduction of the GBFs paper's reported benchmark. The conditional posterior's source standard deviation is amplitude uncertainty under the stated prior, not localization uncertainty.

A conventional fixed-orientation MNE minimum-norm estimate is also generated with `lambda2=1/9`, no depth weighting, the same average-referenced channel set and evoked noise covariance. It is a visual and implementation comparator only; no source truth in this event supports an accuracy ranking. The MNE map is shown at the same 60 review time points.

The MNE resolution comparison uses its inverse kernel applied to the same forward matrix (`K L`) to obtain source point-spread functions. It summarizes peak-location offset and the spatial spread of each absolute point-spread response. This is a model-derived resolution matrix diagnostic, not measured localization accuracy. Sensitivity runs compare the default 10% covariance shrinkage and average reference with a single-electrode `e1` reference, then with 50% shrinkage under average reference.

## Outputs

- `outputs/localize_sub01_run01/foundation_report.html`: self-contained, offline point-cloud viewer, time selector, reconstruction selector, and ambiguity summary.
- `foundation_report.json`: protocol, provenance hashes, key summary statistics, limitations, and top source pairs.
- `gbfs_parity.json`: independent algebraic check against the unmodified GBFs output.
- `mne_minimum_norm.json` and `mne_minimum_norm_preview.npz`: standard inverse comparator settings and 60 viewer maps.
- `mne_resolution_report.json` and `mne_resolution_summary.npz`: source point-spread/resolution-matrix summaries for MNE minimum norm.
- `sensitivity_report.json`: nominal ambiguity summaries under the three frozen reference/covariance variants.
- `nominal_signature_library.npz`: top five distant signature matches for all source vertices plus coordinates and IDs.
- `nominal_ambiguity_pairs.csv`: 20 highest-similarity unique distant pairs.
- `prepared_bundle.npz`, `recorded_estimates.npz`, and `basis_20_per_hemisphere.npz`: local, non-redistributable-data-dependent computation products; do not publish with the dataset files.
- `report.json` and `prepared_bundle.json`: original integration manifest and input contract.

The dashboard normalizes every displayed map frame separately so that spatial patterns remain visible. It cannot be used to compare map amplitude across time or methods.

## Reproduction and acceptance checks

Run `scripts/run_foundation.ps1` from PowerShell in this directory. It verifies required payload files, runs mathematical tests, executes the recorded-data GBFs and conditional baseline, checks independent GBFs parity, runs MNE minimum norm, computes the nominal signature library and checks report consistency. The environment is Python 3.12 with the exact package pins in `requirements-foundation.txt`.

Acceptance for this Foundation release means: all tests pass; the upstream recorded-data path returns finite output; the conditional solver and forward signatures are finite; all 8,196 vertices have valid signatures and a distant alternative; summary statistics lie in [0,1]; metadata and channel dimensions agree; and the offline report and machine-readable provenance exist. Acceptance does not imply source-localization accuracy or a successful biological validation study.

## Current development-case result

For sub-01/run-01, all 8,196 source vertices had a valid sensor signature and a candidate at least 20 mm away. With noise whitening, the median best distant absolute cosine was 0.916; the 90th percentile was 0.945; 6.04% of source vertices had at least one such alternative with similarity of 0.95 or higher; none reached 0.99. Without noise weighting, the corresponding median was 0.961, the 90th percentile 0.977 and 74.89% had a match at or above 0.95. The strongest noise-whitened pair had similarity 0.972 at a separation of 20.45 mm. This difference shows that sensor-noise weighting materially changes which patterns appear similar in this model. It does not establish that either metric is calibrated or that one better predicts biological localization.

Under the two reference operators, the reported median and 90th-percentile whitened cosines were identical to the displayed precision (0.916 and 0.945) when the data, leadfield and covariance were transformed consistently. Raising diagonal shrinkage from 10% to 50% changed those figures to 0.925 and 0.950, and raised the fraction above 0.95 from 6.04% to 9.98%. Under the selected MNE inverse, the median peak offset was 17.96 mm (90th percentile 36.56 mm); median absolute-response weighted distance was 42.73 mm and median point-spread L1 mass within 10 mm was 3.41%. These are all one-case nominal diagnostics. They motivate a Track B calibration study; they are not population-level results or proof that a new framework is needed.

## Deferred work

Track B must establish prior-art novelty, plausible forward-model uncertainty, nuisance handling, calibration and held-out participant evaluation. Track A does not establish a cross-participant or experimental recovery claim, and it does not complete the proposed Recoverable Source Geometry research framework.

## Track A multi-site artifact evaluation

The primary development evaluation uses six distinct 1 mA sites from sub-01 (runs 1, 3, 5, 6, 8 and 10), with a common set of 224 good channels. It applies the dataset-aligned −2 to +2 ms window, 300 GBF modes per hemisphere at Lambda 1.2, and a fixed-orientation MNE minimum-norm comparator at lambda²=1/9. The five same-site 5 mA runs are a secondary current-sensitivity check. No settings are tuned on the known target locations. All eleven runs are from the same participant and remain development data.

Across the six primary sites, GBFs median/mean peak error was 19.76/19.96 mm; MNE median/mean was 28.30/27.16 mm. Across 15 dependent pairs, predicted and observed sensor-pattern similarity had Pearson r=0.345 and Spearman rho=0.343. These are descriptive only. The measured pulse artifact is not a physiological source map, and these values do not validate a recoverability score or rank methods. Full per-site results and current sensitivity are in `outputs/tracka_verified_20261022_final/empirical_evaluation_report.html` and `.json`.

Track A is verified as an engineering and exploratory foundation. The next phase may investigate the falsifiable question of whether nominal signatures predict empirical confusion under plausible forward-model and nuisance variation. Track B's novelty gate remains open until the closest methods are compared at equation level and the proposed quantity is calibrated on participant-held-out data.
