# Mathematical specification: planning version 0.2

> **Historical mathematical proposal, superseded 24 October 2026.** The RSG calibration equations below were not adopted as the active contribution. The current frozen GBFs diagnostic is specified in [`track_b/B2_GBF_SPEC.md`](track_b/B2_GBF_SPEC.md); it makes no novel-method claim.

**Status:** Track A includes standard linear-Gaussian inference and a nominal noise-whitened source-signature measure. The RSG formulas below remain candidate research formulations and are not validated.

## Observation model

For model `m`, channels `C`, vertices `V` and geometric modes `K`:

    y = R L_m Phi a + epsilon_m,    Cov(epsilon_m) = R C_m R^T.

`R` is the reference operator, `L_m` the forward model, `Phi` the GBF basis and `a` a source coefficient description. Whitening is performed only on the supported positive eigenspace of the referenced covariance. Channel order, units, orientation, source correspondence and averaging convention must match.

## Candidate recoverability measure

For two candidate source hypotheses `a` and `b`:

    Delta_m(a,b) = R L_m Phi (a-b)
    d_m(a,b)^2 = Delta_m(a,b)^T (R C_m R^T)^+ Delta_m(a,b).

This is a noise-scaled sensor separation, not yet an original method. A robust candidate is an infimum over a prespecified model family. Three interpretations must be compared before one is selected:

1. **Same-model worst case:** the same unknown physical model generates either hypothesis.
2. **Set-to-set separation:** each hypothesis ranges over its own prediction set; conservative but potentially too pessimistic.
3. **Distribution-weighted risk:** integrates a justified distribution over model parameters; informative only if weights have physical meaning.

The metric must profile or normalize nuisance amplitude, polarity, orientation, latency and baseline according to the chosen task. Otherwise arbitrary scaling can create artificial distinguishability. Principal angles between predicted subspaces or a nuisance-profiled likelihood ratio may be more appropriate than direct vector distance.

## Statistical operating point

For ideal Gaussian observations with equal covariance, known means and equal priors, Mahalanobis separation is related to optimal two-class error. This provides a sanity check. Real thresholds must be calibrated on development data because EEG noise, preprocessing and estimated covariance violate ideal assumptions.

The planned output is not “percentage of the brain recovered.” It is a statement such as: under the stated task and assumptions, these alternatives reach a prespecified empirical discrimination error. Calibration quality and abstention must be evaluated on untouched participants.

## Recoverability hierarchy

The relation `d(a,b) < tau` is reflexive and symmetric under common conditions but generally not transitive. It therefore cannot be called an equivalence relation automatically. Connected components can produce chaining. RSG v0 should return either:

- source-centered ambiguity sets at each tolerance; or
- a hierarchy built with an explicitly stated clustering loss and complete separation constraints.

A single adaptive parcellation is a derived visualization. Its number of regions, stability and dependence on the source family must be reported.

## Relationship to inverse reconstruction

For a standard prior `a ~ N(0,Q)`, conditional reconstruction may use:

    Cpost_m = (A_m^T A_m + Q^-1)^-1
    mean_a_m = Cpost_m A_m^T y,

where `A_m` is the consistently referenced and whitened projected lead field. These equations are established linear-Gaussian inference. They provide a baseline estimate and amplitude uncertainty; they do not establish spatial recoverability.

RSG may constrain the reported basis or aggregate the output according to its hierarchy. That downstream rule must be compared with existing resolution-matrix adaptive parcellation. Smoother maps are not automatically more accurate or honest.

## Forward-model ensemble

Plausible models may vary tissue conductivities or electrode positions only when corresponding physical models can be generated and source coordinates remain comparable. A mixture covariance can describe within-model and between-model spread, but chosen scenario weights are not posterior model probabilities. Arbitrary perturbations of the gain matrix do not establish robustness to anatomical uncertainty.

## Limiting-case tests required

- identical sensor signatures produce zero separation;
- scaling or polarity nuisance behaves exactly as specified;
- a null-space source difference remains unrecoverable;
- increasing supported noise lowers recoverability;
- reference rank loss is handled without singular precision;
- identical forward models reduce to the nominal formulation;
- expanding a worst-case model family cannot increase worst-case separation;
- hierarchy output does not violate its declared within/between criteria;
- covariance and forward misspecification trigger sensitivity warnings.

## Sensor design, deferred

After RSG validation, a candidate sensor may be scored by improvement in the recoverability of a prespecified unresolved contrast. The design must recompute reference and correlated noise consistently. Gaussian variance reduction is a baseline, not the proposed RSG innovation.

## Claim boundary

No rank, distance, hierarchy or posterior map demonstrates access to thoughts, causality or all neural events. RSG would certify only a declared discrimination task under a declared model family and empirical calibration regime.
