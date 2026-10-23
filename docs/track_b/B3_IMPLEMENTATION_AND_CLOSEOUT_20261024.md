# B3 implementation and closeout

**Status: PASS for the bounded software implementation and one sealed model-only demonstration.** This closes B3's implementation deliverable. It does not authorize or report new EEG signal analysis, model fitting, held-out evaluation, or physiological-source validation. Track A remains sealed.

## What the software does

`src/observable_geometry/track_b/distinguishability.py` implements the frozen B2-GBF-v10 nominal forward-signature score as a reusable API. Inputs are a sensor-by-source leadfield, the matching noise covariance, and one coordinate per source in metres. The API validates shapes, finite values, covariance symmetry and positive-semidefiniteness, supported covariance rank, and leadfield energy outside that support. It whitens in the supported covariance eigenspace, normalizes source signatures, then returns distant candidate indices, float64 absolute cosine scores, unit-whitened-norm profiled residuals, validity, norms, and candidate counts.

`scripts/track_b/run_b3_distinguishability.py` is the runnable real-model entry point. It verifies the Track A artifact hashes against its sealed manifest and uses an explicit runtime key allowlist. The prepared bundle exposes only `leadfield` and `noise_cov`; the signature library exposes only coordinates, vertex IDs, and comparison arrays. The EEG `data` member is never requested or materialized. The command writes to a new run directory and refuses overwrites or output inside the sealed Track A release.

Run from the repository root:

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe scripts\track_b\run_b3_distinguishability.py --run-id 20261024_b3_gbf_tool_v1
```

## Method-to-code trace and adaptations

| Operation | Code/evidence | Status and boundary |
|---|---|---|
| GBFs cortical geometry modes | Pinned upstream `vendor/GBFs/utils/seeg_with_eeg.py`: `get_tria_from_src` and `calc_eig_from_src`; invoked in the sealed Track A path through `scripts/pilot_localize.py` and checked through the content-addressed cache in `scripts/geometry_basis_cache.py`. | Upstream code remains unchanged. Track A used 20 modes per hemisphere for its development integration, rather than the 300-mode paper demonstration. This is an explicit adaptation, not a full paper-benchmark reproduction. |
| GBFs regularized inverse | Upstream `process_evoked` in the same pinned file; Track A parity record is `outputs/tracka_release_20261022_v2/gbfs_parity.json`, with the frozen release manifest and reverse-engineering record. | Same-input implementation parity is documented. It does not establish paper-level benchmark reproduction or localization accuracy. New B3 score is not an output of this inverse. |
| Nominal candidate score | `compute_distinguishability` in `src/observable_geometry/track_b/distinguishability.py`; definition and assumptions in `docs/track_b/B2_GBF_SPEC.md`. | Directly compares vertex-level fixed-orientation leadfield columns. The metric is established prior art and no novel-method claim is made. |
| Real-model command, provenance, and output | `scripts/track_b/run_b3_distinguishability.py`; output manifest and access log under `outputs/track_b/20261024_b3_gbf_tool_v1/`. | Runs only on sealed model and comparison arrays. No EEG samples, labels, or new participant outcomes are accessed. |

The project adaptation choices that condition the real case are documented in the frozen B2 specification and Track A metadata: fixed cortical-normal orientation with MNE patch statistics, common-average reference, the declared covariance estimate and shrinkage, Euclidean 20 mm spatial exclusion, top-five reporting, and one participant-specific model. The pair score does not use the GBFs eigenbasis or inverse operator. These workflows are related through the same forward-model provenance but answer different mathematical questions.

## Verification evidence

The B3 run in `outputs/track_b/20261024_b3_gbf_tool_v1/` completed successfully. It read 8,196 source columns over 236 channels; covariance support rank was 235. All 8,196 signatures had an eligible distant alternative. The float64 implementation matched Track A's candidate ordering, valid-source mask, and eligible-candidate counts exactly. The maximum absolute difference from Track A's stored float32 scores was `2.980014734976777e-08`, within the frozen `1e-7` tolerance. Whitened norms passed `rtol=1e-8`, `atol=1e-15`.

Six focused tests pass. They cover analytic orthogonal and polarity/amplitude-equivalent signatures, residual endpoints, stable tie breaking, covariance global-scale invariance, invalid covariance cases, and refusal to discard leadfield components outside covariance support. The analytic arrays are software fixtures, not simulated neural data. The full repository suite and gate register validator are recorded after this closeout.

The access log contains only allowed key reads: `leadfield`, `noise_cov`, `source_coordinates`, `vertex_ids`, `candidate_indices`, `absolute_cosine`, `valid_source`, `whitened_norm`, and `distant_candidate_count`. No `data` key was accessed. This process-level guard is an accidental-access safeguard, not an operating-system security boundary.

The descriptive real-model summary is conditional on the selected model and covariance: median best distant absolute cosine `0.915556984605132`, 90th percentile `0.9453457802989496`, and 6.04% of valid sources had a best distant match at or above `0.95`; none reached `0.99`. These values are nominal geometry summaries, not source-recovery rates, probabilities, or physiological findings.

An additional model-only sensor-montage sensitivity check projects the same sealed leadfield and covariance from the 236-channel contract to the actual 224-channel all-run common subset. The full model first reproduces the sealed B3 output; under the subset, per-source best-similarity ranks have Spearman `rho=0.9958`, the top candidate is retained for 93.36% of source rows, and mean top-five Jaccard overlap is 0.9236. The median best-similarity change is `+0.000132`. This is descriptive robustness evidence for one model and one channel subset, not empirical localization validation or a population estimate. See `B3_MONTAGE_SENSITIVITY_20261024.md` and its hash-verified run output.

## What remains outside B3

B3 does not show that the diagnostic improves analyst decisions. B4/B7 own matched comparisons and decision-value evaluation. It does not establish generalization beyond this one model or participant. The B2 reviewer’s approval covered the registered CPU64 parity recomputation; this B3 software demonstration is separately within the broader project build request and did not perform new EEG analysis. The reviewer’s malformed verifier-hash transcription is retained in the B2 closeout; the locally computed hash is the authoritative implementation identity.
