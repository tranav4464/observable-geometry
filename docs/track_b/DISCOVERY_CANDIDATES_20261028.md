# Discovery candidates after WSGZP/prior-art audit

**Status:** candidate ranking only; no new-method claim supported yet.

## New data-readiness finding (28 October 2026)

Before source fitting, a coordinate-only MRI proximity screen compared the
declared scalp-electrode T1w coordinates with thresholded MRI tissue and used
native-MRI SEEG contacts as a same-image coordinate positive control. Across
36 participants, SEEG contact median proximity was 1.0–1.1 mm, while scalp
electrode medians ranged from 2.0 to 43.0 mm. `sub-32` is an unresolved
outlier (43.0 mm median, 62.7 mm p90) and should be held out of initial
modeling until its coordinate provenance or MRI overlay is reviewed. The
screen is approximate, not a scalp segmentation or registration proof; no
signal samples were read. A separate rotation/translation-invariant comparison
found `sub-32`'s pairwise electrode geometry agrees with MNE's HydroCel-256
template at correlation 0.9934 and 5.75 mm scaled RMSE, within the cohort
range. That suggests a pose/frame mismatch or MRI-screen limitation rather
than an internally malformed net, but cannot identify the cause. The original
`.hpts` source and exact transform are absent from the public package, so the
alignment remains unresolved. These are data-readiness findings, **not a
discovery or novelty result**. See
`WSGZP_COREG_AUDIT_20261028.md` and the external machine-readable screen
outputs.

## The useful question the current data can answer

For each same-stimulation run, does the spatial statement inferred from the
measured scalp response change across defensible source families and bounded
participant-forward-model perturbations, and do rules learned on other
participants make a useful decision on a held-out participant? Separately,
does the reported spatial set include locations of measured SEEG-responsive
contacts? This is a model-conditional observability question with sparse
positive corroboration. It is not complete source reconstruction or
ground-truth family identification.

## Candidate contributions, ranked

### 1. Source-family spatial ambiguity audit

**Object:** A set/range of frozen spatial functionals (e.g. cortical-parcel
source mass or support diameter) compatible with the held-out participant's
measured scalp field within a training-calibrated tolerance, with finite
forward-model stress results shown separately. For the current release this
is in-observation compatibility, not independent scalp-response prediction.

**Closest work:** Set-membership inverse solutions, resolution/fidelity maps,
Bayesian uncertainty including SESAMEEG's posterior alternatives, DeESI's
variance-based inference, source-location confidence intervals, Phee et al.'s 2026
conformal EEG localization, and Skaf–Boyd near-optimal-set geometry. XDL-ESI
already analyzes averaged WSGZP CCEPs and displays a source-extent comparison
against the stimulation site; graph-Fourier filters already target spatial
extent. The set-intersection mathematics is standard.

**Potential value:** A researcher-facing report that shows when materially
different, defensibly constrained source families remain equally compatible
with a held-out participant's measured CCEP scalp field, and whether that
changes a predeclared focal-versus-ambiguous reporting decision. This is an
in-observation fit unless valid independent repetitions are established.

**Falsifier:** The family ambiguity is already demonstrated in close prior
work, does not recur across held-out participants, is explained by noise,
model error or implant sampling, or has no external decision value beyond
single-map/resolution baselines. If exact direct fitting returns the same
identified set, that is expected and rules out a distinct set algorithm
unless a certified guarantee or computational advantage is shown. Do not use
between-half instability without a documented independent split.

**Novelty status:** plausible decision-support software contribution; novelty
not established.

### 2. Calibrated source-family identity classifier

**Object:** A confidence score that selects point, patch, distributed or
multi-patch explanations.

**Closest work:** The families overlap/nest, and the measurements do not label a
true whole-cortex family. Residual ordering cannot create an identifiable
target.

**Falsifier:** Already falsified as a true-family claim by the nesting and
absence of labels.

**Decision:** Reject. Do not implement as a classifier of physiological truth.

### 3. Continuous robust certificate over forward uncertainty

**Object:** A mathematically valid lower/upper bound on the spatial ambiguity
set for every conductivity, sensor placement and orientation inside a
continuous bounded uncertainty region.

**Closest work:** Robust inverse problems, forward-model uncertainty, and
existing interval/posterior methods. A sampled grid is not a continuous bound.

**Potential value:** A stronger guarantee if the forward map can be bounded
and the solver yields certified extrema.

**Falsifier:** Bounds are too loose to change the decision, or their
computational cost makes the full participant model unusable.

**Novelty status:** high effort; do not choose before the forward model and
measured baseline are established.

## Candidate-by-candidate novelty test

| Candidate | Exact object and bounded claim | Closest work / required novelty delta | Proof and evaluation required | Cost, use, data and falsifier |
|---|---|---|---|---|
| **1. Source-family ambiguity audit** (empirical question; not yet a method contribution) | For a held-out participant's measured scalp response, report the set/range of a frozen spatial functional compatible with prespecified source families and forward scenarios. This is an in-observation compatibility analysis, not independent scalp prediction or recovery of the biological generator. | Set-membership inverse problems, Skaf–Boyd near-optimal solution-set geometry, spatial-fidelity / PSF / CTF analyses, SESAMEEG posterior alternatives, DeESI variance-based inference, conformal regions, and source-extent methods are close. XDL-ESI already analyzes averaged WSGZP CCEPs and displays a source-extent comparison against the stimulation site; graph-Fourier methods already target extended source regions. A possible empirical contribution is a reproducible participant-held-out finding about family-dependent ambiguity beyond those outputs. | Freeze the functional, family constraints, calibration rule and focal-vs-ambiguous action before evaluation. Do not split averaged responses unless valid independent repetitions are documented. Compare participant-held-out reports with GBF, XDL-ESI (or record why a matched reproduction is impossible), SESAMEEG, DeESI, and graph-Fourier extent methods where the data and source model permit. Treat the 2026 transformer as prior art only; its synthetic benchmark is outside this project's evidence rules. Direct constrained fitting over the exact same feasible set is an equivalence oracle: same report is expected; a new algorithm must add a proved guarantee or certified cost/tightness advantage, not a different answer. SEEG positive-contact concordance is secondary and cannot prove true-source coverage. | Moderate to high cost after valid forward models exist. Use: show when focal display is sensitive to source-family assumptions. Needs WSGZP measured CCEP, reviewed coordinates, individual forward/covariance and a valid held-out external endpoint; no signal access until the freeze. Falsified as a new finding if ambiguity is absent, explained by noise/model error/sampling bias, already reported in close literature, or does not change interpretation relative to standard outputs. Otherwise the result may remain useful software. |
| **2. Continuous-forward-uncertainty outer certificate** (possible method contribution; highest mathematical risk) | Compute sound lower/upper bounds on the source-family compatibility set for every lead field in a stated continuous uncertainty region, rather than testing a finite grid. Candidate output: a guaranteed outer spatial range or certified family exclusion, with numerical error accounted for. | Robust inverse problems, interval analysis, robust optimization, Skaf–Boyd near-optimal sets and set-valued recovery already cover much of this territory. A novelty claim requires an exact theorem/algorithmic step not reducible to these methods, not merely replacing a grid with more samples. | Derive a bound preserving source-family disjunctions and shared physical-parameter coupling; prove enclosure validity over the full uncertainty set; independently replay numerical bounds; benchmark against direct fitting as the exact-answer oracle and established interval/branch-and-bound relaxations. The new solver must preserve the oracle's answer while showing a meaningful certified cost/tightness advantage or a stronger guarantee. Include adversarial and degenerate cases. | High to potentially prohibitive cost; branch-and-bound or interval methods can scale poorly across ~8k cortical sites and multiple families. Use: certify that a source report survives plausible sensor/coregistration/conductivity error. Needs validated participant lead field and defensible uncertainty bounds. Falsified if bounds are vacuous, runtime is unusable, or no certified advantage over standard methods appears. Do not implement as the headline until a written reduction identifies a true gap. |
| **3. Family-identity classifier** (rejected) | Predict which source family generated an event. | Families overlap or nest, and WSGZP lacks a complete label for the distributed generator. A lower residual only ranks model fit; it does not identify truth. | Would require independent source-family truth labels and calibrated error, not available in the current route. | Could be computationally cheap and superficially attractive, but the target is not identifiable from current labels. Already rejected: do not build or claim as neural-family discovery. |

### Current novelty decision

No candidate currently passes a novelty gate. Candidate 1 is the best
**testable scientific question** but may end as a careful empirical extension
or useful software. Candidate 2 is the only current route to a distinct
**mathematical method**, but its relevant theory is close to established
robust inverse/set-membership work and the computational burden is unknown.
Candidate 3 is not supportable with the available labels. Keep Candidate 1
as the next evaluation target only if the exact prior-art comparison and
measured-data gates pass; do not present it as a proven novelty direction.

The physiology of the candidate source families is itself a gate. A
mathematically convenient family (for example, arbitrary signed coefficients
inside local patches) is not a defensible physiological alternative without
evidence. Prior single-sign-per-patch results are family-sensitivity
diagnostics only. Before treating those families as plausible, tie each to
published source-physiology evidence and test reasonable alternative
orientations, polarity rules, patch sizes, cortical area weights and temporal
constraints. If no family set can be defended, pivot the biological claim
while preserving the software and numerical work.

The initial literature-grounded family definitions are now recorded in
`SOURCE_FAMILY_PHYSIOLOGY_REVIEW_20261028.md`. The literature supports testing
contiguous geometry-aware patches, cortical-normal orientations and
cancellation across folds; it does not establish a true family for WSGZP CCEPs.
The proposed coherent-patch, multi-patch and unrestricted signed models remain
candidate alternatives until held-out participant compatibility and external
concordance/sensitivity checks are completed. Do not call an in-observation
fit a held-out prediction.

## Provisional route

Keep Candidate 1 as the only live empirical question, but label it
**promising, not novel**. First build and verify participant-specific forward
models. Then freeze the run-average response representation, response window,
good-channel contract, source-support functional, held-out participant
decision rule and baselines. The held-out scalp response is the inference
input, not an independent prediction target. The outer split is
participant-level leave-one-out; all global threshold selection stays within
training participants. WSGZP's sparse SEEG responses are secondary positive
corroboration only.

Before calling the result a new method, require a theorem or independently
replayed certified computational advantage over direct constrained fitting
of the same identified set, with matched assumptions and numerical accuracy.
Agreement with that oracle is expected. A separate empirical-finding claim
must survive comparison with GBF, MNE/dSPM/eLORETA/LCMV, matched patch methods,
resolution/fidelity analyses and the MRI-informed conformal comparator, and
show a previously unreported, reproducible measured phenomenon with a clear
researcher interpretation. Different residuals or narrower sets alone are
insufficient.

If forward models cannot be built from the available MRIs/coordinates, stop
before signal fitting. If baselines make equivalent held-out decisions, report
`VALIDATED SOFTWARE CONTRIBUTION` unless a distinct empirical finding survives
its own prior-art and measurement tests; if the measured endpoint cannot
support the claim, report `PIVOT`. Never describe repeatability coverage as
coverage of the true physiological source.

## Proof standard for a novelty claim

Novelty is an outcome to test, not an objective that licenses relabeling known
math. We need to distinguish three possible end states:

### New method

This requires a specific algorithmic or mathematical step absent from the
closest source-imaging, set-membership, near-optimal-set, patch-sparsity and
convex-union work. Write the exact estimand and equations, prove the claimed
guarantee (including all admitted source families and forward-model
uncertainty), and independently replay its certificates. Compare with direct
constrained fitting of the same object as an equivalence oracle, plus GBFs,
PSF/CTF and matched patch methods. The new method should return the oracle's
answer while providing a meaningful certified complexity/runtime/tightness
gain or a genuinely stronger guarantee. A different answer caused by changed
assumptions is not an advantage. Different residuals, a larger candidate set,
a calibration wrapper or a new name do not meet this bar.

### New empirical finding

This would not be a new algorithm. The leading candidate is a replicated,
participant-held-out finding that materially different, defensibly
constrained source families remain compatible with measured late-CCEP scalp
fields and that this ambiguity affects interpretation for a prespecified
subset of cases. Participant-held-out evidence within WSGZP is not an
independent-cohort replication. Without independent same-condition repetitions, compatibility
is an in-observation fit, not held-out prediction. This is an empirical
conditional-observability result, not a new method or proof of the true
generator. Positive SEEG-contact capture at matched cortical area may serve
only as sparse corroboration. The WSGZP
data paper explicitly proposes source-localization comparisons on the
released data, the 2026 GBF study already performs stimulation-site
localization on iES-CCEP and analyzes N1/N2 propagation, and XDL-ESI estimates
source extents from averaged CCEPs on the same cohort. Therefore EEG-to-SEEG
concordance, source extent, GBF application, or contact overlap alone cannot establish
novelty. See `NOVELTY_PROOF_PLAN_20261028.md` for the close-prior-art delta and
falsification criteria. SEEG remains sparse positive evidence;
nonresponsive or unsampled tissue is not a whole-cortex negative label, and
the stimulation contact is not the unique generator of a later response.

### Validated software contribution or pivot

If exact direct fitting gives the same identified set, that rules out a new
identified-set algorithm unless it adds a certified computational or
guarantee advantage; it does not by itself erase a distinct empirical
finding. If established single-map/resolution methods yield the same measured
interpretation and no previously unreported phenomenon remains, the honest
result is a reproducible researcher tool with bounded claims or a pivot. The
current evidence is still at this
stage of uncertainty: there is no signal-level result, no valid participant
forward model, and no measured-data advantage. Novel-method status is
**unproven**.

## Decisive sequence

1. Finish metadata and provenance freezes, including the baseline/scale
   discrepancy and participant-grouped folds; do not open signal values
   before the lock.
2. Clear participant-specific coordinates and forward models, then run the
   frozen source families against matched baselines. Keep each WSGZP
   participant's sessions, runs and events in one outer fold.
3. Score the prespecified observability outcome: whether materially different
   source supports remain compatible with the held-out participant's measured
   scalp field under a training-calibrated tolerance and bounded forward
   scenarios. This is an in-observation fit. Keep fit residual, set size,
   stability and sparse positive SEEG-contact concordance separate; do not
   call them source truth, sensitivity or specificity.
4. Ask whether the ambiguity changes interpretation relative to single-map
   GBF, patch or resolution methods. Treat exact direct constrained fitting as
   an equivalence oracle for the same identified set; require certified
   computational/guarantee gain for a new algorithm. If no empirical finding
   or method advantage survives its appropriate test, stop the novelty claim.
5. Only after an empirical gap survives, decide whether a new theorem or
   solver is needed. A neural network is not required; any ML component must
   beat a matched classical method while preserving the stated guarantee.

## 28 October prior-art update: robust operator uncertainty

Candidate 2 is weaker than the initial ranking suggests. Bekri, Juditsky and
Nemirovski already study robust linear/polyhedral recovery when the observation
matrix is uncertain, while Juditsky and Nemirovski treat functional recovery
over finite unions of convex sets and a 2026 preprint treats linear-image
recovery for sparse signals. The combination does not automatically solve the
exact EEG identified-set problem, but it rules out presenting “continuous
forward uncertainty + sparse/patch source family” as the innovation without a
formal reduction showing what these methods fail to provide. Candidate 2 is
therefore **not implementation-ready as a novelty claim**. First compare the
exact output and guarantee branch-by-branch with those results, then implement
only a distinct remaining step. See
`PRIOR_ART_OPERATOR_UNCERTAINTY_AUDIT_20261028.md` and the updated
`NOVELTY_PROOF_PLAN_20261028.md`.
