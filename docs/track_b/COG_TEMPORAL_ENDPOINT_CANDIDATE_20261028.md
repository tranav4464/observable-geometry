# COG temporal endpoint candidate (metadata and literature only)

**Status:** proposed temporal component of a future signal-analysis lock; not
authorization to open EEG/SEEG sample values

## Candidate primary response window

Use the fixed post-stimulation interval **50–300 ms** as the primary scalp
response window, corresponding to the published N2 interval in the WSGZP
dataset paper. The analysis must use the complete channel-by-time response in
that interval, not search for and select each run's largest peak. Keeping the
window fixed avoids choosing a favorable peak after seeing the response and
preserves the waveform information needed for held-out prediction.

For each held-out participant, apply the frozen procedure to each condition's
released run-averaged scalp response. Keep all runs and event rows from that
participant in the same outer fold; tune global choices only on other
participants. Do not use an interleaved event-row split as confirmatory
evidence. The available epoch tables do not identify matching EEG and SEEG
trials, so this does not permit trial-paired source truth. SEEG remains a
separate, sparse positive-corroboration endpoint.

## Metadata basis

The extracted EEG epoch sidecar reports a 1-second epoch, event time at 300 ms,
mean baseline correction over −300 to 0 ms, and filtering inherited from the
released derivative. Channel metadata report 1 kHz sampling, average reference,
0.5–45 Hz filtering and voltage units. The derivative description reports
third-order Butterworth filtering, EEG ICA for eye blinks, and manual channel
and epoch rejection. These preprocessing steps are inherited, not reproduced
from the unavailable continuous recordings.

Parmigiani et al. (2022), the WSGZP data paper, quantify scalp N1 and N2
components using maxima in 0–50 ms and 50–300 ms respectively. The proposed
endpoint adopts the published N2 interval but deliberately uses the entire
fixed interval rather than its per-run maximum, because a maximum is a
nonlinear summary that can hide waveform and topographic changes.

## Artifact and interpretation limits

The 50–300 ms choice is intended to focus on the later physiological CCEP and
avoid the immediate stimulation transient. It does **not** prove that the
released preprocessing fully removed stimulation artifact or filter recovery
effects. Supplementary Material 1 supplies the study-level hd-EEG sequence:
visual trial/contact rejection, neck/cheek removal, stimulation-artifact
removal, third-order Butterworth 0.5–45 Hz filtering, epoching, session
exclusions, spherical interpolation, average rereference, baseline correction
from −300 to −50 ms, then ICA for ocular, cardiac and remaining muscle
components. The supplement does not fully parameterize artifact removal or
identify the trial pool used to fit ICA. A 2024 methods study shows that
filtering can alter CCEP morphology and spread artifact in time. Thus 50–300 ms
is a fixed response window, not evidence by itself that every retained sample
is artifact-free.
The official curation exporter was inspected at pinned commit
`8721fc04328c00b131659915dfbfa569bd342b54`. It calls an external
`itcfpy.load_scoreg`, crops the returned epoch object and writes the arrays;
its filter, reference and baseline fields are metadata declarations. The
exporter alone cannot determine whether preprocessing happened inside the
loader or earlier. The upstream loader and continuous recordings/trigger/
rejection logs remain unavailable, so the exact processing order and artifact
handling are not independently replayable. Supplementary Material 1 reports
scalp baseline correction from −300 to −50 ms and SEEG CCEP z-scoring against
that baseline; the exporter declares mean subtraction from −300 to 0 ms and
voltage units for both modalities. This may reflect different processing
stages, but the released arrays' baseline and SEEG standardization state remain
unresolved. The supplement is bioRxiv v1; equivalence to the final journal
supplement was not checked. The endpoint can be locked only as an analysis of
the released processed derivative, with inherited-preprocessing and fold-scope
limitations declared; it cannot be called an end-to-end raw-data holdout or
independently verified artifact-free physiology. Do not inspect the target EEG
response to tune the window. Details and source hashes are in
`WSGZP_PREPROCESSING_PROVENANCE_20261028.md`.

The data paper also averages the scalp N2 component and compares it with SEEG
measures, but SEEG contacts are sparse. A later CCEP can recruit distributed
networks; the stimulated bipolar pair is the intervention site, not complete
ground truth for every response generator. Consequently, good held-out scalp
prediction establishes repeatability of the measured field, not correct source
recovery.

## Still required before the full lock

This temporal proposal does not resolve the other pre-signal gates. The full
protocol must still freeze: participant coordinate provenance and reviewed
forward models; channel exclusions and reference projection; the source-family
coefficient/support constraints; forward-uncertainty bounds; covariance
estimator and average scaling; an exhaustive or explicitly bounded search;
the spatial agreement rule and its decision threshold; calibration; comparator
implementations; negative controls; stopping rules; and code/configuration
hashes. No source family may be called physiologically validated from the
constructed-field audits.

## Evidence checked

* Local WSGZP derivative sidecars and channel/epoch TSV metadata; metadata only,
  no EEG or SEEG sample values read.
* Parmigiani et al. (2022), *Simultaneous stereo-EEG and high-density scalp
  EEG recordings to study the effects of intracerebral stimulation
  parameters*, *Brain Stimulation* 15:664–675,
  [DOI 10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007).
  The paper reports N1 maxima in 0–50 ms and N2 maxima in 50–300 ms for scalp
  hd-EEG.
* Parmigiani et al., bioRxiv Supplementary Material 1, pp. 1–2,
  [preprocessing and electrode-localization methods](https://www.biorxiv.org/content/10.1101/2021.11.15.468625v1.supplementary-material).
* Levinson et al. (2024), *Data processing techniques impact quantification
  of cortico-cortical evoked potentials*, *Journal of Neuroscience Methods*
  408:110130, [DOI 10.1016/j.jneumeth.2024.110130](https://doi.org/10.1016/j.jneumeth.2024.110130).
  The study reports that filtering and rereferencing can change CCEP magnitude
  and morphology, and discusses temporal spreading of stimulation artifact.
