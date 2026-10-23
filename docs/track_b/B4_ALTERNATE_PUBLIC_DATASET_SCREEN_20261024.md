# B4 alternate public dataset screen

**Screen date:** 24 October 2026  
**Purpose:** Determine whether an already public real dataset can reopen B4 for EEG source-pattern distinguishability under an individual forward model.  
**Data boundary:** Metadata and published descriptions only. No neural-signal samples were opened for this screen.

## Decision

**No screened alternative presently reopens B4–B6.** The available public candidates either lack the paired geometry required by the active GBF question, have already been used for closely related source-imaging analyses, or do not have an identifiable public release of the required records. This is a feasibility decision, not evidence that no such dataset exists. The bounded GBF reproduction and model-conditional diagnostic remain the supported project deliverable unless a qualifying source is found or supplied.

## Requirements for a qualifying dataset

To test whether the current GBF distinguishability output predicts a useful real-data outcome, the dataset must provide, for the same participant and acquisition:

1. scalp EEG with sensor positions, channel names/order, units, reference, and preprocessing provenance;
2. a participant-specific forward model or the MRI, tissue surfaces, transforms, electrode positions, and conductivity information needed to recreate and verify one;
3. an independent, spatially registered reference appropriate to the outcome, such as intracranial contacts and event timing, while acknowledging that SEEG samples only implanted locations;
4. enough independently repeated events/conditions and participants for the proposed split and unit of inference;
5. public access, license, and data-use terms that permit the proposed reproducible analysis; and
6. a task-level prior-art comparison showing what new decision the GBF output would add beyond existing ESI, resolution, source-separability, and EEG–SEEG comparison methods.

Availability of scalp EEG and intracranial EEG somewhere in a cohort is not sufficient: the pairing, geometry, reference, independent unit, and intended outcome must all be verified.

## Candidate screen

| Candidate | What primary/public records establish | Fit to the active GBF question | Disposition |
|---|---|---|---|
| Localize-MI | Seven participants with individual anatomical/forward-model resources and intracranial stimulation paired with scalp EEG. The existing B4 audit establishes that the evaluated pulse is a stimulation artifact, not an endogenous response. Site–intensity conditions occur in one run, and the cross-intensity held-out comparisons are sparse and uneven. | Best available participant-specific geometry, but the target mismatch and run structure do not support the planned physiological or participant-level confirmatory claim. | Keep B4–B6 pivoted for the current endpoint. Do not open reserved participant outcomes. See the B4 reopening proposal and metadata feasibility report. |
| NEMAR/OpenNeuro `on004752` | Fifteen participants with simultaneous low-density 10–20 scalp EEG and depth iEEG during verbal working memory; MNI contact coordinates and task labels are available, with 68 paired sessions in the pinned audit. | The task can support a distinct scalp-to-contact prediction question, but it does not provide the verified participant-specific MRI/forward-model contract required by the active GBF estimand. Close prior work already analyzes working-memory load, scalp-source/hippocampal coupling, and joint scalp+iEEG network inference on this cohort. | Retain as historical evidence from the superseded NeuroFlowNet/WBEN route. Do not reopen the current GBF spatial-pair evaluation by silently changing its question or head-model contract. See `B1_PHYSIOLOGICAL_DATASET_SCREEN.md` and `B0_WBEN_NEURIPS_2025_AUDIT.md`. |
| NEMAR `nm000513`, “Simultaneous EEG-SEEG recordings of deep mesial temporal sources” | The public release describes seven patients, nine networks, and 1,945 simultaneous interictal spike epochs. The public README states that SEEG contact coordinates are not released and lists them as `n/a`; it cites prior papers analyzing these recordings. | Simultaneous EEG/SEEG is useful for a different prediction or detection question, but the released contact geometry is insufficient for a verified participant-specific GBF forward model, and the source-detection task has direct prior analyses. | Do not use as a source-distinguishability validation set. Reconsider only if usable geometry is obtained and a distinct question survives a new prior-art review. |
| NEMAR `nm000456`, “Human-AI collaboration for co-managing epilepsy in real time” | The v1.0.2 NEMAR participant table classifies 11 of 13 participants as `Scalp`/`eeg` and two as `SEEG`/`ieeg`. The release is 514 GB and licensed CC-BY-NC-SA-4.0. The associated article describes a patient-facing seizure-monitoring system, not a participant-specific EEG source-localization benchmark. | The released participant metadata do not establish paired scalp and SEEG streams within the same participants, and the public record does not establish the intracranial contact geometry plus individual forward models needed here. The dataset is also a poor fit for source-pattern distinguishability. | Exclude from B4 reopening. It may be relevant to a separate seizure-monitoring project, not this GBF evaluation. |
| Hao et al. 2025, “HD-EEG source imaging with simultaneous SEEG recording in drug-resistant epilepsy” | The paper reports 29 analyzed patients with simultaneous 64-channel scalp EEG and 64–192 SEEG channels, and directly evaluates ESI relative to SEEG-defined sources. Its data statement says de-identified recordings will be placed in a public repository with a DOI upon publication and directs pre-release requests to the corresponding author. | Scientifically relevant, but the paper itself is close source-imaging prior art. As of this screen, the paper page did not identify a public repository DOI or downloadable underlying recordings; the methods and results alone are not a reproducible evaluation dataset. | Not currently available for an independent build. A future release could be re-screened for full geometry, license, usable independent events, and overlap before any outcomes are accessed. |
| Zauli et al. 2024, “Localizing hidden interictal epileptiform discharges with simultaneous intracerebral and scalp high-density EEG recordings” | The study reports simultaneous scalp and intracranial recordings and evaluates localization of hidden interictal discharges. A public OSF release is identified in the repository's earlier screen. | The study is directly on source localization and therefore close prior art. The earlier local metadata screen found only one released intracranial contact per participant and no adequate competing source-pair geometry for the current pairwise GBF estimand. | Not a qualifying validation set for the current GBF question. Preserve as close prior art and a possible separate reproduction target only if data terms and geometry are independently rechecked. |

## Prior-art implications

The alternatives reinforce rather than remove the novelty constraint. EEG–SEEG translation and source imaging already have direct literature, including work on simultaneous scalp/intracranial events and ESI validation. A future dataset alone would not make the GBF cosine a new method. Any reopening needs to state a different, testable decision, match established comparators, and avoid treating implanted contacts as complete brain ground truth.

The 2025 Hao et al. study is especially close to the proposed empirical direction: it reports simultaneous 64-channel scalp EEG and SEEG, uses SEEG-informed source imaging, evaluates localization distance, and concludes that larger simultaneous datasets are needed. Its published data statement does not currently give a public data DOI. This makes it a potential future collaboration or data-access lead, not a present independent validation route.

## Gate consequences

- **B4:** Remains **PIVOT** for empirical validation of endogenous source distinguishability. The Localize-MI artifact branch remains closed to confirmatory outcomes. The alternate screen does not authorize signal access.
- **B5:** Remains **PIVOT**. No confirmatory protocol is locked because no qualifying endpoint and dataset pair has passed feasibility and prior-art review.
- **B6:** Remains **PIVOT**. No held-out outcome analysis was performed for these candidates.
- **B7:** Remains **PIVOT** for researcher decision utility. Model-only association with MNE PSF summaries is descriptive and cannot establish decision benefit.
- **B8:** This screen is additional provenance for the release packet. It does not replace the outstanding unaffiliated external review or independent reproduction.

## Reopening checklist

Reopen the empirical branch only after a candidate has a versioned public data record and license, a metadata-only pairing/geometry audit, adequate independent units for a prespecified split, a precise outcome and decision, a matched prior-art review, and independent technical review of a frozen protocol. If no candidate meets these conditions, finish the bounded reproduction and state plainly that no valid empirical test or novel method was established.

## Sources checked

- Localize-MI dataset paper: [Nature Scientific Data, 2020](https://doi.org/10.1038/s41597-020-0467-x); local B4 feasibility evidence is linked in `B4_ARTIFACT_VALIDATION_REOPENING_PROPOSAL_20261024.md`.
- NEMAR `nm000513` release: [dataset repository](https://github.com/nemarDatasets/nm000513); the repository README records seven participants, nine networks, simultaneous epochs, no released SEEG contact coordinates, and prior analyses.
- NEMAR `nm000456` release: [version 1.0.2 dataset record](https://nemar.org/dataset/nm000456?v=v1.0.2); its public `participants.tsv` and release description provide the modality counts, license, and scale.
- Hao et al. 2025: [Epilepsia article, DOI 10.1111/epi.18552](https://doi.org/10.1111/epi.18552); the article's methods and data-availability statement are the sources for cohort and release status.
- Zauli et al. 2024: [Journal of Neuroscience Methods, DOI 10.1016/j.jneumeth.2024.110193](https://doi.org/10.1016/j.jneumeth.2024.110193); its dataset details and prior-art proximity are recorded in the existing project screen.
