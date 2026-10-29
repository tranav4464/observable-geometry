# Observable Geometry: discovery and novelty outcome

**Assessment date:** 29 October 2026\
**Decision:** **PIVOT the novel-method / measured source-recovery claim. Preserve and submit the bounded software build.**\
**Novel method supported:** No\
**Measured neural source recovery established:** No

**Close-prior-art update (29 October 2026):** the targeted primary-source
recheck now includes CANDLE (arXiv:2610.07824) and arXiv:2610.27461v1. These
preprints explicitly use lead-field observable/null-space decompositions;
CANDLE also reports geometry-aware reconstruction and stimulation localization
on the Parmigiani data family. They do not share our source-family
distinguishability estimand, but they further rule out a broad novelty claim
around making EEG observability or null-space structure explicit. They also
raise the empirical comparison bar. The estimand distinction alone does not
change the current outcome because there is still no held-out decision benefit
over direct fitting or matched source-imaging baselines. See
[`CLOSE_PRIOR_ART_RECHECK_20261029.md`](CLOSE_PRIOR_ART_RECHECK_20261029.md).

## Decision in one paragraph

Observable Geometry has substantial reproducible computational work and a bounded measured-data family comparison, but the evidence does not show that its source-family analysis improves a researcher decision over established methods. The most promising held-out WSGZP decision cannot currently be run under a valid participant-specific forward model and locked preprocessing contract. The existing Localize-MI comparison is a one-participant stimulation-pulse-artifact control, not neural source validation. The proposed fixed-area lower-envelope ranking is not yet operational and can collapse to zero whenever any compatible explanation avoids a parcel. Therefore the defensible submission is a **researcher-facing, auditable software contribution with conditional source-family results**, with novelty and neural-source recovery explicitly unclaimed.

**Additional model-only robustness check (29 October):** a threshold-swept comparison of every saved positive-margin tail-closed rank (1–25) against bilateral low-mode and sensor-SVD bases passed independent replay for all 75 cases. The candidate reaches higher maximum rank at the retrospective 1% and 2% normalized-margin cuts (18/16 versus 16/14 for sensor-SVD), but ties sensor-SVD at 5% and 10% (11/8). Because the selector is optimized for this margin, ranks and cuts were inspected after the frontier, and the experiment uses one shifted-FEM prior on one participant model, these results do not establish novelty or researcher decision value. See `TAIL_CLOSED_NOVELTY_FALSIFICATION_20261029.md` and `research/gbf_omitted_activity_20261024/TAIL_CLOSED_RANK_MARGIN_SWEEP_PROTOCOL_20261029.md` with fresh replay output `tail_closed_rank_margin_verification_002/result.json`.

**Per-field relative-margin correction (29 October):** the optional tail-closed analysis now also computes the declared relative residual margin using generalized eigenvalues against `B.T @ B`, rather than only the older conservative global-gain denominator. On the same saved one-model operator and a 2,049-point multiplier grid, 28 nominal and 25 error-inflated positive-rank bases passed independent direct-matrix replay with input and code hashes checked. The resulting descriptive robust rank counts at 1%, 2%, 5% and 10% are 22, 21, 19 and 15. These counts cannot be compared as method performance with the legacy 18, 16, 11 and 8 because the margin denominators differ. This is an established generalized-eigenvalue reformulation of the existing bound; it strengthens the software's alignment with its stated estimand but does not establish novelty, physiological validation, or researcher utility. See `TAIL_CLOSED_RELATIVE_FRONTIER_20261029.md` and `outputs/track_b/20261029T_relative_frontier_002/independent_check_001.json`.

**Matched relative-margin baselines (29 October):** under the same operator, error inflation, budget, and grid, all 75 selected/fixed-subspace rows passed independent direct-solve replay. At the descriptive 1%, 2%, 5%, and 10% cuts, the optimized frontier retained ranks 22/21/19/15; sensor-SVD retained 19/19/17/13; bilateral low modes retained none. This is expected because the candidate directly optimizes the same objective. The generalized-eigenvalue method is exactly the direct rank-k subspace optimization at each multiplier, so no distinct algorithmic advantage is established. The result is a bounded representation comparison, not a novel method or measured-data decision benefit. See `outputs/track_b/20261029T_relative_baseline_002/independent_check_001.json` and the same-objective comparison in `TAIL_CLOSED_RELATIVE_FRONTIER_20261029.md`.

## Candidate claim and test considered

The candidate researcher decision was: **choose a fixed cortical area for follow-up recording from scalp EEG, and determine whether a source-family-aware report captures more sampled SEEG-responsive contacts than matched-area baselines on held-out participants.**

The proposed endpoint was participant-macro positive-contact capture, comparing the same area budget against GBF, direct constrained fitting, MNE/dSPM/eLORETA/LCMV, patch/extent, PSF/CTF, and XDL-ESI where a fair reproduction is possible. This endpoint is deliberately limited: responsive SEEG contacts are sparse positives; unimplanted or nonresponsive locations are not verified negatives. It cannot validate the complete generator, whole-cortex coverage, or the correctness of an ambiguity probability.

The candidate map used the minimum compatible parcel-mass fraction across the source-family set. This is **not ready to freeze**: one compatible explanation with zero mass in a parcel forces that parcel's score to zero. If compatible explanations avoid all parcels, the entire map is zero and the policy abstains. There is no eligible WSGZP source-family fit to establish whether this happens. Do not relax the minimum, add family weights, or tune an area budget after seeing outcomes. The candidate score therefore remains a falsifiable design hypothesis, not a validated algorithm.

The algebraic failure is documented in
[`FIXED_AREA_SCORE_FALSIFICATION_20261029.md`](FIXED_AREA_SCORE_FALSIFICATION_20261029.md): for any parcel avoided by one feasible member of the compatibility set, its guaranteed-mass score is exactly zero. This is a property of the definition, not a finding from neural data. The score is rejected for ranking unless a separately justified rule is specified before outcome access.

## Evidence and requirement audit

| Requirement | Current evidence | Status |
|---|---|---|
| Preserve prior work and sealed release | Track A release and prior source-family audits remain intact; this report is additive. | Met |
| Define a precise decision, endpoint and baselines | Candidate is recorded in `NOVELTY_TARGET_SELECTION_20261029.md`; the exact map score has a degeneracy risk and numeric choices are not frozen. | Partial; not a locked protocol |
| Check close prior art | 2026 GBF work already analyzes WSGZP; XDL-ESI also analyzes the same CCEP cohort; PSF/CTF, spatial-fidelity, set-membership and robust inverse work overlap substantially. | Met as a falsification screen; no gap established |
| Participant-specific WSGZP forward models | The local extracted dataset scan found no original `.hpts` digitizer file or scalp-to-MRI registration transform/QC. CHARM model build has not started. | Not met |
| Reproducible preprocessing and endpoint semantics | Study-level pipeline descriptions exist, but processing of the released arrays, baseline/scale, artifact handling and ICA fitting scope are inherited and not independently replayed. | Not met |
| Frozen participant-held-out protocol | `PROTOCOL_LOCK.md` remains UNLOCKED; B4–B7 are PIVOT. | Not met |
| Held-out measured neural EEG comparison and independent replay | No eligible WSGZP signal analysis has been run. HDEEG access is unresolved and its surgery outcome is indirect. | Not met |
| Existing measured-data evidence | Localize-MI `sub-01` compares source families on measured stimulation pulse artifacts with a held-current check. Its saved output SHA-256 was rechecked as `B19F896546154514E622F3D1286362E9571733BDE2CB3FF4ABC8AB047F26151B`. The flexible fits residuals better; this is not neural source recovery, participant-held-out validation, or researcher-decision advantage. | Valid bounded control only |
| Demonstrated advantage over baselines | Direct constrained fitting has supplied equivalent decisions in existing conditional model audits; no held-out measured-data utility gain is established. | Not met |
| Novel mathematical guarantee or certified computational advantage | No distinct guarantee or cost/tightness improvement over direct fitting and established robust/set-valued methods has survived the prior-art and reduction audits. | Not met |

## Why the claim must pivot now

The primary empirical route is not ready to support the proposed analysis: the released BIDS electrode coordinates and T1w MRIs are present, but the upstream digitizer-to-MRI provenance and participant-level registration QC have not been found in the extracted release or broader local user workspace. The released-array preprocessing is not fully reproducible, and the B5 protocol is not locked. These are validity requirements, not paperwork that can be waived to meet a deadline. WSGZP has already been used for GBF and XDL-ESI source analyses, so applying source families to this dataset or reporting contact overlap alone would not establish novelty. The expanded filename-only search is recorded in [`WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md`](WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md); it found unrelated Localize-MI and ds004752 transforms, but no WSGZP digitizer or registration artifact.

The alternate data routes do not close the gap. The metadata-only Localize-MI feasibility audit found the proposed held-out cross-intensity artifact test too sparse and uneven: only 19 geometry-eligible comparisons remain across six untouched participants, with one participant contributing 12 and the others 0–3. It is not suitable for the planned participant-level decision test, and it is a pulse-artifact endpoint rather than endogenous neural activity. The earlier B7 same-model analysis found moderate association between the forward-signature score and MNE PSF summaries but no researcher decision benefit. HDEEG-IED-SurgOutcome is access-limited and supplies indirect clinical references; its 2026 GBF overlap further reduces the available independent evaluation set. `ds004752` is a scalp-to-iEEG transport benchmark, not a spatially registered source-recovery endpoint. No substitute has been silently promoted to neural ground truth.

## Submission-safe conclusion

> Observable Geometry is an auditable computational tool for examining how EEG source distinguishability changes under declared source-family and forward-model assumptions. Its current results are conditional software and model diagnostics. They do not establish a novel source-localization method, calibrated source uncertainty, or recovery of endogenous neural generators. A held-out measured-data test of researcher-decision value remains unverified because the participant-specific geometry, preprocessing contract and protocol lock are unresolved.

## Reopen criteria

Reconsider the WSGZP test only after receiving and independently checking the original scalp digitizer points, MRI-registration transform and registration QC for eligible participants; resolving released-array preprocessing and signal scale; specifying a nondegenerate score and numeric area budget without outcome access; completing the matched-baseline protocol; and obtaining independent review before signal fitting. If any requirement cannot be met, retain the bounded software contribution and do not revive the novelty claim.

## Sources inside this project

- `docs/track_b/PROJECT_DEFINITION.md`
- `docs/track_b/GATE_REGISTER.json`
- `docs/track_b/PROTOCOL_LOCK.md`
- `docs/track_b/NOVELTY_TARGET_SELECTION_20261029.md`
- `docs/track_b/CALIBRATION_IDENTIFIABILITY_AUDIT_20261029.md`
- `docs/track_b/MEASURED_SOURCE_REFERENCE_DATASET_REVIEW_20261029.md`
- `docs/track_b/WSGZP_COORDINATE_PROVENANCE_REQUEST.md`
- `docs/track_b/WSGZP_PREPROCESSING_PROVENANCE_20261028.md`
- `docs/track_b/WSGZP_FORWARD_MODEL_BUILD_FEASIBILITY_20261029.md`
- `research/gbf_omitted_activity_20261024/LOCALIZE_FAMILY_VALIDATION_20261028.md`
- `docs/track_b/NOVELTY_PROOF_PLAN_20261028.md`
- `docs/track_b/FIXED_AREA_SCORE_FALSIFICATION_20261029.md`
- `docs/track_b/WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md`

Closest external threats recorded in the prior-art audit include [the GBF study](https://arxiv.org/html/2604.25592), [CANDLE](https://arxiv.org/abs/2610.07824), [the observability-aligned diffusion/null-space preprint](https://arxiv.org/abs/2610.27461), [XDL-ESI](https://doi.org/10.1016/j.neuroimage.2024.120802), [EEG/MEG spatial-fidelity evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7793168/), and [forward-model uncertainty analysis](https://orbit.dtu.dk/en/publications/evaluation-of-the-influence-of-uncertain-forward-models-on-the-ee/).
