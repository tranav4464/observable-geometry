# Measured source-reference dataset review

**Date:** 29 October 2026\
**Purpose:** Identify whether an accessible measured dataset can close the source-reference gap needed to prove novelty.\
**Scope:** Public records, release metadata and prior papers only; no new EEG/SEEG samples accessed.

## Finding

No reviewed route currently supplies all three at once: endogenous neural events, participant-specific scalp forward geometry, and an independently defensible spatial reference for the same event. The sources support different, bounded validation tasks. They must not be combined rhetorically into a claim of complete neural source truth.

| Route | Useful reference | Critical limitation for this project | Valid role |
|---|---|---|---|
| **WSGZP / iES-CCEP** | Simultaneous hd-EEG/SEEG, stimulation contacts, participant MRI and scalp/electrode metadata; open dataset package. | The intervention site is not the full generator of later CCEPs; responsive SEEG contacts are sparse positives. Scalp electrode source `.hpts` and exact transform provenance remain unresolved for the current release audit. The 2026 GBF paper already analyzes this route. | Primary measured CCEP route, if protocol, geometry, preprocessing and endpoint gates close. Can test model-conditional compatibility and sampled-positive-contact utility, not source-set coverage. |
| **HDEEG-IED-SurgOutcome** | 44 analyzed patients in the 2025 data descriptor (45 in the dataset record), individual presurgical MRI, 257-channel EEG averages, T1-space scalp electrode coordinates, postsurgical MRI and 12-month surgical outcome. | Outcome/resection is an indirect clinical reference, not direct event-level measurement of the generator. Raw EEG is unavailable and preprocessing varied across clinical years. Dataset-specific EBRAINS access remains unresolved in the project. The 2026 GBF study also lists this dataset, so it is not automatically independent of that prior art. | Potential external clinical-concordance evaluation if legitimate access is granted; no claim of neural-source ground truth. |
| **NEMAR `nm000513` deep mesial temporal EEG–SEEG** | Open CC-BY-4.0 release; 7 patients, 9 networks, 1,945 simultaneous 1-s spike epochs, 128-channel scalp EEG and bipolar SEEG. This is directly measured endogenous interictal activity. | The release README says SEEG contact coordinates are absent (`n/a`); hence no verified participant-specific spatial map or source-family contact-capture test can be built from the package as released. It is the same cohort analyzed by Koessler et al. (2015) and Ternisien et al. (2023), which already tested scalp visibility/extraction using averaged spike events and BSS. | Possible replication/control for deep-spike scalp detectability if the narrow endpoint is justified; not an independent or spatially registered novelty validation. |
| **Localize-MI** | Measured scalp responses to electrical current delivered between known intracranial contacts, with participant-specific MRI and geometry. | The evaluated early response is stimulation artifact, not endogenous neural activity. | Controlled pulse-artifact / forward-model control only, as already specified. |
| **ds004752 / on004752** | Fifteen participants with simultaneous standard 10–20 scalp EEG and depth iEEG during verbal working memory; the release provides MNI intracranial contact coordinates, trial information, and LCMV virtual sensors. | No participant-specific MRI or individualized scalp-electrode geometry is present in the local v1.0.0 snapshot. Intracranial coordinates are normalized to MNI, not participant-native anatomy. The task and released virtual sensors support prediction/connectivity questions, not a participant-specific forward-model source-family test. | Preserve as the completed scalp-to-iEEG transport benchmark, not proof of this source-family claim. |

## Prior-art consequence for `nm000513`

The NEMAR record states that the release contains simultaneous spike-centred scalp EEG and SEEG epochs from seven patients, but the package README specifies no released contact coordinates. It points to the Mendeley dataset and the prior studies. Ternisien et al. (2023) analyzed the same seven-patient, nine-network cohort, reporting 1,949 spikes and evaluating extraction of deep mesial temporal sources that were difficult to see in individual scalp epochs. The NEMAR release lists 1,945 epochs; the small discrepancy must be resolved before exact replication. This is useful measured-data material, but it cannot be presented as a new validation cohort or as an unexplored discovery setting.

Primary records: [NEMAR dataset record](https://www.nemar.org/dataset/nm000513), [release README](https://github.com/nemarDatasets/nm000513), [Ternisien et al. 2023](https://doi.org/10.1007/s10548-023-00940-5), and [Koessler et al. 2015](https://doi.org/10.1007/s10548-014-0417-z).

## Geometry consequence for `ds004752` / `on004752`

The official [NEMAR release description](https://www.nemar.org/dataset/on004752)
and [dataset repository](https://github.com/nemarDatasets/on004752) describe 15
participants, standard 10–20 scalp EEG, depth iEEG, MNI intracranial contact
coordinates, and LCMV-derived virtual sensors. The primary [Scientific Data
paper](https://doi.org/10.1038/s41597-020-0364-3) describes intracranial
localization from post-implant CT/MRI followed by normalization to MNI space.
The locally downloaded `ds004752_v1.0.0_full` snapshot was checked for NIfTI
images and contains no participant MRI files. Consequently, the release cannot
support an individualized scalp-to-MRI forward model in this workspace. A
template-head analysis could be a separately labelled exploratory transport
experiment, but it would not verify participant-specific source geometry or
provide an independent test of the active source-family estimand.

## What would genuinely close the reference gap

For **source-set coverage / false-confident attribution**, acquire an independent measured cohort with a spatially registered, event-matched neural source reference sufficiently complete for the target claim, and participant-disjoint calibration and test groups. Examples may include carefully selected interictal events with simultaneous scalp and intracranial recordings plus validated contact coordinates, but sparse SEEG alone still samples only implanted sites. Alternatively, use an experimentally controlled endogenous neural event whose location and extent are independently established at the relevant time scale. A stimulation contact validates the stimulation location, not a later distributed response generator.

For a more limited WSGZP claim, keep the output model-conditional and evaluate a separately frozen fixed-area shortlist against sampled responsive SEEG contacts. That can answer whether the report helps prioritize follow-up recording sites; it cannot validate the full compatible set.

## Novelty decision update

The data search does not uncover a ready-made dataset that upgrades the present WSGZP endpoint to true-source calibration. The most promising alternate route for direct endogenous scalp/iEEG events (`nm000513`) has missing spatial reference coordinates and strong same-cohort prior work. HDEEG offers a richer clinical proxy but remains access-limited and its outcome is not direct source truth. Therefore novelty must currently be proved, if at all, as a bounded empirical decision benefit on WSGZP or as a genuinely new mathematical guarantee; neither is demonstrated. If these limitations make the required validation impossible, report that the full source-truth claim cannot be supported with available data rather than substituting a weaker endpoint without saying so.
