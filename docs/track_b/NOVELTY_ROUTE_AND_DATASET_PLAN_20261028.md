# Observable Geometry: measured-source validation and novelty route

## Executive decision

The current software build is useful, but the present evidence cannot support
either endogenous source recovery or a novel GBF claim. The strongest next
route is not to invent another inverse solver. It is to test and, if justified,
implement a **calibrated source-family observability certificate**:

> Given a measured scalp field, a participant-specific forward model, a
> declared source family and a bounded forward-model uncertainty set, report
> which source families remain observationally indistinguishable, and abstain
> from a unique attribution when the measured data cannot support one.

The full requested certificate requires a defensible calibration target and
independent measured references. The current WSGZP and HDEEG endpoints do not
provide labels for complete source-family coverage. No calibration or novelty
advantage is established. Preserve the full target while seeking an adequate
reference; do not silently relabel contact capture or surgical concordance as
source coverage. Compare against direct constrained fitting, GBF, PSF/CTF and
established inverse methods. If the required target cannot be validated, say
so explicitly and classify the result within the stated outcome categories.

## Non-synthetic-data rule

The primary novelty and validation analyses will use **measured recordings
only**. We will not inject simulated neural signals into scalp data, generate
synthetic EEG/iEEG trials, or present forward-model-generated observations as
physiological evidence. The measured inputs will be scalp EEG plus the
independent reference available for the selected endpoint: post-artifact CCEP
responses and SEEG in iES-CCEP, or endogenous interictal EEG with surgical
outcome in HDEEG-IED-SurgOutcome.

Forward models are still necessary because the research question concerns what
source families could have produced each measured scalp field. Therefore,
model-generated candidate fields may be used as **hypotheses and fit terms**,
not as observations. Synthetic or algebraic cases may remain in unit tests,
solver regression tests and numerical-error checks, but they must be stored in
a separate evidence class and cannot be used to calibrate thresholds,
demonstrate source-recovery accuracy, or support the novelty claim.

## Why the original GBF idea is no longer a novelty route

A 2026 *Nature Biomedical Engineering* paper already presents participant-
specific geometric basis functions for EEG/MEG source imaging and validates
GBF on meta-source benchmarks, task EEG, resting-state networks, intracranial
stimulation and epilepsy data. It also releases code and names the iES-CCEP
and HDEEG-IED-SurgOutcome datasets. Therefore the following are not new claims:

* using cortical Laplace–Beltrami eigenmodes as an anatomical basis;
* applying GBFs to source reconstruction;
* demonstrating GBF on intracranial stimulation;
* showing that geometric modes can compactly represent source activity.

The candidate gap is narrower: **quantify, under explicit assumptions, when a
scalp measurement cannot distinguish competing source families**, then test
whether exposing that ambiguity changes a researcher decision beyond existing
methods. Whether this can be calibrated against an adequate measured reference
is unresolved; calibration is not assumed available from WSGZP or HDEEG.

## Dataset ranking

### 1. Primary: iES-CCEP / WSGZP

Official identifiers: DOI `10.17605/OSF.IO/WSGZP`; EBRAINS DOI
`10.25493/EF4K-HJH`; related paper Parmigiani et al., *Brain Stimulation*
2022, DOI `10.1016/j.brs.2022.04.007`.

Reported contents are simultaneous 256-channel high-density scalp EEG and SEEG,
individual pre-implant MRI, digitized scalp-electrode positions, intracranial
contact coordinates, synchronized stimulation triggers, and 323 sessions from
36 epilepsy patients. Intracranial single-pulse stimulation varies intensity,
pulse width, contact geometry and cortical location. The later response is a
physiological cortico-cortical evoked response, while the earliest pulse
interval must be treated separately as stimulation artifact.

Why it is the best primary dataset:

* individual geometry and forward models can be reconstructed;
* the stimulation contact is a spatial reference for the intervention site,
  not a complete label for the generator of a later distributed CCEP;
* repeated sessions and stimulation parameters permit held-out testing;
* the post-artifact CCEP provides a measured neural response, not only a
  mathematically injected signal;
* 36 participants may support participant-grouped evaluation, but the sparse
  positive SEEG labels do not calibrate whole-cortex source-set coverage or
  correctness of the `unique / ambiguous / unsupported` label.

Risks:

* stimulation is an intervention, not spontaneous cognition;
* the contact midpoint is not a complete neural source map;
* post-artifact responsive SEEG contacts are sparse positives, not a complete
  source map or verified negatives;
* the 2026 GBF paper already uses this resource, so our estimand and decision
  must be different;
* OSF/EBRAINS terms and access must be checked before downloading or
  redistributing any files.

### 2. External endogenous validation: HDEEG-IED-SurgOutcome

Official identifier: EBRAINS DOI `10.25493/B3B8-XPM`; Vorderwülbecke et al.,
*Scientific Data* 2025, DOI `10.1038/s41597-025-05740-z`.

The public dataset record lists 45 patients; the 2025 data descriptor analyzes
44 after exclusions. They have pharmacoresistant focal epilepsy,
individual structural MRI, 257-channel EEG averages of interictal discharges,
postsurgical imaging, and 12-month surgical outcomes. Thirty patients had
favourable outcomes. It is an endogenous clinical-concordance resource for
testing whether prespecified EEG spatial summaries associate with resection
and outcome. It does not supply event-matched direct source truth and cannot
by itself calibrate false-confident attribution or whole-cortex set coverage.

Risks:

* surgical outcome is an indirect reference, not a full neural ground truth;
* the data are averaged IEDs rather than simultaneous scalp/iEEG trials;
* the dataset has already been used for source-localization benchmarking;
* project-specific EBRAINS access has not been granted; and
* this dataset can support clinical concordance analysis, not calibration of
  event-level source coverage or a whole-cortex ambiguity label.

### 3. Existing bounded controls retained in this project

* **Localize-MI:** real scalp EEG, individual forward models and known
  stimulation contacts. The current run is a pulse-artifact diagnostic and is
  retained as a negative/control endpoint, not as endogenous validation.
* **OpenNeuro ds004752:** simultaneous scalp EEG and stereo-EEG from 12
  participants. It is already a valid cross-session scalp-to-contact
  prediction benchmark, but lacks the individual-forward-model contract for
  the GBF estimand.

### 4. Lower-priority alternatives

* `nm000513` has seven patients and 1,945 simultaneous scalp/SEEG interictal
  spike epochs, but the released SEEG contact coordinates are `n/a`, and the
  same cohort was analyzed in 2015 and 2023. It cannot serve as independent
  participant-specific spatial validation as released. See
  `MEASURED_SOURCE_REFERENCE_DATASET_REVIEW_20261029.md`.
* `on004752` has 15 patients, scalp EEG, iEEG and MNI contact coordinates, but
  its 10–20 scalp montage and missing verified individual forward-model
  contract make it a secondary transport benchmark, not the primary source
  certificate dataset.
* `nm000456` is a large scalp/SEEG clinical resource, but its access burden,
  geometry contract and endpoint must be audited before selection.

## Proposed method, stated as a candidate rather than a claim

For a participant-specific leadfield `G_theta`, covariance `Sigma`, measured
field `y`, source family `F` and forward uncertainty set `U`, define:

```text
r_F(y) = min over theta in U and x in F
         || Sigma^(-1/2) (y - G_theta x) ||_2
```

For competing families `F1, ..., Fk`, report:

1. the residual for each family;
2. the residual gap between the best and competing families;
3. the set of families whose residuals are within a **prespecified fit
   tolerance**; call this calibrated only after its target, null distribution
   and participant-level calibration design are justified;
4. the spatial support shared by all surviving families;
5. an **ambiguous/unique/unsupported** decision.

Any calibration is performed only on training participants. A residual/noise
compatibility threshold must be calibrated for the residual event after
family, source-parameter and forward-uncertainty optimization. A threshold
learned from sparse SEEG positives or intervention/resection labels does not
calibrate whole-cortex source coverage. WSGZP's positive-contact capture and
HDEEG's resection/outcome concordance are distinct bounded endpoints; neither
validates the biological source set. The current calibration identifiability
and data-reference audits are in
`CALIBRATION_IDENTIFIABILITY_AUDIT_20261029.md` and
`MEASURED_SOURCE_REFERENCE_DATASET_REVIEW_20261029.md`.

A candidate certificate is useful only if its precisely named target and
decision value are evaluated on unseen participants. If no valid source
coverage labels are available, do not report source coverage or selective
error for true neural attribution.

This candidate keeps source-family disjunctions and forward uncertainty
explicit. That object combination is not automatically a contribution: its
mathematical ingredients, including whitened least squares, convex fitting,
weak duality, Gaussian testing, resolution matrices and set-valued/calibration
ideas, are established. The only possible contribution is a rigorously
validated new guarantee or a predeclared researcher decision benefit beyond
matched methods. Current data do not yet support calibration of whole-cortex
family observability.

## Three candidate contribution levels

### Candidate A: Calibrated Family-Observability Certificate

**Object:** calibrated set of plausible source families plus an abstention
decision under forward uncertainty.

**Closest prior art:** GBF source imaging, PSF/CTF and resolution matrices,
source-fidelity evaluation, empirical Bayesian forward uncertainty, and
conformal/calibration work. These are direct threats to novelty.

**Required evidence:** a valid source-reference target for coverage and
selective localization error, plus a decision comparison against direct
fitting, MNE/dSPM/eLORETA/LCMV, GBF-only output and established patch methods.
The currently reviewed WSGZP/HDEEG labels do not supply that whole-cortex
target, so Candidate A cannot yet be calibrated as specified.

**Falsifier:** direct fitting or a standard resolution metric gives the same
  ambiguity decisions and equal or better performance for the exact supported
  target; the candidate becomes a software/workflow contribution only.

**Rank:** best candidate, but novelty is conditional and must be earned by the
  measured decision result.

### Candidate B: Cross-participant source-family transfer benchmark

**Object:** a reproducible benchmark showing whether nominal ambiguity scores
  predict source-family disagreement and a clearly bounded measured endpoint
  across participants and stimulation parameters. WSGZP can supply sparse
  positive-contact capture, not complete source-reference error.

**Closest prior art:** the 2026 GBF paper, source-fidelity frameworks, and
  existing iES-CCEP localization studies.

**Falsifier:** no association after participant-level holdout, or identical
  decisions from standard PSF/CTF metrics.

**Rank:** high publication and software value, but more likely a benchmark
  contribution than a new method.

### Candidate C: Observability-aware sensor-design recommendation

**Object:** choose electrode subsets or montage changes that reduce a
  model-conditional family-ambiguity measure for a stated source pair or
  region. It is not a calibrated source-truth claim unless a valid target is
  supplied.

**Closest prior art:** optimal sensor placement, resolution kernels and
  experimental-design methods.

**Falsifier:** standard sensor-density or resolution optimization makes the
  same recommendations.

**Rank:** defer until Candidate A produces a validated ambiguity measure.

## Locked execution protocol

### Stage 0: data and prior-art freeze

1. Preserve the completed WSGZP acquisition and metadata-only audit. Do not
   download HDEEG signals unless its legitimate access gate is granted.
2. Verify license, checksums, MRI-to-sensor transforms, contact coordinates,
   trigger timing, reference, filtering and forward-model reproducibility.
3. Build an equation-level overlap matrix against the 2026 GBF paper,
   Mikulan/Parmigiani, Zauli, Unnwongse, Samuelsson, Le Cam, and standard
   resolution and patch methods.
4. Freeze the primary estimand, source families, artifact exclusion window,
   CCEP window, split, metrics and calibration rule before reading held-out
   outcomes.

### Stage 1: geometry and reference audit

For every included participant:

* reconstruct the individual head model and average-reference leadfield;
* verify channel order, orientation, source coordinates and covariance rank;
* map the stimulation pair and any HDEEG resection reference into the same
  surface coordinate system, while keeping intervention and clinical outcome
  distinct from a measured CCEP generator;
* quantify transform, conductivity and sensor-position perturbations;
* publish a machine-readable manifest and independent replay.

### Stage 2: primary measured-source test

Use iES-CCEP only after the Stage 0 lock:

* exclude the direct pulse-artifact interval;
* define a post-stimulation CCEP window from the published timing contract;
* extract scalp topographies and independent SEEG response features;
* compute point, uniform, smooth, signed, flexible and multi-patch fits;
* compute the candidate observability certificate;
* keep every session, run and event from one participant in the same outer
  fold; never use event-level or run-level splits as participant holdout;
* report stimulation-site localization only for the stimulation artifact or
  another endpoint explicitly validated against that intervention site;
* for later CCEPs, report model-conditional family compatibility and a
  separately defined sparse positive-contact capture endpoint;
* do not report source-reference error, calibrated source coverage or
  false-confident attribution from those sparse positives.

### Stage 3: endogenous external test

Use HDEEG-IED-SurgOutcome as an external endpoint:

* fit all thresholds and calibration parameters on a training subset;
* evaluate a predeclared EEG-to-resection/outcome concordance endpoint on
  held-out participants, if access is granted;
* do not call concordance source coverage, event-level localization error or
  false-confident attribution;
* report temporal/extratemporal strata and the effect of channel density;
* treat surgical outcome as an indirect reference, not absolute truth.

### Stage 4: baselines and falsification

The same participant splits must be used for:

* direct constrained fitting;
* GBF-only inverse reconstruction;
* MNE, dSPM, eLORETA and LCMV where valid;
* PSF/CTF or empirical resolution matrices;
* uniform, smooth and established patch families;
* the candidate certificate.

Predeclare one decision and its evidence class. A false-confident-attribution
rate requires a defensible source reference. With WSGZP's current labels, a
possible bounded decision is fixed-area follow-up prioritization measured by
sampled-positive-contact capture. A method passes the novelty gate only if it
adds a valid guarantee or improves that predeclared held-out decision beyond
matched baselines; a weaker endpoint must not be represented as source
coverage.

### Stage 5: ML role, only if justified

Do not add a neural network by default. If calibration is unstable across
participants, use a small hierarchical model to estimate calibration parameters
from training participants. The ML component must:

* use participant-level splits;
* output calibration parameters or risk estimates only for a supported target,
  such as sampled-positive-contact capture, not whole-cortex source coverage;
* be compared against a non-ML pooled and per-participant calibration;
* preserve the deterministic certificate and its failure states;
* be rejected if it improves only in-sample prediction or hides ambiguity.

## Novelty gate and final outcomes

The project must end in exactly one of these classifications:

1. **Novel method supported:** a mathematically valid, target-specific
   calibrated family certificate changes a predeclared held-out decision or
   provides a validated guarantee beyond all baselines. This requires a
   source-reference dataset that supports the calibration target.
2. **Promising but unverified:** limited measured results or formal results are
   encouraging, but independent source-reference evidence is insufficient.
3. **Validated software contribution:** the workflow is reproducible and useful,
   but direct baselines make equivalent decisions.
4. **Pivot:** the endpoint, geometry or calibration fails and no defensible
   decision remains.

The plan must not be declared successful merely because the candidate method
produces different numbers. A difference matters only if it improves a
predeclared researcher decision under held-out measured evidence.

## Required deliverables

* `DATASET_ACCESS_AND_PROVENANCE.md`
* `PRIOR_ART_EQUATION_MATRIX.md`
* frozen protocol and hash manifest;
* participant-level preprocessing and leakage audit;
* runnable implementation and independent verifier;
* machine-readable per-event and per-participant outputs;
* calibration and selective-risk report;
* baseline comparison report;
* plain-language claim ledger;
* final classification and explicit laboratory data request if the public data
  are insufficient.

## Current recommendation

Retain **WSGZP iES-CCEP as the required primary route**, subject to its open
protocol, coordinate and preprocessing gates. Treat HDEEG only as a possible
external clinical-concordance route if legitimate access is granted; do not
call it source truth. Keep Localize-MI and ds004752 in their declared control
roles. Current evidence does not establish a novel theorem, method, or
validated decision framework. The strongest present route is to first resolve
whether the required source-space calibration target can be supplied. If it
cannot, explicitly report that the full certificate objective was not
validated; do not substitute a weaker result without stating the limit.

## Source records

* Nature Biomedical Engineering 2026 GBF framework:
  https://doi.org/10.1038/s41551-026-01664-0
* iES-CCEP / WSGZP dataset: https://doi.org/10.17605/OSF.IO/WSGZP
* Parmigiani et al. 2022: https://doi.org/10.1016/j.brs.2022.04.007
* Mikulan et al. 2020 Localize-MI: https://doi.org/10.1038/s41597-020-0467-x
* HDEEG-IED-SurgOutcome: https://doi.org/10.25493/B3B8-XPM
* Vorderwülbecke et al. 2025: https://doi.org/10.1038/s41597-025-05740-z
* Zauli et al. 2024 HDEEG/SEEG: https://doi.org/10.1016/j.jneumeth.2024.110193
* Unnwongse et al. 2023: https://doi.org/10.1093/braincomms/fcad023
* Samuelsson et al. spatial-fidelity framework:
  https://doi.org/10.3389/fnins.2020.00311
* Le Cam et al. forward-model uncertainty:
  https://doi.org/10.1016/j.neuroimage.2017.03.030
