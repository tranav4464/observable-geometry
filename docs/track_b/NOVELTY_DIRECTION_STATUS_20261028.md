# Observable Geometry novelty direction: evidence status

**Status:** candidate research question; no novel method supported yet
**Scope:** source-family sensitivity and measured-data validation; metadata and
MRI geometry only in this update, with no EEG/SEEG samples read

**Execution state (29 October 2026):** `GATE_REGISTER.json` marks B4–B7
PIVOT. The proposed held-out WSGZP contact-prioritization comparison is not an
active or authorized analysis; it is only a possible reopening route. The
current build therefore has no measured-data novelty result. A new coordinate
code audit narrows, but does not clear, the scalp-to-MRI provenance issue; see
`WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md`.

## Candidate direction under review

The proposed direction is a researcher-facing **source-family observability
audit**: for a measured scalp response, expose which spatial explanations
remain compatible across prespecified point, patch, smooth, distributed and
multi-patch source families, and whether a spatial statement survives stated forward-model
perturbations and shows held-out concordance with sparse positive SEEG contacts. Its useful output
would be a bounded, auditable ambiguity report rather than a single
source-location picture.

This is a credible use case, but calling it a new mathematical method is not
currently defensible. Source-family constraints substantially change the
candidate residuals in existing one-model calculations, yet the difference is
an assumption-sensitivity finding. No held-out measured-data advantage or
researcher-decision change has been demonstrated.

## Closest mathematical overlap identified

Juditsky and Nemirovski (2019; arXiv version 2018) study recovery of linear and
N-convex functionals from indirect noisy observations when the signal belongs
to a finite union of convex compact sets. Their Gaussian observation model is
`y = A x + noise`, and their N-convex class explicitly includes maxima of
fractional-linear functions. This overlaps the source-family union and
several possible spatial functionals in Observable Geometry. In particular,
a parcel-mass fraction within a fixed convex sign branch is fractional-linear
when its denominator is positive. The family-union framing, functional
estimation, and convex optimization alone therefore cannot be presented as
our invention. The paper's guarantees do not automatically cover every
discontinuous output such as support diameter or the full spatial identified
set, but any such distinction needs a theorem and a decision advantage, not a
change of wording.

Additional close prior art already identified includes:

* Srebro (1996) already searches a noise-constrained feasible set of
  physiologically plausible EEG source explanations. ESI-A* (AAAI 2023)
  already searches connected cortical supports with a provable optimum and
  reports real epilepsy EEG comparisons. These rule out “first noise-feasible
  source set” and generic “optimal connected-patch search” claims. Their
  inspected methods do not provide our exact combination of source-family
  compatibility ranges and continuous forward-operator uncertainty, but that
  difference is not a novelty claim by itself. The exact comparison is now in
  `PRIOR_ART_OPERATOR_UNCERTAINTY_AUDIT_20261028.md` and
  `NOVELTY_PROOF_PLAN_20261028.md`.

* Wen, Yang & Liu's 20 October 2026 arXiv preprint explicitly calls its EEG
  source-localization method “observability-aligned” and separates lead-field
  row-space information from null-space completion. Its learned diffusion and
  completion method is not the same object as our candidate family-wise
  compatibility report, and its recorded-data evidence is exploratory and
  narrow. It nevertheless preempts broad novelty language around observability
  decomposition or observability-aware reconstruction. Our exact delta, if
  any, must be a distinct guarantee or a held-out researcher-decision benefit
  against a fair comparison, not the row/null distinction itself.
* He et al.'s August 2026 scalp-to-intracranial review already distinguishes
  source imaging from virtual-iEEG event, feature and waveform targets, and
  separates observability, identifiability, fidelity, predictability and
  utility. A taxonomy, calibrated-uncertainty checklist or call for matched
  baselines is not a contribution by itself.
  Equation/claim-level entries and links are recorded in
  `NOVELTY_PROOF_PLAN_20261028.md`.

* GBF source localization with CCEP/stimulation validation on a closely
  related cohort;
* XDL-ESI (Jiao et al., 2024), which applies a learned source-extent estimator
  to averaged CCEPs from the same 36-participant hd-EEG/SEEG stimulation
  cohort and compares reconstructed activity with the stimulation contact.
  This is a direct threat to claims about source extent or CCEP source imaging
  on WSGZP; see the equation/endpoint comparison in
  `NOVELTY_PROOF_PLAN_20261028.md`;
* graph-Fourier source-extent methods (Yang et al., 2024), which already
  project classical estimators into low-spatial-frequency subspaces and test
  extended source estimates on synthetic EEG and real MEG. This makes
  “extended region rather than point” an occupied method objective.
* MRI-informed source localization with conformal uncertainty (Phee et al.,
  2026), which makes generic calibrated source confidence an inadequate claim;
* SESAMEEG (Luria et al., 2024), which already returns posterior source
  configurations, uncertainty maps, and competing explanations when data are
  ambiguous. A deterministic feasible set must prove a different guarantee or
  decision value, not merely display alternatives;
* DeESI (Tong et al., 2025), which adds debiased estimates, variance-based
  inference, hypothesis tests, and PSF/CTF diagnostics, and evaluates known-
  stimulation localization on the seven-participant Localize-MI dataset. This
  directly pre-empts generic known-stimulation localization claims for our
  Localize-MI control, but is distinct from the 36-participant WSGZP/iES-CCEP
  resource. Full equation and endpoint review is in
  `PRIOR_ART_DEESI_CODE_AUDIT_20261028.md`;
* Hart et al. (2026), a newly published transformer for single- and
  multi-source EEG localization under noise, electrode dropout and
  source-count variation. Its primary abstract specifies simulated training
  and evaluation data, with code/data promised for future release. It is a
  close algorithmic baseline but does not provide measured-data validation;
  it cannot meet this project's primary evidence criterion by itself;
* empirical spatial-fidelity evaluation of nonlinear and patch estimators
  (Samuelsson et al., 2021);
* comparisons of EEG source consistency across anatomical models, electrical
  models, inverse methods and implementations (Mahjoory et al., 2017);
* inverse methods that combine patch structure with leadfield/coregistration
  uncertainty (López et al., 2012).

These comparisons are recorded in the existing prior-art audits and must be
rechecked against exact estimands, not just titles. A source-family union,
repeatability threshold, perturbation grid, set-valued output, or abstention
rule by itself is not evidence of novelty.

## Evidence that does and does not support a contribution

**Supports continued investigation:** existing calculations show that
unrestricted within-patch sign changes can create a much closer competing
scalp field than a one-sign-per-patch family. This makes the physiological
definition of a source family consequential. The exact result remains
conditional on one model and tested candidate set; it does not establish which
family is physiologically correct.

**Does not yet support novelty:** direct constrained fitting yields equivalent
decisions in current cases; global multi-patch certification is not yet
scalable; the physically admissible source family is not validated; and the
WSGZP forward-model gate has not passed. No endogenous source-recovery
accuracy, calibrated true-source coverage, or external replication has been
shown.

## New gate issue: certificate construction must be independent of scoring

An additional review found that v3's interleaved A/B/C event-row assignments
do not satisfy the requested participant/session holdout. They also cannot
undo inherited rejection and ICA performed before export. Amendment v4
supersedes these row assignments for confirmatory evaluation: all runs and
events from a participant stay in one outer fold, with global tuning limited
to outer-training participants. Evaluation remains conditional on the
processed derivative and its unrecorded ICA fitting pool; it is not a
raw-to-output holdout. Amendment v4 is proposed and not locked for signal
access.

The earlier row-split manifest and verifier agree on all 36 participants,
323 EEG epoch tables and 10,088 metadata rows, but its row assignments are
historical QA only. A new metadata-only leave-one-participant-out manifest and
independent verifier now pass against the extracted derivative:
`outputs/track_b/20261028_wsgzp_participant_split/participant_grouped_manifest_v1.json`
and `verification_v1.json`. They cover all 36 participants, 323 EEG run tables
and 10,088 metadata rows, keep every participant's runs together, and report
that no BIDS session entity appears in the EEG epoch paths. No signal values
were read. This is fold-inventory verification only; it does not validate
forward geometry, a locked protocol, or outcome performance.

The temporal component has a literature/metadata-grounded candidate: use the
complete fixed 50–300 ms scalp N2 window, without choosing a per-run peak, for
an in-observation compatibility analysis. This matches the published WSGZP N2
interval and the released epoch timing while avoiding response-driven peak
selection. The participant-held-out split protects global tuning; it does not
make the same participant's measured response an independent scalp prediction
target. The paper supplement has now been retrieved and visually
checked. It describes study-level hd-EEG artifact removal, third-order
Butterworth 0.5–45 Hz filtering, epoching, trial/contact rejection, channel
interpolation, average rereferencing, baseline correction and ICA. It also
describes a separate SEEG pipeline with bipolar rereferencing and Tukey median
artifact reduction from −5 to +5 ms. This closes the gap in publication-level
method description, but not the link from those steps to the exact released
arrays: the pinned exporter calls an external loader and writes metadata, and
the supplement does not disclose the ICA fitting pool or all artifact-removal
parameters. It also reports baseline correction over −300 to −50 ms for scalp
and SEEG, with SEEG z-scoring; exporter metadata declare mean subtraction over
−300 to 0 ms and voltage units for both. This may reflect different processing
stages, but the exact saved-array baseline and scale remain unresolved.
Therefore 50–300 ms remains a fixed candidate response interval, not a
verified artifact-free window. Participant-held-out analysis under v4 would
still be conditional on the released derivative. The remaining spatial,
model and calibration gates are also open. See
`COG_TEMPORAL_ENDPOINT_CANDIDATE_20261028.md` and
`WSGZP_PREPROCESSING_PROVENANCE_20261028.md`.

## Measured-data readiness result

Metadata-only MRI/electrode overlays were rendered for `sub-01` and `sub-32`
with released scalp coordinates, NAS/LPA/RPA, SEEG contacts, true orthogonal
MRI slices and max-intensity projections. The T1w-mm-to-scanner-RAS
interpretation remains an assumption. `sub-01` shows no obvious gross
left/right reversal in the diagnostic views, but the complete registration
cannot be verified from an overlay alone. It also has 30 blank superior MRI
planes and 12/185 scalp sensors above its last positive-intensity plane;
blank margin alone does not establish cropping or validate registration.
For `sub-32`, 29/185 scalp sensors
are beyond the superior MRI FOV, and 98/185 lie above the last positive MRI
intensity plane (z=212); 43 complete superior planes remain blank before the
FOV limit. Its median-sensor axial plane has no visible anatomy. The released
MRI content may be cropped or masked superiorly, but that does not establish
the coordinate frame or transform. A frame/transform discrepancy also
remains possible. Neither explanation is resolved by this overlay. The
overlays do not clear either participant, and `sub-32` remains
a priority exclusion until source provenance or authoritative QC resolves
the issue. See
`WSGZP_OVERLAY_QC_20261028.md` and its hash manifest.

The missing original `.hpts` digitizer file and transform are a provenance
limitation, but they are not the only possible route to clearing geometry:
authoritative confirmation of the final released coordinate frame plus
reviewed anatomy-based sensor QC could also suffice. Neither route is
available yet. MRI-only segmentation and surface preparation are conceptually
separate from leadfield use and may proceed when tools and disk space permit;
they do not clear electrode registration or authorize source fitting.

The exploratory computation API was also corrected after review. Its former
`unique_enough` result inferred spatial uniqueness from a count of family
labels after unrestricted least-squares fitting, without receiving spatial
supports or proving constrained feasibility. It is now explicitly a
`screen_family_spans` relaxation: a low computed float64 residual is compatible
with the family not being excluded by that span, while a high residual is only
an observed screen result, not a certified exclusion because no numerical
error bound is computed. It makes no spatial-uniqueness or
continuous-uncertainty claim. The full repository test suite passes (146 tests)
after this refinement. Unit tests do not validate the scientific method or
measured-data performance.

An additional focused rerun passed 23 existing algebraic/regression tests for
the two-sided capped-branch fit, robust attribution interval, forward-error
radius/envelope, stability helper and finite span screen. The exact command,
environment and SHA-256 input list are recorded in
`outputs/track_b/20261028_novelty_prototype_test_audit_v1/SESSION.md`. This
verifies those code paths on the declared fixtures only. The `screen_family_spans`
routine remains an uncertified relaxation; the triangle-inequality error
radius remains a standard bound that depends on externally justified column
radii. Neither supplies the missing continuous, physiology-grounded
family-wise identified-set guarantee or novelty evidence.

No WSGZP neural sample values were accessed. There are still no participant
surfaces, source spaces or forward solutions in the release. HDEEG remains
unavailable without access authorization. The current machine has about
5.2 GB free and no SimNIBS/Charm or FreeSurfer executable available. SimNIBS
officially supports Windows and its current installer takes about 3 GB, but
the remaining disk headroom is too small for a safe installation plus
participant mesh outputs. Official Charm supports T1-only head segmentation,
but warns that skull segmentation is less accurate without T2 and requires
visual inspection; it is a future engineering path, not a substitute for
coordinate provenance or reviewed registration.

## Current conclusion and next falsifiable experiment

The novelty status is **UNPROVEN**. Candidate 1 remains the leading empirical
question because a single best-fit map can hide spatially conflicting
alternatives. The next evaluable study, only after coordinate, forward-model
and protocol gates pass, is a frozen participant-held-out comparison of
source-family reports against an external sparse-positive outcome:

1. Freeze participant-grouped outer folds, keeping all runs/events from a
   participant together; tune global choices only on outer-training
   participants.
2. Apply the frozen procedure to each held-out participant's scalp response
   as the inference input, permitting only prespecified outcome-blind geometry
   and covariance inputs.
3. Compare source-family reports with direct constrained fits, GBF, matched
   patch methods and empirical spatial-fidelity/resolution baselines. Exact
   direct fitting is an equivalence oracle; a new algorithm must improve
   certified cost/tightness or guarantee while preserving its answer.
4. If a valid run-condition mapping and geometry are established, use SEEG
   only for sparse positive concordance at a fixed cortical-area budget, with
   sampling controls. It is not a whole-cortex negative map or complete truth
   for later distributed CCEP sources. Report inherited preprocessing and
   unresolved baseline/scale semantics.

If exact direct fitting gives the same report, that rules out a distinct
identified-set algorithm unless a certified computational or guarantee gain
is shown; it does not by itself rule out a new empirical finding. If standard
single-map or resolution baselines yield the same interpretation and no
previously unreported measured phenomenon remains, report validated software
or pivot. No simulation can replace the measured-data evidence.

## Primary sources checked for this update

* Jiao et al. (2024), XDL-ESI and same-cohort CCEP source-extent analysis,
  [DOI 10.1016/j.neuroimage.2024.120802](https://doi.org/10.1016/j.neuroimage.2024.120802),
  [full text in PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC11549933/).
* Yang et al. (2024), graph-Fourier source-extent estimation,
  [DOI 10.1186/s40708-024-00221-2](https://doi.org/10.1186/s40708-024-00221-2).
* Parmigiani et al. (2022), simultaneous scalp hd-EEG and SEEG CCEP dataset,
  [DOI 10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007).
* Official WSGZP curation code at pinned commit
  [`8721fc04328c00b131659915dfbfa569bd342b54`](https://github.com/iTCf/ccepcoreg/tree/8721fc04328c00b131659915dfbfa569bd342b54);
  inspected `export_bids.py` and `fx_bids.py`. This exporter consumes
  processed epoch objects; processing declarations in its metadata are not
  evidence that it applied those operations.
* Levinson et al. (2024), CCEP processing effects,
  [DOI 10.1016/j.jneumeth.2024.110130](https://doi.org/10.1016/j.jneumeth.2024.110130).
  It supports artifact/filter sensitivity as a requirement, not a claim about
  the unavailable WSGZP upstream processing run.
* Parmigiani et al., bioRxiv Supplementary Material 1, pp. 1–2,
  [preprocessing methods](https://www.biorxiv.org/content/10.1101/2021.11.15.468625v1.supplementary-material).
* Juditsky & Nemirovski (2019), *Near-Optimal Recovery of Linear and
  N-Convex Functions on Unions of Convex Sets*:
  <https://arxiv.org/abs/1804.00355>
* SimNIBS 4.6, *Creating Head Models*:
  <https://simnibs.github.io/simnibs/build/html/tutorial/head_meshing.html>
* SimNIBS 4.6, *Requirements*:
  <https://simnibs.github.io/simnibs/build/html/installation/requirements.html>
* SimNIBS 4.6, *Installation*:
  <https://simnibs.github.io/simnibs/build/html/installation/installation.html>

## Metadata-only repeated-run screen (28 October 2026)

A full scan of the extracted WSGZP epoch metadata (323 EEG/iEEG run tables)
found two within-participant pairs of run tables with identical
stimulation-condition strings: sub-14 runs 01/02 and sub-36 runs 06/07. EEG
and iEEG epoch counts differ within both pairs; the TSVs expose no shared event
identifiers or onsets. The pinned curation repository has two run-numbering
helpers, but the exporter consumes an external `runs_table.csv` and the
published materials do not establish which helper produced the released
mapping. The run IDs therefore do not establish chronology, session identity,
or independence. The metadata also cannot establish temporal spacing, epoch
overlap, or whether preprocessing was estimated jointly. The pairs are leads
for a custodian query, not independent replications. They do not justify
repeatability as a primary novelty endpoint. The publication's 25-retained-
trial rule makes sub-36/run-06 ineligible for a paper-matched repeat test
unless its count and session membership are reconciled. Sub-14 is one
row-count-eligible participant pair, but its acquisition and preprocessing
independence remain unverified; it could support only a descriptive
within-participant comparison if those facts are confirmed. See
`WSGZP_REPEAT_RUN_FEASIBILITY_20261028.md` and
`outputs/track_b/20261028_wsgzp_repeat_run_audit/repeat_run_inventory_v3.json`.

This finding changes the metadata inventory, not the novelty verdict.
Novelty remains **unproven**, and no WSGZP signal fitting or scoring is
authorized by this audit.

## Run-ID semantics cross-check (29 October 2026)

The exporter consumes `run_id` from an external `runs_table.csv`. The pinned
repository contains two helpers with different numbering behavior, but neither
the published notebook nor repository establishes which table-construction
helper produced the released mapping. The run labels identify distinct
exported derivative entries; they do not establish chronological order,
non-overlapping acquisition, session identity, or independent preprocessing.
Therefore the two exact condition matches are candidate same-condition
run-table repeats, not proven test-retest acquisitions. This reinforces the
custodian provenance gate and weakens repeatability as a novelty route unless
upstream records resolve it. See the [numbering helpers](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L876-L961),
[exporter table input](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/export_bids.py#L365-L450),
and [pinned usage notebook](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/_00_getting_started.ipynb).

The primary data paper adds an eligibility problem: it reports 30/40 trials
per stimulation session and says 323 of 379 sessions were retained after
excluding nine sessions with evoked epileptic spikes and 47 with fewer than
25 retained trials. Yet released sub-36/run-06 has 13 EEG and 15 iEEG epoch
rows. The available metadata do not explain whether these are the same
counting unit or whether this run belongs to the paper's retained set. Thus
sub-36 runs 06/07 cannot support a paper-matched repeatability test unless
the custodian reconciles the discrepancy. The sub-14 pair exceeds 25 rows in
both modalities but still lacks proof of independent acquisition and
preprocessing. The two-pair metadata screen therefore currently yields at
most one unresolved candidate, not a repeatability dataset. See
`WSGZP_REPEAT_RUN_FEASIBILITY_20261028.md` and
`WSGZP_CUSTODIAN_QUERY_DRAFT_20261028.md`.

The public OSF v2 file index was checked directly on 29 October. It lists the
six multipart archive files under `/data/` and `eeg_badtrials.json` under
`/additional_info/`, but no run map, event-index table, chronology crosswalk,
or 379-to-323 selection table. Thus the discrepancy is not resolvable from
the currently indexed public files; only the dataset custodian can confirm
the provenance if records exist upstream. This file-index check accessed
names and paths only. See `WSGZP_PUBLIC_FILE_INDEX_AUDIT_20261029.md` and
`outputs/track_b/20261029_wsgzp_osf_file_index.json`.

## Novelty-proof update (28 October 2026)

The exact overlap audit sharpened the main threat. The 2026 GBF study already
uses the same iES-CCEP resource for 318 stimulation sessions across 35
participants. Its quantitative stimulation-site endpoint selects the peak
source estimate within ±5 ms of stimulation; it separately reconstructs
later N1/N2 propagation. The WSGZP data paper itself points to source
localization comparisons as a use of the release. Therefore applying GBF,
comparing maps to stimulation sites, analyzing N1/N2, or reporting
EEG-to-SEEG contact concordance is not a distinct contribution by itself.

A further direct threat is XDL-ESI (Jiao et al., 2024): the full-text methods
describe the same 36-participant simultaneous hd-EEG/SEEG stimulation cohort,
FEM head model, and 2,213 volumetric source cubes. The real-data section
compares the estimated maps with the stimulated contact and displays the top
five dipoles for Subj. 29. This is direct overlap for source extent and
stimulation-site localization, but the displayed result is not a
participant-held-out family-ambiguity analysis. The possible empirical delta must therefore be
narrower than “source extent” or “CCEP source localization”: it would have to
show a reproducible, held-out source-family ambiguity result under declared
forward uncertainty that changes a predeclared interpretation beyond GBF,
XDL-ESI, direct constrained fitting, and resolution/patch baselines. This
result has not been demonstrated.

The only live empirical hypothesis is narrower: materially different,
physiologically defensible source families may remain compatible with the
same measured late-CCEP scalp fields, making a focal source report
unsupported for some held-out participants. Under the current release this is
an in-observation compatibility finding, not independent prediction. It would
be a conditional observability finding, not a new algorithm or true-source
recovery claim.
Positive SEEG-contact capture is the candidate primary external endpoint for
the bounded action of prioritizing a fixed cortical area for follow-up; it is
not validation of the ambiguity label or source truth. Generic family-set
feasibility, functional ranges, calibration, and forward-model uncertainty
each have close prior art. A formal candidate set has now been
written in `NOVELTY_PROOF_PLAN_20261028.md`, explicitly without claiming the
construction is novel.

The candidate priority output still has an identifiability gap: a feasible set
expresses possibility, not a location probability or ranking. Counting
solutions or optimizer hits would make the map depend on sampling choices. A
conservative lower-envelope map is recorded as a candidate, but its common
amplitude scale, floor, numerical/continuous error control and abstention rule
are not settled. Until that map is defined, SEEG contact capture cannot be
used as a preregistered decision endpoint. For fixed convex branches the
lower-envelope score reduces to standard constrained convex optimization and
finite-union aggregation, so it is not an algorithmic novelty candidate
without a new certified gain or demonstrated decision value.

Novelty remains **unproven**. The next research step is an exact equation and
endpoint delta against GBF, WSGZP, SESAMEEG, spatial-fidelity, patch,
robust-forward, and set-valued/conformal methods, followed by an adversarial
check that a mathematically defined report could change a predeclared
researcher decision beyond direct fitting and existing resolution methods. No
signal fitting is authorized until that survives and the existing protocol,
geometry and preprocessing gates close.

The reproducible source hashes and detailed preprocessing consequences are in
`WSGZP_PREPROCESSING_PROVENANCE_20261028.md`.

## Calibration identifiability audit (29 October 2026)

The audit in `CALIBRATION_IDENTIFIABILITY_AUDIT_20261029.md` separates three
targets that were previously easy to conflate: a residual/noise compatibility
threshold, whole-cortex source-set coverage, and fixed-area capture of
sampled responsive SEEG contacts. WSGZP's intervention contacts and sparse
positive SEEG contacts do not label the complete generator of a later CCEP;
therefore they cannot calibrate true-source coverage or ambiguity-label
correctness. Until an appropriate residual null is derived and validated,
report a prespecified fit tolerance rather than calibrated probability. The
only plausible measured-data performance endpoint in the present route is
sampled-positive-contact capture, with participant-grouped uncertainty and
the explicit restriction that it is not calibration of the source set or
source truth.

This is a statistical identifiability result from the measurement/label
structure, not a WSGZP signal result. Signal access remains closed. Novelty
remains unproven; the next valid path still requires clearing geometry,
preprocessing and protocol gates, then testing whether the bounded
research-prioritization decision adds value beyond matched baselines.

## Measured source-reference dataset screen (29 October 2026)

`MEASURED_SOURCE_REFERENCE_DATASET_REVIEW_20261029.md` records a primary-
source check for alternatives that might calibrate the source-space claim.
The open NEMAR `nm000513` release has endogenous simultaneous EEG/SEEG spikes
but no released SEEG contact coordinates, and its underlying seven-patient
cohort was already analyzed in 2015 and 2023. HDEEG-IED-SurgOutcome has
participant MRI, dense scalp geometry and postsurgical outcome but only an
indirect source reference; project access is still unresolved and the 2026
GBF paper also lists it. Neither route currently closes the whole-cortex
source-truth gap. This is a feasibility/prior-art result, not a neural-data
result, and does not open WSGZP signal access.

## Pinned WSGZP curation-source recheck (29 October 2026)

The upstream `iTCf/ccepcoreg` repository was checked at commit
`8721fc04328c00b131659915dfbfa569bd342b54`. Its exporter reads the same
`{subj_name}_egi_dig.hpts` file for the scalp-electrode table and coordinate
sidecar; the helper writes the parsed coordinates directly while declaring
`T1w`/mm. A separate `load_trans` helper exists, but the checked exporter does
not call it or apply a transform. The repository and exact source hashes,
line-level links, and interpretation are recorded in
`WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md`.

This makes the missing provenance more specific, but does not prove the
coordinates are incorrect: the source `.hpts` may already contain MRI-frame
coordinates, consistent with the paper's description of coregistration. Until
the curators confirm that contract or provide the source points/transform and
reviewed overlays, the participant-specific forward-model gate remains open.
Therefore the novelty experiment is still not ready for signal fitting; this
audit is a provenance finding, not evidence for a novel method.
