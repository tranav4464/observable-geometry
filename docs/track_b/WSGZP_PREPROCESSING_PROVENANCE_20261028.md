# WSGZP preprocessing provenance audit

**Audit date:** 28 October 2026\
**Status:** publication-level method details recovered; derivative-level execution and fold-wise fitting not independently reproduced\
**EEG/SEEG sample values accessed for this audit:** no

## Question

Can the released derivative and official public curation code establish how
the simultaneous scalp EEG and SEEG were filtered, referenced, baseline
corrected, and cleared of stimulation artifact?

## Evidence inspected

The official [`iTCf/ccepcoreg` repository](https://github.com/iTCf/ccepcoreg)
was pinned to commit
`8721fc04328c00b131659915dfbfa569bd342b54` (resolved from its HEAD on 28
October 2026). Source hashes at that revision:

| File | SHA-256 |
|---|---|
| `export_bids.py` | `d8807afb62944102ec461e93f2004ac3fcb5be3b5378bad10bbd335248f6b2ae` |
| `fx_bids.py` | `0b5d3c817e939f3bc20c1e0c2c2c6e86ec42c317e3bc3a260388dc5823bf6eef` |

In `fx_bids.py`, the exporter calls the external `itcfpy.read_write.load_scoreg`,
then crops the returned epoch object to −0.3 through 0.7 s, writes channel
metadata, and serializes `epo.get_data()` to `.npy`. The inspected curation
function does not show filtering, average re-referencing, ICA, baseline
subtraction, or stimulation-artifact suppression. However, `load_scoreg` may
apply some of these operations internally, or the data passed to it may
already have undergone them. Its implementation and upstream input are not
included in the pinned curation repository. The evidence therefore does **not**
prove that the operations were absent; it proves that their exact execution
and order cannot be reconstructed from this exporter alone.

The exporter writes `low_cutoff=0.5`, `high_cutoff=45`, and
`reference=average` for EEG channels, and `0.5`, `300`, and `bipolar` for SEEG
channels. It also writes baseline-correction metadata (`mean subtraction`,
−0.3 to 0 s). These are dataset declarations written by the exporter; by
themselves they do not prove which processing operation ran, or when. The local
derivative description additionally reports manual channel/epoch rejection,
third-order Butterworth filtering and EEG ICA for blink removal. These are
inherited processing claims; the public curation script does not provide a
replayable trace tying them to the saved arrays. The original 2024 CCEP
processing study reports that filtering and rereferencing can change CCEP
morphology. This supports sensitivity analysis but does not reproduce the
pipeline applied to the released epochs.

The 2022 data paper says retained SEEG and hd-EEG sessions were processed by
prior pipelines and directs readers to its supplementary material. The public
exporter does not recover the missing continuous recordings, trigger stream,
rejected-trial log, or exact artifact-removal steps. The 2024 CCEP-processing
study reports that filtering and rereferencing can change CCEP morphology and
that filtering may spread stimulation artifact in time. This supports keeping
the post-artifact endpoint provisional; it does not identify what was done to
these specific released epochs.

### Supplementary method recovered

The paper's bioRxiv v1 supplementary material (Supplementary Material 1,
pp. 1-2) was retrieved and inspected. Its equivalence to the final journal
supplement has not been independently established. SHA-256 of the downloaded PDF:
`241c3a155d61b8b786cb7cd278c8b5fb907e0ee46ae52a4f99c9f3352313456a`.
It describes the study-level pipelines as follows:

* **Scalp hd-EEG:** visual rejection of noisy, muscle-contaminated or
  interictal trials and bad contacts; removal of neck/cheek contacts; stimulation
  artifact removal (citing prior methods, without a full parameterization in
  this supplement); third-order Butterworth 0.5-45 Hz filtering; segmentation
  from -300 to +700 ms; session exclusion for more than 20 bad contacts or
  fewer than 25 artifact-free trials; spherical interpolation of rejected
  contacts; average rereferencing; baseline correction from -300 to -50 ms;
  and ICA to remove eye, heartbeat and remaining muscle components.
* **SEEG:** linear detrending; third-order Butterworth 0.5-300 Hz filtering and
  optional notch filtering; adjacent-contact bipolar montages; Tukey-windowed
  median artifact reduction from -5 to +5 ms around stimulation; clinical and
  visual exclusions; trial/contact rejection; segmentation from -300 to +700
  ms; and baseline z-scoring from -300 to -50 ms.
* MRI/CT electrode localization is also described: post-implantation cone-beam
  CT coregistered to T1 MRI with FLIRT, electrode positions labeled with
  FreeSurfer/SEEG-Assistant, then nonlinear normalization to MNI152 with ANTs
  SyN. This describes the paper's localization workflow, not proof that every
  transform needed for our participant-specific scalp forward model is
  available in the released BIDS derivative.

This materially improves the publication-method record: preprocessing is no
longer unknown at the study-description level. It remains **inherited, not
independently reproduced**, at the specific exported-array level because the
public exporter delegates to external `load_scoreg`, and its exact inputs,
version, implementation, and relationship to the published processing run are
not documented in the inspected source. The supplement does not state the trial
pool used to fit ICA; it may include all retained repetitions, a longer
continuous recording, or another pool. It also reports visual rejection before
the proposed split. Therefore the prior A/B/C event-row split is not an
end-to-end untouched preprocessing holdout. This is not proof of supervised
outcome leakage, but the held-out rows are conditional on the released
processed derivative.

There is also a baseline/representation discrepancy requiring resolution. The
preprint supplement reports scalp baseline correction from −300 to −50 ms and
contact-level SEEG CCEP z-scoring against that baseline. The exporter instead
declares mean subtraction from −300 to 0 ms and voltage units for both
modalities. These may describe different stages or representations. This does
not prove that exported arrays are incorrectly labelled or already z-scored:
the available source does not establish which stage supplied those arrays.
The released arrays' baseline and SEEG standardization state therefore remain
unresolved at the execution-provenance level. Do not silently treat the
operations as equivalent, especially if contact response thresholds or
cross-modal amplitudes are used.

## Consequence for the proposed analysis

1. Treat the release as **processed with publication-level methods described,
   but incompletely traceable array-level execution**. Do not claim that this
   project independently reproduced its filtering, rereferencing, ICA,
   baseline correction or artifact removal from raw recordings.
2. The main paper's N2 definition motivates the prespecified 50–300 ms window.
   It is not evidence that every sample in the interval is free of artifact or
   filter recovery.
3. A released-derivative repeatability analysis is **not currently cleared**.
   It would require a verified independent repeated acquisition and explicit
   acceptance of inherited preprocessing/baseline limitations in the freeze.
   The only same-condition pair whose modality-specific metadata counts meet
   the paper's stated minimum of 25 is sub-14 runs 01/02, but acquisition and
   preprocessing independence are unverified. Sub-36 runs 06/07 include a run
   below that count and require an authoritative selection/count reconciliation.
   Even if cleared, repeatability would be conditional on released preprocessing,
   not independent reproduction or verified post-artifact physiology. Keep
   artifact-sensitivity controls and bound claims.
4. The old A/B/C manifest verifies metadata row assignments only and is not
   the confirmatory split. Keep participants, sessions and all their events
   grouped as specified in amendment v4. Because the ICA fitting pool is
   unrecorded, the held-out analysis remains conditional on the released
   derivative. This is not proof of supervised outcome leakage, but it
   precludes an end-to-end raw-data holdout claim.
5. Before signal access, the analysis lock must explicitly record these
   preprocessing limits and resolve or bound the baseline/scale contract for
   every outcome used.

This is a data-provenance finding, not evidence for or against a new source
method. It may force the primary endpoint to be narrowed or the dataset route
to be reconsidered if the scientific question requires independently
verifiable artifact correction.

### Additional provenance required for an epoch-split test

The separate `additional_info/eeg_badtrials.json` contains one binary mask
per paired run. A header-only comparison found that its zero count matches the
exported EEG epoch row count and NPY first-axis length in 317 of 323 runs;
six runs disagree. The count match is only a candidate index mapping. The
mask's zero/one meaning, source epoch sequence, order preservation, additional
post-mask rejection, and relation to the EEG array rows are not defined in the
public exporter. The upstream `itcfpy.read_write.load_scoreg` implementation
and its inputs are not included in the pinned repository or the extracted
dataset; `itcfpy` is not installed in the project environment and no public
PyPI project metadata was found. Do not infer the mask convention from the
filename or counts alone.

Before using these masks to form any train/repeat split, obtain an authoritative
description or mapping from the dataset authors covering:

* Whether `0` or `1` denotes a retained trial and the exact indexing origin.
* How each original EEG event index maps to each exported NPY row, including
  the six count-mismatch runs and any additional manual exclusions.
* Retained event sample indices/timestamps for EEG and SEEG, plus any mapping
  between modalities. Do not assume simultaneous trial identity from matching
  run labels.
* Whether windows overlap and what filtering, artifact removal, baseline
  correction, channel rejection and ICA fitting were performed before export;
  identify the data pool used to fit any across-trial transform.

If authors cannot provide this information, an analysis of split NPY rows can
only be labeled **repeatability conditional on the released derivative**,
with no claim of event-level independence or EEG–SEEG trial correspondence.
The machine-readable count audit is
`outputs/track_b/20261028_wsgzp_trial_index_feasibility/trial_index_audit.json`;
its script reads TSVs, the JSON mask and NPY headers only, never sample values.

## Sources

* Parmigiani et al. (2022), *Simultaneous stereo-EEG and high-density scalp
  EEG recordings to study the effects of intracerebral stimulation
  parameters*, [DOI 10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007).
* Parmigiani et al., bioRxiv v1 supplementary material, [Supplementary Material 1](https://www.biorxiv.org/content/10.1101/2021.11.15.468625v1.supplementary-material), pp. 1-2 (preprint processing and electrode-localization methods; equivalence to the final journal supplement not verified).
* Official data-curation code, pinned [`export_bids.py`](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/export_bids.py)
  and [`fx_bids.py`](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py).
* Levinson et al. (2024), *Data processing techniques impact quantification
  of cortico-cortical evoked potentials*, [DOI
  10.1016/j.jneumeth.2024.110130](https://doi.org/10.1016/j.jneumeth.2024.110130).
  This is an original processing study, not a review.
