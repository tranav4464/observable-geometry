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

The certificate must be calibrated against independent measured references and
must beat direct constrained fitting, GBF, PSF/CTF and established inverse
methods on a predeclared decision. If it does not, the final result is a
validated software contribution, not a novel method.

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

Our defensible gap is narrower: **measuring and calibrating when the scalp
measurement cannot distinguish competing source families**, then exposing that
uncertainty as a researcher-facing decision rather than returning one
apparently precise inverse map.

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
* the stimulation contact gives a predeclared spatial reference;
* repeated sessions and stimulation parameters permit held-out testing;
* the post-artifact CCEP provides a measured neural response, not only a
  mathematically injected signal;
* the dataset is large enough for participant-level hierarchical calibration.

Risks:

* stimulation is an intervention, not spontaneous cognition;
* the contact midpoint is not a complete neural source map;
* the 2026 GBF paper already uses this resource, so our estimand and decision
  must be different;
* OSF/EBRAINS terms and access must be checked before downloading or
  redistributing any files.

### 2. External endogenous validation: HDEEG-IED-SurgOutcome

Official identifier: EBRAINS DOI `10.25493/B3B8-XPM`; Vorderwülbecke et al.,
*Scientific Data* 2025, DOI `10.1038/s41597-025-05740-z`.

The dataset contains 45 patients with pharmacoresistant focal epilepsy,
individual structural MRI, 257-channel EEG averages of interictal discharges,
postsurgical imaging, and 12-month surgical outcomes. Thirty patients had
favourable outcomes. It is a strong endogenous clinical endpoint for testing
whether an ambiguity-aware report avoids false confident localization and
whether accepted localizations agree with the resection/epileptogenic zone.

Risks:

* surgical outcome is an indirect reference, not a full neural ground truth;
* the data are averaged IEDs rather than simultaneous scalp/iEEG trials;
* the dataset has already been used for source-localization benchmarking;
* EBRAINS registration and terms of use must be respected.

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
  spike epochs, but released contact coordinates and individual forward-model
  inputs are insufficient for the primary geometry test.
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
3. the set of families whose residuals are within a calibrated tolerance;
4. the spatial support shared by all surviving families;
5. an **ambiguous/unique/unsupported** decision.

Calibration is performed only on training participants. The tolerance is learned
from held-out stimulation or endogenous reference outcomes, with participant-
level resampling and no event-level leakage. A candidate certificate is useful
only if its advertised coverage and selective error are met on unseen
participants.

This extends the current GBF audit by preserving source-family disjunctions
and forward uncertainty instead of collapsing them into one unconstrained L1
ball. The mathematical ingredients must be attributed correctly: whitened
least squares, convex fitting, weak duality, Gaussian testing, resolution
matrices and conformal/calibration ideas are established. The possible new
step is the **validated decision protocol that calibrates family-level
observability against an independent spatial reference**, not a claim that any
individual optimization primitive is new.

## Three candidate contribution levels

### Candidate A: Calibrated Family-Observability Certificate

**Object:** calibrated set of plausible source families plus an abstention
decision under forward uncertainty.

**Closest prior art:** GBF source imaging, PSF/CTF and resolution matrices,
source-fidelity evaluation, empirical Bayesian forward uncertainty, and
conformal/calibration work. These are direct threats to novelty.

**Required evidence:** held-out participant coverage, selective localization
error, false-confidence rate, and a decision comparison against direct fitting,
MNE/dSPM/eLORETA/LCMV, GBF-only output and established patch methods.

**Falsifier:** direct fitting or a standard resolution metric gives the same
  ambiguity decisions and equal or better calibration; the candidate becomes a
  software/workflow contribution only.

**Rank:** best candidate, but novelty is conditional and must be earned by the
  measured decision result.

### Candidate B: Cross-participant source-family transfer benchmark

**Object:** a reproducible benchmark showing whether nominal ambiguity scores
  predict source-family disagreement and source-reference error across
  participants and stimulation parameters.

**Closest prior art:** the 2026 GBF paper, source-fidelity frameworks, and
  existing iES-CCEP localization studies.

**Falsifier:** no association after participant-level holdout, or identical
  decisions from standard PSF/CTF metrics.

**Rank:** high publication and software value, but more likely a benchmark
  contribution than a new method.

### Candidate C: Observability-aware sensor-design recommendation

**Object:** choose electrode subsets or montage changes that reduce the
  calibrated family ambiguity for a stated source pair or region.

**Closest prior art:** optimal sensor placement, resolution kernels and
  experimental-design methods.

**Falsifier:** standard sensor-density or resolution optimization makes the
  same recommendations.

**Rank:** defer until Candidate A produces a validated ambiguity measure.

## Locked execution protocol

### Stage 0: data and prior-art freeze

1. Download only metadata and one pilot subject from WSGZP and
   HDEEG-IED-SurgOutcome.
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
* map the stimulation contact pair and the HDEEG surgical reference into the
  same surface coordinate system;
* quantify transform, conductivity and sensor-position perturbations;
* publish a machine-readable manifest and independent replay.

### Stage 2: primary measured-source test

Use iES-CCEP only after the Stage 0 lock:

* exclude the direct pulse-artifact interval;
* define a post-stimulation CCEP window from the published timing contract;
* extract scalp topographies and independent SEEG response features;
* compute point, uniform, smooth, signed, flexible and multi-patch fits;
* compute the candidate observability certificate;
* hold out entire sessions or participants, never random trials from the same
  stimulation condition;
* evaluate spatial error to the stimulated pair, response agreement with SEEG,
  family ambiguity, selective risk and calibration coverage.

### Stage 3: endogenous external test

Use HDEEG-IED-SurgOutcome as an external endpoint:

* fit all thresholds and calibration parameters on a training subset;
* evaluate accepted versus abstained localization decisions on held-out
  participants;
* compare against surgical resection/12-month outcome labels;
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

Predeclare one decision: for example, *when should the system abstain from a
unique source attribution?* A method passes the novelty gate only if it reduces
false confident attribution at matched coverage, or supplies a validated
guarantee/calibration that baselines do not.

### Stage 5: ML role, only if justified

Do not add a neural network by default. If calibration is unstable across
participants, use a small hierarchical model to estimate calibration parameters
from training participants. The ML component must:

* use participant-level splits;
* output calibration parameters or risk estimates, not an opaque source map;
* be compared against a non-ML pooled and per-participant calibration;
* preserve the deterministic certificate and its failure states;
* be rejected if it improves only in-sample prediction or hides ambiguity.

## Novelty gate and final outcomes

The project must end in exactly one of these classifications:

1. **Novel method supported:** the calibrated family certificate changes a
   predeclared held-out decision or provides a validated guarantee beyond all
   baselines.
2. **Promising but unverified:** constructed-field or limited measured results
   are encouraging but independent source-reference evidence is insufficient.
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

Proceed with **WSGZP iES-CCEP as the primary dataset** and
**HDEEG-IED-SurgOutcome as external endogenous validation**. Keep Localize-MI
and ds004752 as completed controls. Do not claim that this route is likely to
produce a new mathematical theorem. It has a realistic chance of producing a
novel, validated researcher-facing decision framework only if the held-out
certificate changes the confidence/abstention decision beyond direct fitting
and standard resolution diagnostics. Otherwise the correct high-quality result
is a reproducible, empirically validated software contribution.

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
