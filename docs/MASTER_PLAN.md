# Recoverable Source Geometry: master research and delivery plan

> **Historical plan, superseded 24 October 2026.** The active build target is the GBFs source-pattern distinguishability tool documented in [`track_b/PROJECT_DEFINITION.md`](track_b/PROJECT_DEFINITION.md) and [`track_b/GBF_BUILD_PLAN.md`](track_b/GBF_BUILD_PLAN.md). RSG calibration and adaptive reporting remain unvalidated ideas, not the active project route.

**Owner:** Tranav Tyagi. **Reviewed:** 22 October 2026. **Status:** Track A Foundation Build verified for one development case; Track B Research Build remains planned.

## 1. Project in one sentence

Recoverable Source Geometry (RSG) will attempt to determine the finest task-specific cortical distinction supported by an EEG montage under measured noise and plausible head-model uncertainty, then prevent a GBFs reconstruction from displaying finer spatial detail than held-out evidence justifies.

GBFs supplies the cortical geometric language. The forward-model ensemble represents physical uncertainty. A calibrated recoverability hierarchy is the candidate contribution. The 3D interface explains the result. Additional-electrode recommendation is a later extension.

## 2. Scientific question and scope

**Question:** Can a statistically calibrated, model-robust measure predict which cortical source alternatives EEG can distinguish, and can that measure improve the honesty or utility of source reconstruction relative to existing resolution analysis?

The answer is conditional on the source family, amplitude/orientation/latency treatment, montage, reference, noise distribution, head-model family and allowed decision error. The project will not claim a universal spatial resolution, recover every brain event, decode imagination or identify causal circuitry.

## 3. Candidate contribution

For each pair of candidate source descriptions, RSG compares their forward-predicted scalp signatures after handling task-relevant nuisance variables. It relates this separation to a statistical error tolerance and tests robustness across a justified family of forward models. Because thresholded pairwise similarity is not transitive, the first representation will be a hierarchy or set-valued ambiguity region rather than an unjustified equivalence partition.

The possible innovation is a **forward-family, measurement-level, statistically calibrated recoverability object** in a GBFs source language, tested against held-out empirical confusion. Resolution matrices, adaptive cortical parcellation, Bayesian uncertainty and robust forward modeling already exist. Gate 0 must show an exact mathematical difference before the project uses “new framework” as a result rather than an aim.

## 4. Components and roles

| Component | Role | Status |
|---|---|---|
| GBFs | Existing estimator and geometric basis | Code pinned and inspected; benchmark not reproduced |
| Localize-MI | Physical stimulation/scalp benchmark | Metadata and one selected payload inspected |
| Reverse engineering | Trace equations to actual GBFs transformations | Initial audit complete |
| RSG metric | Nuisance-aware, calibrated source distinguishability | Candidate specification only |
| Forward ensemble | Conductivity/electrode/model sensitivity supported by physical ranges | Not designed fully |
| Calibration | Map predicted separation to empirical confusion on development data | Planned; simple statistical model first |
| Adaptive reporting | Limit displayed detail according to recoverability | Planned after metric validation |
| Sensor recommendation | Split a specified unresolved distinction | Deferred extension |
| Viewer | Display hierarchy, alternatives, model sensitivity and provenance | Delivery layer, not scientific novelty |

A large neural network is not justified by seven participants. Any ML component begins with simple calibration and must outperform a fixed mapping on untouched participants.

## 5. Work packages and kill gates

### WP0: novelty and task definition

Complete equation-level comparisons with GBFs, resolution-matrix analysis, adaptive parcellation, SESAMEEG, robust eLORETA and Bayesian approximation-error methods. Select one source family and one decision task. Specify nuisance variables and the empirical meaning of “distinguishable.”

**Pass:** one exact mathematical difference, expected benefit, falsifier and compatible benchmark. **Fail:** narrow the contribution or present a replication study.

### WP1: physically valid data contract

Resolve channel order, units, reference, time axis, covariance convention, source orientation, surface/forward coordinates and the meaning of a bipolar stimulation target. Separate stimulation artifact localization from physiological response localization.

**Pass:** annotated case manifest and transform diagram. **Fail:** stop scientific processing.

### WP2: GBFs reproduction and reverse engineering

Reproduce unchanged upstream behavior on identical inputs, then document a recorded-data adaptation separately. Preserve upstream normalization and penalty behavior in parity mode. Do not call a Localize-MI adaptation reproduction of the GBFs paper benchmark.

**Pass:** hashes, environment, numerical comparison, departures and interpretation limits. **Fail:** diagnose before adding RSG.

### WP3: mathematical recoverability specification

Define source signatures, nuisance profiling, covariance support, model-family treatment, statistical threshold and hierarchy construction. Analyze identical, weakly separated, observable, null-space and misspecified cases. Resolve threshold non-transitivity explicitly.

**Pass:** another researcher could implement the method without guessing. **Fail:** revise mathematics before code expansion.

### WP4: forward-family construction

Use only uncertainty ranges supported by metadata or primary literature. Preserve a shared source convention. Establish whether the available prepared forward permits conductivity/electrode perturbations; arbitrary noise added to a gain matrix is not a physical head-model ensemble.

**Pass:** reproducible perturbation generator with parameter provenance and sensitivity plots. **Fail:** evaluate nominal recoverability only and narrow the claim.

### WP5: frozen evaluation

Keep sub-01 as development because it has already been inspected. Choose remaining development/test participants by eligibility without viewing outcomes. Group repeated pulses and sessions. Freeze preprocessing, nuisance handling, thresholds, baselines, exclusions and one primary endpoint.

**Pass:** dated protocol before test evaluation. **Fail:** label results exploratory and obtain fresh confirmation for later claims.

### WP6: empirical test

First test whether predicted source-condition separation agrees with held-out empirical distinguishability. Then test whether recoverability-limited reporting improves calibration or spatial utility. Compare nominal lead-field distance, resolution/adaptive-parcellation analysis, original GBFs and one conventional inverse baseline with matched tuning.

**Pass:** participant-level benefit and documented failures. **Fail:** report the null/negative result and revise only with development evidence.

### WP7: integration and release

Export the recoverability hierarchy, alternatives, source maps and provenance. The viewer must show units, reference, model assumptions and whether a layer represents noise uncertainty, model sensitivity or empirical calibration. Verify licenses and clean-environment reproduction.

**Pass:** an external user can reproduce the main result. **Fail:** do not call the package complete.

### WP8: optional sensor design

Only after WP6 succeeds, rank feasible added sensors by their expected ability to separate one unresolved source contrast. Account for reference changes and correlated noise. Compare equal-budget standard, random and nominal designs.

## 6. Architecture

Recorded data and geometry → contract validation → reference/noise model → GBF source signatures → nuisance-aware separation → forward-family robustness → calibrated recoverability hierarchy → disciplined reconstruction → report/viewer.

The upstream GBFs clone remains unchanged. Adapters provide explicit arrays and metadata. Research logic is independent of the viewer. Every cache key includes mesh, basis, channels, reference, orientation, model parameters and software version.

## 7. Evaluation hierarchy

**Primary endpoint:** held-out calibration of predicted pairwise source-condition distinguishability, aggregated at participant level. The exact calibration score and tolerated error are frozen after the source family and data contract are resolved.

**Secondary endpoints:** participant-level localization distance, empirical confusion ranking, recoverability-hierarchy stability, sensitivity to forward perturbations, and spatial detail retained compared with baselines.

Repeated trials increase precision within a condition but do not increase the participant count. Localize-MI does not provide full distributed cortical-current truth, so it cannot validate whole-brain amplitude recovery. Conditional posterior amplitude variance is not a location-confidence or recoverability certificate.

## 8. Completion definitions

**Engineering completion:** pinned environment, valid data contract, GBFs parity, specified RSG implementation, mathematical tests, recorded-data run, clean reproduction and documented interface.

**Scientific completion:** frozen held-out evaluation against strong baselines, participant-level uncertainty, ablations, sensitivity analysis and honest failure reporting.

**Innovation evidence:** an equation-level difference from closest methods plus empirical evidence that the difference predicts confusion or improves a prespecified decision. Packaging, naming, ensemble averaging or visually smoother maps do not satisfy this criterion.

## 9. Timing after build authorization

| Cumulative milestone | Focused effort | Likely elapsed time |
|---|---:|---:|
| Close WP0-WP1 decisions | 20-40 hours | 1-2 weeks |
| Recorded GBFs baseline | 40-70 hours | 2-5 weeks at 15-25 h/week |
| RSG metric and development analysis | 90-150 hours | 4-10 weeks |
| Held-out study and reproducible release | 170-270 hours | 7-18 weeks |
| Optional sensor design and broader confirmation | 230-360 hours | 10-24 weeks |

Rows are cumulative. Data and reproduction problems should receive a 25-35% contingency. A December scoped prototype is possible with sustained work and a narrow source task; a validated breakthrough is not schedulable in advance.

## 10. Immediate decisions still open

1. Which source family is physically compatible with Localize-MI stimulation?
2. Which empirical discrimination task can be evaluated without target leakage?
3. How should amplitude, polarity, orientation and latency be handled?
4. Is robust separation same-model worst case, set-to-set separation or probability-weighted risk?
5. Should the first output be a hierarchy or source-centered ambiguity sets?
6. Can meaningful forward perturbations be regenerated from available anatomy?
7. What exact existing method is the strongest RSG comparator?

These are foundation decisions. Implementation should not begin until WP0 and the critical parts of WP1 have passed.
