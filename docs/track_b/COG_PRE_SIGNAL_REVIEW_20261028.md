# COG pre-signal review and required protocol amendment

**Date:** 28 October 2026
**Decision:** **HOLD before signal analysis**
**Evidence inspected:** source code, papers, BIDS metadata, NumPy headers and MRI/geometry file presence; no EEG/iEEG sample values inspected.

**Protocol update:** Section 4's earlier interleaved A/B/C event-row proposal is
superseded for confirmatory evaluation by
`COG_PROTOCOL_AMENDMENT_20261028_v4.md`. The participant-grouped metadata
manifest is verified, but the full scientific lock remains open.

## Why the current COG v1 cannot proceed unchanged

### 1. The released modality rows are not paired trials

There are 323 same-condition run pairs across 36 participants, but retained EEG
and SEEG epoch counts differ in 319/323 runs. The epoch tables contain only
`duration`, `zero_time`, and `trial_type`; none contains event identity or an
onset/sample index. Array row `j` therefore cannot be treated as the same
observation across modalities. Use separately calculated run-level condition
averages, or obtain original trigger and rejection logs before any trial-level
cross-modal claim.

### 2. The source-family label is not identifiable

Point, patch, multi-patch, signed and flexible families overlap or nest. If a
point solution is admitted by a flexible family, its residual cannot be lower
than the flexible family's residual. Residual ranking cannot identify the
true family, and WSGZP does not label a complete whole-cortex source family.
Sparse SEEG contacts also cannot provide whole-cortex negative labels.

Replace “one source family wins” with a claim about **spatial agreement across
all fit-qualified explanations**. Define a spatial functional before analysis,
such as support diameter or whether every admissible support lies in the same
predeclared anatomical parcel. `UNIQUE_ENOUGH` is allowed only if every
admissible explanation meets that spatial rule; `AMBIGUOUS` means they
materially disagree; `UNSUPPORTED` means none of the declared families fits the same measured
scalp field within the locked residual tolerance. This tests conditional observability, not the true
neural generator.

### 3. A minimum over model perturbations is not robust certification

`min_{theta in U}` shows that at least one tested model in `U` can fit the
field. It does not show that the fit holds across every allowed model. A finite
parameter grid is a stress ensemble, not a continuous uncertainty bound.
Report existential plausibility separately from worst-case stability. Do not
claim a continuous certificate until between-grid errors have a valid bound.

### 4. The measured endpoint and split must match the claim

Before opening signal arrays, specify the response as a channel-by-time matrix
on a fixed interval, not an unspecified peak across a broad window. The
current candidate is participant-held-out source-family evaluation on the
released processed derivative, with sparse measured SEEG-response contacts
used only for positive corroboration:

1. Keep each participant, all their sessions (if present), run tables and
   events in one outer fold. The metadata audit found no BIDS `ses-` entity in
   the EEG epoch paths; run labels encode stimulation conditions and are not
   presumed to be independent sessions.
2. Tune global thresholds, family budgets and calibration only on outer
   training participants. Apply frozen choices to each held-out participant's
   released scalp response using only outcome-blind, prespecified participant
   geometry and covariance inputs.
3. Do not split epoch rows across train/test or zip EEG and SEEG rows. Counts
   differ and shared trial identifiers are absent. Use condition-level
   averages separately, and compare the reported spatial support with sampled
   SEEG-responsive contact locations under a predeclared metric.
4. Compare against direct constrained fitting, GBF, matched patch methods
   and empirical resolution/spatial-fidelity baselines. Report
   participant-macro summaries and participant-bootstrap intervals.

This can validate a held-participant decision and sampled positive-contact
capture, not true whole-cortex source recovery. The stimulated contact is an
intervention, not the unique source of a later distributed CCEP. A
nonresponsive sampled contact means “no detected response there under this
condition,” not inactive cortex. Do not infer specificity from unsampled or
nonresponsive cortex.

The main 2022 data paper defines scalp N1/N2 windows; 50–300 ms is the
candidate late-response interval. Supplementary Material 1 describes intended
preprocessing, but its baseline/scale statements differ from exporter metadata,
and the ICA fitting pool is unrecorded. Treat analyses as conditional on the
released processed derivative unless those execution details are resolved.
Do not tune the window from response values.

### 5. The participant forward model is not yet available

All 36 individual MRIs and scalp/SEEG coordinate tables are present, but the
release has no source surfaces, BEM surfaces, source spaces or leadfields. The
project environment has MNE and nibabel, but no FreeSurfer surface-generation
executables were found on `PATH`. A participant-specific forward-model build,
coordinate transform and sensor overlay check must pass before inverse fitting.
Do not substitute an fsaverage or spherical model and call it participant
specific.

Resolve the metadata issues without changing the source release:

* All 36 scalp coordinate sidecars point to missing `*_T1.nii`; the actual
  images are `*_T1w.nii`. Record the local path resolution and preserve source
  hashes.
* A coordinate-only follow-up varied the coarse MRI intensity threshold for
  `sub-01` and `sub-32`. The `sub-32` scalp-distance outlier persisted from
  thresholds 10–50 while its native-MRI SEEG positive control stayed near
  1 mm. This makes a simple threshold-cutoff artifact less likely, but the
  screen is not scalp segmentation or registration proof. Its MRI/electrode
  overlay and original digitizer transform still need review; no source fitting
  is cleared. Reproducible output:
  `outputs/track_b/20261028_wsgzp_coreg_audit/threshold_sensitivity_v1.json`.
  A full-voxel follow-up at thresholds 0.1–10 left the sub-32 median at
  43.02 mm (`threshold_sensitivity_low_v1.json`), ruling out the tested
  threshold and sampling choices but still not distinguishing coordinate
  registration from missing/masked scalp voxels.
* An exact NIfTI affine/FOV check found listed scalp sensors outside the MRI
  volume for 8/36 participants. Counts were largest for `sub-32` (29/185),
  `sub-29` (11/185), `sub-33` (8/185) and `sub-21` (4/185). This can reflect
  MRI cropping of external scalp and is not, by itself, evidence of a bad
  transform. These points cannot be overlaid on MRI tissue and must be included
  in coordinate/QC review, not silently clipped. Machine-readable output:
  `outputs/track_b/20261028_wsgzp_coreg_audit/electrode_fov_v1.json`.
* Exclude the 10 good sub-33 SEEG channels without exact native coordinates
  (`V1-2`, `V2-3`, `V3-4`, `V6-7`–`V12-13`) from spatial comparisons unless an
  authoritative mapping is obtained.
* The derivative dataset description has trailing-comma JSON. The audit's
  narrow parser repair is in-memory only; preserve the original file/hash.
* Original continuous sources and trigger/rejection logs named in epoch JSON
  files are absent. Treat filtering, ICA and artifact rejection as inherited;
  do not claim raw preprocessing was reproduced.

## Data boundary and primary split

Subject is the outer split unit. Use deterministic leave-one-participant-out
evaluation; all runs from the held-out participant stay held out. Thresholds,
family budgets, support rules and model selection are determined only inside
the remaining participants. Weight participants equally and bootstrap whole
participants. This is not a clinical- or population-generalization claim:
WSGZP is one clinical stimulation cohort and has already appeared in published
GBF/CCEP work.

The metadata-only grouped manifest and independent replay are in
`outputs/track_b/20261028_wsgzp_participant_split/`. The verifier confirms the
36-participant, 323-run, 10,088-row inventory and that every run stays with its
participant. This is not a signal-level split or a protocol lock.

## Prior-art falsification updates

* **Wang et al., 2026, Nature Biomedical Engineering** already presents
  participant-specific GBFs and evaluates intracranial stimulation/epilepsy,
  including WSGZP-related data. The released demo averages epochs, uses a
  short stimulation-centred window for peak localization, and compares the
  peak to the stimulated contact. A post-artifact response analysis would be a
  different estimand, but a larger analysis of the same cohort is not an
  independent replication.
* **Jiao et al., 2024, XDL-ESI** is another direct collision. It uses the same
  36-participant hd-EEG/SEEG stimulation cohort, estimates spatial extents
  from averaged CCEPs, and compares maps to the stimulated contact. The paper
  describes test-time hyperparameter variation but the detailed displayed
  WSGZP comparison is for Subj. 29. Its stated data availability is “on
  request”; no code-availability statement was found in the article.
  Therefore the novelty claim cannot be “source extent on WSGZP.” The
  remaining candidate must specifically test family-wise compatibility under
  declared uncertainty against SEEG responses to later distributed CCEPs,
  while treating SEEG as sparse positives rather than whole-cortex truth.
  See `NOVELTY_PROOF_PLAN_20261028.md`.
* **Yang et al., 2024, graph-Fourier source-extent filters** already use
  low-spatial-frequency graph subspaces to recover extended source regions;
  their real-data example is MEG, not WSGZP. Include this family of methods in
  extent baselines where applicable. A broader map alone is not novel.
* **Phee et al., 2026** reports an MRI-informed EEG source-localization model
  with conformal uncertainty and evaluation on recorded intracranial-
  stimulation data. The Crossref record is dated 8 September 2026; its issue
  is December. I inspected the public code at commit
  `ded88a361ad349cb5e93a07171a11772f791a0e5`: its conformal block computes
  pooled scalar localization-loss quantiles from extra synthetic examples,
  including examples generated for the same held-out MRI identities used by
  its unseen test loader. The sample indices differ, so this is not evidence
  of EEG-sample reuse; it is identity-aware calibration and does not by itself
  establish cold-start coverage for a new participant absent from calibration.
  The visible block does not construct a per-test spatial set. This bounded
  code observation does not replace full-manuscript review. Generic
  “calibrated source-localization confidence” is therefore not a defensible
  novelty claim. See the [code-level prior-art audit](PRIOR_ART_PHEE_CODE_AUDIT_20261028.md).
* **Samuelsson et al. spatial fidelity** was miscited in the existing route
  plan. The correct reference is *NeuroImage* 224 (2021), 117430,
  DOI `10.1016/j.neuroimage.2020.117430`; its empirical framework covers
  nonlinear estimates, patches and noise. Compare it, not only point-source
  resolution matrices.
* Existing source-model averaging, structured/patch sparsity, Gaussian
  composite-hypothesis testing and conformal uncertainty are close prior art.
  A source-family union, set-membership fit or calibration wrapper alone is
  not new.

The official GBF loader expects a FreeSurfer subjects directory, builds a
three-layer BEM/source space, and caches subject-specific forward files. Its
loader converts the scalp coordinate values from millimetres to metres but
labels them as head-frame positions; the source dataset labels them T1w. That
coordinate path must be reconciled and independently checked before using the
GBF implementation as a baseline. Do not inherit its transform assumption
without an electrode-to-MRI overlay and transform audit.

### Independent-review correction: visual coregistration still required

The official WSGZP `export_bids.py` reads `{participant}_egi_dig.hpts` and
passes its values directly to the scalp-sidecar and electrode-table writers.
Those functions label the copied coordinates `T1w` millimetres without showing
an export transform. The original Parmigiani et al. data paper says scalp
electrodes and fiducials were digitized with SofTaxicOptic and coregistered
with the pre-implant MRI, supporting the declared MRI frame. MNE documents
`.hpts` points as usually being in head coordinates, but that generic
convention does not disprove the paper's specific coregistration. The source
`.hpts` files and exact transform remain absent, so independent overlay review
is still needed.

The earlier audit's transform placed fiducials on expected head axes because
it constructed the transform from those same fiducials. That was a
construction check, not independent evidence of coregistration. The
`PASS_INTERNAL_GEOMETRY_ONLY` label is withdrawn. The replacement status is
`REVIEW_REQUIRED_VISUAL_COREGISTRATION`; WSGZP forward modeling and signal
fitting remain blocked until a reviewed MRI/electrode overlay is available.

## Current verdict and next gate

**Verdict:** WSGZP may support participant-held-out run-condition analysis with
sparse SEEG-positive concordance, but it does not currently support a verified
repeatability endpoint. The public derivative has one row-count-eligible
same-condition candidate pair (sub-14), whose acquisition and preprocessing
independence are unknown; sub-36 fails the paper-matched 25-row screen unless
its counts and selection membership are reconciled. No calibrated true-source
or novel-method claim is justified. Keep the protocol unlocked and do not open
EEG/iEEG samples until the forward model, response matrix/window, spatial
functional, baseline/scale contract, comparator implementations and held-out
decision are frozen. If direct fitting, GBF and established resolution methods
make equivalent decisions, report a validated software contribution or pivot.

## Primary references

* Wang et al. (2026), GBF: <https://doi.org/10.1038/s41551-026-01664-0>
* Parmigiani et al. (2022), simultaneous scalp EEG/SEEG CCEP: <https://doi.org/10.1016/j.brs.2022.04.007>
* Phee et al. (2026), MRI-informed EEG localization: <https://doi.org/10.1016/j.cmpb.2026.109637>
* Samuelsson et al. (2021), spatial fidelity: <https://doi.org/10.1016/j.neuroimage.2020.117430>
* WSGZP data-curation repository: <https://github.com/iTCf/ccepcoreg>
* WSGZP BIDS exporter and loader: <https://github.com/iTCf/ccepcoreg/blob/main/fx_bids.py>
* GBF implementation: <https://github.com/ncclab-sustech/GBFs>
* GBF WSGZP loader: <https://github.com/ncclab-sustech/GBFs/blob/master/utils/ccep_loader.py>
* Phee et al. implementation: <https://github.com/pheeeeee/eeg_source_localization>
