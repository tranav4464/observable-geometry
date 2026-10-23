# Recoverable Source Geometry: candidate framework specification

**Reviewed 22 October 2026. Planning only. No novelty or performance claim has been established.**

## 1. The proposed contribution

Recoverable Source Geometry (RSG) asks a narrower question than ordinary EEG source reconstruction:

> Given a stated source family, sensor montage, reference, noise level and plausible head models, what is the finest cortical distinction that the measurements can support at a prespecified error tolerance?

GBFs supplies a compact cortical geometry basis. A forward-model ensemble represents plausible variation in conductivities, electrode locations and other justified physical assumptions. RSG would operate before or alongside an inverse estimate, identify source alternatives whose sensor predictions cannot be reliably separated, and prevent the displayed spatial detail from exceeding that limit.

The intended outputs are:

1. a task-specific recoverability profile;
2. source alternatives that remain observationally confusable;
3. a cortical representation that becomes coarse where distinctions are unsupported and fine where they are supported;
4. separate effects of sensor noise and forward-model variation;
5. eventually, a measurement recommendation targeted at one unresolved distinction.

This is not a claim to recover all neural activity. It is a framework for stating which distinctions are supported under explicit conditions.

## 2. Why the first idea was insufficient

Forward-model uncertainty, probabilistic source localization, resolution matrices, point-spread/cross-talk analysis and adaptive EEG/MEG parcellation all have substantial prior art. In particular, Farahibozorg, Henson and Hauk (2018) already optimized cortical parcels using cross-talk-based sensitivity and distinguishability, and Hauk, Stenroos and Treder (2022) formalized practical resolution-matrix analysis. Therefore neither “merge indistinguishable regions” nor “run GBFs across several head models” is a standalone innovation.

The candidate distinction of RSG is the combination of:

- a **forward-family, measurement-level** distinguishability criterion rather than a partition derived only from one chosen inverse operator;
- an explicit statistical decision tolerance rather than an uncalibrated similarity threshold;
- robustness to a justified family of head models;
- a geometric source language compatible with GBFs;
- empirical testing of predicted confusability using held-out physical stimulation data.

This difference is currently a hypothesis. Gate 0 requires an equation-level review showing that the same object and guarantee are not already available.

## 3. Observation model

For model `m`, let

    y = R L_m Phi a + epsilon,

where `y` is the scalp observation, `R` is the reference operator, `L_m` is a lead field, `Phi` is a geometric cortical basis, `a` is a coefficient vector and `epsilon` has covariance `C_m`. Every comparison must use the same physical units, channel order, source convention and averaging level.

For candidate source descriptions `a` and `b`, define their model-conditional sensor difference

    Delta_m(a,b) = R L_m Phi (a-b).

A first candidate separation is

    d_m(a,b)^2 = Delta_m(a,b)^T C_m^+ Delta_m(a,b),

computed only on the supported covariance subspace. A robust lower separation could be the infimum over a prespecified model family. If uncertainty sets are compared rather than paired models, the correct same-model or set-to-set formulation must be justified physically before implementation.

Under an ideal equal-covariance Gaussian two-hypothesis model with known means and equal priors, Mahalanobis separation is linked to optimal classification error. This supplies an interpretable starting point, not a license to assume real EEG is Gaussian. Development data must calibrate the decision threshold and untouched data must test it.

## 4. Nuisance parameters that must be removed fairly

Two locations cannot be declared distinguishable merely because one candidate was assigned a larger arbitrary amplitude. The comparison must specify or optimize over nuisance amplitude, polarity, orientation, latency and baseline according to the scientific task. Candidate choices include normalized topographic distance, principal angle between predicted sensor subspaces, or a likelihood ratio that profiles nuisance parameters. These are competing formulations to evaluate, not interchangeable metrics.

The source family also matters. Focal dipoles, cortical parcels and arbitrary combinations of GBFs produce different recoverability questions. The initial study should use one prespecified family closely aligned with the physical benchmark. Results cannot be generalized automatically to arbitrary distributed brain activity.

## 5. From pairwise separation to a cortical representation

The threshold relation `d(a,b) < tau` is generally not transitive. Calling it an equivalence relation without repair would be a mathematical error. Connected components can create chaining, where distant endpoints become grouped through intermediate similarities. A valid RSG partition therefore needs one of the following, selected before implementation:

- a partition optimization with an explicit within-cell and between-cell criterion;
- a hierarchy or dendrogram that preserves graded ambiguity instead of claiming equivalence;
- a set-valued recoverability region around each candidate without forcing a global partition.

The recommended first formulation is a **recoverability hierarchy**. At each calibrated error tolerance, it shows which distinctions are supported. A single adaptive parcellation may be derived later for visualization, with its loss function and stability reported.

## 6. Candidate research claims and falsifiers

### Claim A: calibration

Predicted robust separation is associated with held-out empirical distinguishability between known stimulation conditions.

**Fails if:** declared high-recoverability pairs are frequently confused, calibration is unstable across participants, or nominal lead-field distance performs equally well under matched tuning.

### Claim B: reconstruction discipline

Restricting reported spatial detail using the recoverability hierarchy reduces unsupported precision while preserving or improving useful localization compared with tuned GBFs and adaptive-parcellation baselines.

**Fails if:** spatial coarsening only makes maps look stable, loses useful localization without improved calibration, or duplicates an existing resolution-matrix method.

### Claim C: model robustness

The forward-model family predicts failures that a single nominal model misses.

**Fails if:** plausible perturbations have no reproducible relationship with held-out errors, or uncertainty ranges are arbitrary and chosen after observing outcomes.

Only claims supported by the eventual results may appear in a report.

## 7. Minimum scientific study

1. Reproduce and audit a pinned GBFs path.
2. Define one physically compatible source family and one observation window.
3. Construct only forward perturbations supported by available anatomy and literature.
4. Compare nominal distance, resolution-matrix/adaptive-parcellation analysis, and the candidate robust recoverability measure.
5. Freeze nuisance handling, thresholds, participant split and exclusions on development data.
6. Test calibration and spatial utility on untouched participants.
7. Report individual participants, failures and sensitivity to every major modeling choice.

Localize-MI can test whether predicted distinctions between stimulation conditions are reflected in recorded scalp patterns. It does not provide the complete distributed cortical current, so it cannot validate every amplitude or whole-brain claim. Stimulation artifact and physiological response require separate interpretations.

## 8. Stage gates

| Gate | Required evidence | Failure response |
|---|---|---|
| 0. Novelty | Equation-level comparison with adaptive parcellation, resolution analysis, robust inverse and Bayesian model-error methods | Narrow or abandon the novelty claim |
| 1. Physical contract | Verified reference, units, orientations, coordinate transforms, source target and time window | Stop; repair data/target definition |
| 2. Baseline parity | Pinned GBFs behavior reproduced on identical inputs | Diagnose before extension |
| 3. Metric validity | Nuisance-invariant distance, calibrated threshold and non-transitivity handled explicitly | Revise mathematics |
| 4. Perturbation validity | Forward ensemble generated from justified parameter ranges and shared source correspondence | Remove unsupported perturbations |
| 5. Frozen evaluation | Dated split, equal tuning budgets, endpoints, exclusions and falsifiers | Do not inspect test outcomes |
| 6. Held-out evidence | Participant-level calibration and utility against strong baselines | Report null/negative result honestly |
| 7. Release | Clean reproduction, manifests, licenses, provenance and interpretation limits | Do not call the package complete |

## 9. What would count as innovation

The project would justify a framework claim only if it delivers a mathematically defined recoverability object that differs from existing resolution/adaptive-parcellation methods, has a statistically meaningful operating point, handles model uncertainty coherently, and predicts held-out empirical confusability or improves a prespecified downstream decision. A new name, interface, ensemble average or attractive brain map is insufficient.

## 10. Scope boundary

The first authorized build should stop after Claim A and the minimum reconstruction comparison. Ambiguity-targeted electrode recommendation is a later extension. Thought decoding, imagination reconstruction, causal circuit discovery and full-brain modeling are motivations for future work, not outcomes of this study.
