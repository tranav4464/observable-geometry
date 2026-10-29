# Calibration identifiability audit for the WSGZP route

**Date:** 29 October 2026\
**Status:** design audit only; no EEG or SEEG samples accessed\
**Decision:** current WSGZP labels cannot calibrate whole-cortex source-set coverage or the correctness of the `unique enough / ambiguous / unsupported` label.

## Why “calibrated” needs a target

Let `Y` be a measured scalp response, `A_θ` a participant-specific forward operator under an admissible geometry/conductivity parameter `θ`, and `F_k` a declared source family. A natural compatibility score is

```text
r_k(Y) = inf_{θ ∈ U, X ∈ F_k} || W (Y - A_θ X) ||,
```

where `W` whitens using a declared noise covariance and `U` is a bounded forward-model uncertainty set. This score can support a statement about fit under the specified model. It does not, by itself, say that a true generator is in `F_k`, that a region has a calibrated probability of being active, or that the spatial set has a given coverage probability.

There are three different possible calibration targets:

| Target | What a valid calibration would establish | Evidence currently available | Status |
|---|---|---|---|
| Sensor-noise / residual compatibility | Under a declared noise and forward-error model, a threshold controls a stated false-rejection or goodness-of-fit rate for model-compatible observations. | WSGZP has a processed derivative and baseline metadata, but signal scale, reference/baseline provenance and geometry are unresolved. Fitting over families, source coefficients and `θ` also changes the residual distribution. | Not calibrated. A threshold needs a derived null distribution or a valid held-out null design after those gates close. |
| Whole-cortex source-set coverage | A set reported from scalp data contains a defined true neural generator with a stated marginal or conditional frequency. | Stimulation contacts mark intervention sites, not the generator of later distributed CCEPs. SEEG responsive contacts are sparse positives; unsampled and nonresponsive locations are not verified negatives. | Not identifiable from current WSGZP labels. Do not claim coverage, posterior probability, sensitivity/specificity, calibrated ambiguity, or false-confident-attribution rate. |
| Sampled positive-contact capture (evaluation endpoint, not set-coverage calibration) | At a fixed cortical-area budget, a map prioritizes a specified fraction of SEEG contacts labelled responsive in held-out participants. | Run-condition EEG/SEEG summaries may support this after protocol, geometry, scale and leakage gates close; the labels are sparse and only positive observations. | Potentially estimable as a bounded utility endpoint, with participant-level uncertainty. It is not source truth or calibration of the whole-cortex set. |

## Statistical constraint

Conformal uncertainty methods require calibration examples carrying the target whose coverage is claimed, plus an exchangeability unit that matches deployment. For example, task-driven conformal inverse-problem work constructs calibration scores using ground-truth task outputs and then calibrates intervals for those outputs ([Task-Driven Uncertainty Quantification in Inverse Problems via Conformal Prediction](https://pmc.ncbi.nlm.nih.gov/articles/PMC12109201/)). It does not make an unobserved biological source label available. WSGZP's intervention site and sparse positive SEEG contacts are not labels for the complete spatial generator of a later scalp response.

Likewise, a residual quantile is not automatically a valid noise threshold after selecting among source families and minimizing over coefficients and uncertain forward operators. The calibration procedure must account for that selection and dependence. A threshold estimated from post-response residuals could instead absorb model misspecification and cannot be interpreted as a false-rejection guarantee without additional assumptions and validation.

## What a scientifically honest WSGZP report may say

1. **Model-conditional compatibility:** enumerate which frozen source families have residuals below a clearly named, justified tolerance under the stated forward model and uncertainty set. Until the tolerance has a valid calibration, call it a *prespecified fit tolerance*, not a calibrated probability or coverage threshold.
2. **Model-conditional ambiguity:** if materially different families or supports satisfy that criterion, say the measured field does not distinguish them *under these assumptions*. This is a mathematical consequence of the declared model, not proof that all listed sources occurred biologically.
3. **Sampled-contact utility:** separately test whether a frozen fixed-area shortlist captures more responsive SEEG contacts than matched-area GBF, direct-fit, patch and resolution baselines in participant-held-out evaluation. Report participant-macro estimates and intervals, plus implantation-density/region/distance controls. This is an outcome-evaluation endpoint, not calibration of the source set. Call the metric positive-contact capture or prioritization yield, never whole-cortex sensitivity or source recovery.
4. **No outcome leakage:** write/hash family compatibility outputs and the shortlist before revealing corresponding SEEG summaries. Use participants, not run rows or contacts, as the independent split/resampling unit.

## Evidence needed to upgrade each claim

### To calibrate noise/residual compatibility

Resolve the WSGZP scale/reference/baseline and geometry contracts; define `W`, the admissible `U`, the null and the false-rejection target; derive the score distribution including family/parameter/uncertainty optimization, or provide an independent participant-grouped calibration set whose exchangeability assumptions are justified. Freeze the threshold and validate empirical coverage of the *declared residual event* on held-out participants. This still does not calibrate spatial coverage.

### To calibrate spatial coverage or ambiguity decisions

Obtain independent measured examples with a defensible reference for the target being covered: e.g. a known neural generator or an independently adjudicated, sufficiently complete source target at the same spatial/temporal scale. Stimulation location alone is inadequate for later distributed CCEP responses. Sparse positive SEEG contacts can validate positive-contact capture, but cannot label unobserved cortex as inactive or score the complete source set. Calibration and test splits must be participant-disjoint and match the intended deployment population.

## Novelty consequence

“Calibrated source-family observability certificate” is currently too strong as a WSGZP claim. The route may still support a useful researcher-facing **model-conditional compatibility report** plus a separate **held-out sampled-contact prioritization test**. Neither is novel merely by being packaged together. Novelty would require a preregistered, reproducible advantage over GBF, direct constrained fitting and matched patch/resolution methods on the bounded endpoint, or a new valid mathematical guarantee. If all decisions and utility are equivalent, classify the result as useful software only or pivot.

## Current gate effect

This is a metadata/literature/statistical-design conclusion, not a data result. It does not authorize signal access or model fitting. It narrows the current claim and adds a prerequisite: before the planned participant-held-out test, specify whether the project is testing (a) model-conditional compatibility at a fixed tolerance or (b) a genuinely calibrated residual event. Do not call either one source-truth calibration. Existing signal-access gates remain closed.
