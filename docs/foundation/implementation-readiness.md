# Implementation readiness review

> **Historical readiness review, superseded 24 October 2026.** It records Track B as pre-authorization. The user has since authorized the GBFs software build, and the current status is in [`track_b/GATE_REGISTER.json`](../track_b/GATE_REGISTER.json). Retain this file as a record of the earlier Track A handoff, not as an active build restriction.

**Updated 22 October 2026. Track A engineering foundation accepted after remediation; this review covers scientific readiness for Track B.**

## Recommendation

Track A is ready to hand off to Track B's prior-art and task-feasibility research. Do not treat it as validation of RSG. Before a new-method claim or a physiological-source experiment, close the method-level novelty review and establish a benchmark with physically meaningful targets, orientation handling and held-out participants. The Track A stimulation-pulse artifact remains an integration benchmark only.

## Prior-art collision matrix

| Existing work | Capability already established | Required distinction for RSG |
|---|---|---|
| GBFs | Geometric cortical basis and inverse reconstruction | RSG uses GBFs as representation; cannot claim the basis |
| Resolution-matrix analysis | Point-spread, cross-talk and objective spatial-resolution metrics | RSG must define a measurement-level calibrated decision object beyond renaming these metrics |
| Adaptive cortical parcellation | Merges/splits parcels using sensitivity and distinguishability | RSG must differ mathematically through forward-family robustness and statistical calibration |
| SESAMEEG | Probabilistic focal localization and uncertainty | RSG cannot claim alternatives or uncertainty alone |
| Bayesian approximation error / robust inverse | Models conductivity/forward error | RSG must show why recoverability is a distinct target and useful output |
| Conductivity-aware sensor selection | Selects electrodes under conductivity uncertainty | Later RSG sensor design must beat this conceptually and empirically |

This matrix screens the gap; it is not yet a systematic review. A claim is permitted only after equations and assumptions are compared in full.

## Must-freeze decisions

1. Physical stimulation target and source family.
2. Artifact versus physiological response task.
3. Fixed versus free orientation handling.
4. Amplitude, polarity and timing nuisance treatment.
5. Robust model-family interpretation.
6. Hierarchy versus source-centered ambiguity sets.
7. Calibration score, tolerated error and participant split.
8. Strongest existing comparator and equal tuning budget.

## Acceptance checklist

| Artifact | Acceptance evidence | Status |
|---|---|---|
| Novelty statement | Exact mathematical difference and falsifier | Not ready |
| Data contract | Verified channels, reference, units, orientation and transforms | Track A integration contract passed; fixed-normal physical validity remains a limitation |
| Benchmark task | Defensible target and empirical discrimination definition | Pulse-artifact development proxy passed; physiological task not validated |
| GBFs baseline | Numerical parity and recorded adaptation | Track A integration and same-input algebraic parity passed; paper benchmark not reproduced |
| RSG mathematics | Nuisance handling, calibration and non-transitivity resolved | Candidate only |
| Forward ensemble | Physical ranges and reproducible generation | Not ready |
| Evaluation | Frozen split, primary endpoint and baselines | Draft only |
| Release | Clean run, provenance, licenses and interface | Track A sealed run passed; Track B release not started |

## Small-sample rule

Sub-01 is development because it has already been inspected. Select additional development/test participants by eligibility before method outcomes are viewed. Report every participant and aggregate trials within session and participant. Once test outcomes influence redesign, those participants no longer constitute independent confirmation.

## Failure controls

Missing transforms, source mismatch, unsupported perturbations, unexplained reference behavior or inability to reproduce GBFs all stop the scientific pipeline. Failed or null RSG results remain valid project outcomes. They must not be converted into a breakthrough claim through a new metric or post-hoc threshold.

## Execution boundary

Track A is accepted for the Track B research handoff. Track B may begin with prior-art equations, task validity and dataset feasibility; algorithm implementation and claims of novelty remain gated on that review and the next explicit build authorization. Track A outputs remain a development benchmark, not independent confirmation.
