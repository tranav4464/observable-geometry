# Review first: project decision and foundation gates

> **Historical review plan, superseded 24 October 2026.** The proposed RSG research route and pre-build authorization language below are not active constraints. Current scope and progress are in [`track_b/PROJECT_DEFINITION.md`](../track_b/PROJECT_DEFINITION.md) and [`track_b/GATE_REGISTER.json`](../track_b/GATE_REGISTER.json).

**Updated 22 October 2026 | Track A foundation accepted | Track B research/novelty work ready to start**

## Proposed project

**Recoverable Source Geometry:** calculate the finest task-specific cortical distinction that EEG can support under sensor noise and plausible head-model uncertainty. GBFs supplies the geometric source representation. The forward-model ensemble supplies physical uncertainty. A calibrated recoverability hierarchy is the candidate contribution.

This is a plausible research direction, not a demonstrated innovation. Adaptive cortical parcellation and resolution-matrix analysis already target source distinguishability; robust inverse methods already address forward uncertainty. Track B starts with full method-level comparison, task validity and a go/no-go novelty decision.

## Decision table

| Decision | Proposed position | Status |
|---|---|---|
| Starting system | Pinned GBFs implementation | Recorded-data execution plus independent same-input algebraic parity check complete; paper benchmark not reproduced |
| Main scientific output | Calibrated recoverability hierarchy/ambiguity sets | Candidate |
| Physical uncertainty | Justified family of plausible forward models | Candidate; generation feasibility unresolved |
| Reconstruction output | Never display finer detail than recoverability supports | Downstream hypothesis |
| ML role | Simple calibration of predicted separation to empirical confusion | Optional; sample size limits complexity |
| Primary dataset | Localize-MI | Selected inputs inspected |
| Primary endpoint | Held-out calibration of predicted distinguishability | Definition pending task audit |
| Sensor selection | Later extension | Deferred |
| REA | Use only for a relevant opaque component | No target identified |
| Long-term HIRO goal | Motivation only | Outside this study |

## Foundation gates

### Gate 0: novelty and task fit

Complete equation-level comparison with resolution matrices, adaptive parcellation, SESAMEEG, robust eLORETA and Bayesian model-error approaches. Specify the source family, nuisance variables, statistical decision and exact difference.

**Exit:** closest-method matrix, exact objective, predicted benefit and falsifier. **Status:** not passed; direct prior-art collision found.

### Gate 1: physical data contract

Verify reference, units, channels, time, covariance, orientation, coordinate transforms and the physical meaning of a bipolar stimulation target. Confirm that the benchmark source can be represented in the chosen source family.

**Exit:** annotated manifest and transform/target diagram. **Status:** partial.

### Gate 2: GBFs baseline parity

Reproduce pinned upstream numerical behavior, then document Localize-MI adaptation separately. Resolve the observed normalization and penalty-domain questions.

**Exit:** reproducibility report with hashes and departures. **Status:** Track A same-input parity and recorded-data integration passed; published GBFs benchmark not reproduced.

### Gate 3: complete RSG mathematics

Define nuisance-aware separation, noise support, forward-family treatment, calibrated tolerance and hierarchy construction. Resolve non-transitivity of threshold similarity and derive limiting cases.

**Exit:** implementation-independent specification. **Status:** candidate equations only.

### Gate 4: valid forward ensemble

Use physical perturbations with cited ranges and shared source correspondence. Do not substitute arbitrary gain-matrix noise.

**Exit:** parameter provenance and reproducible generator design. **Status:** unresolved.

### Gate 5: leakage-resistant evaluation

Freeze participant split, grouping, thresholds, baselines, exclusions and one primary endpoint before test outcomes. Treat inspected sub-01 as development.

**Exit:** dated protocol and failure criteria. **Status:** draft only.

### Gate 6: evidence and release

Report participant-level calibration, utility, sensitivity and failures. Reproduce the result cleanly with licenses and provenance.

**Exit:** reviewable release. **Status:** no experiment completed.

## Scope ladder

**Minimum build:** GBFs reproduction plus a prespecified test of whether predicted source-condition separation tracks held-out empirical confusion.

**Strong prototype:** validated RSG hierarchy, matched reconstruction comparisons, clear failures and reproducible 3D/report interface.

**Extended project:** ambiguity-targeted sensor recommendation and a second confirmation dataset or hardware study.

## Two-track delivery decision

Track A is a complete Foundation Build: verified GBFs reproduction, recorded-data adaptation, nominal source signatures, nominal distinguishability, ambiguity reporting and a reproducible interface. Track B is the Research Build: justified forward-model family, RSG mathematics, calibration, recoverability-limited reconstruction and held-out validation. Track B begins only after the Foundation is frozen and Gate 0 identifies a defensible gap. See the [two-track execution plan](../planning/two-track-execution-plan.md) for work packages and acceptance evidence.

## Realistic estimate after authorization

| Outcome | Cumulative effort |
|---|---:|
| Close novelty/task/data decisions | 20-40 focused hours |
| Recorded GBFs baseline | 40-70 hours |
| RSG development prototype | 90-150 hours |
| Held-out study and release | 170-270 hours |
| Sensor extension/broader confirmation | 230-360 hours |

At 25 hours per week, the core release is roughly 7-11 weeks; at 15 hours per week, roughly 12-18 weeks. These are estimates, not guarantees. A reproducible study can be planned; a breakthrough cannot.

## Required review decision

Track A is now an executable foundation, not evidence that Recoverable Source Geometry is novel or scientifically useful. Review the development report and `RECOVERABLE_SOURCE_GEOMETRY.md` before starting Track B experiments.

## Change control

Record scope changes in [`decisions.md`](decisions.md). Do not install dependencies, train models, generate recordings, run experiments or continue implementation until Tranav explicitly authorizes the build. Research and documentation may continue.
