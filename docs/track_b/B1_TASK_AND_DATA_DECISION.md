# B1 task and real-data decision

> **Superseded on 23 October 2026. Historical NeuroFlowNet/WBEN route only.** The active build is GBFs reproduction and nominal source-distinguishability under one verified participant-specific head model. Do not use this file as an active task, protocol, or gate contract. See `PROJECT_DEFINITION.md`, `GBF_BUILD_PLAN.md`, and `GATE_REGISTER.json`.

**Active-route clarification (2026-10-23): B1 passes real-data compatibility for the selected 200 Hz waveform task, at the bounded scope below.** The separate 50 Hz event-relative representation was verified for the earlier WBEN route and is now historical. For the active NeuroFlowNet-inspired route, the development-only 200 Hz audit verified paired event alignment, sample shapes, and finite resampling output in 14 sessions; the task-window audit separately checked the candidate late-maintenance interval. These checks establish data and task-window feasibility only. They do not establish exact reproduction of NeuroFlowNet's original dataset/protocol, full preprocessing fidelity, predictive performance, or held-load transfer. The active project uses real recordings only. Synthetic datasets and simulated performance are excluded from the project's primary experiments. Earlier synthetic feasibility runs remain historical artifacts and are not evidence for the current build.

## Selected real dataset

Use the pinned NEMAR mirror **on004752 v1.0.0** (source OpenNeuro ds004752 v1.0.1; DOI `10.82901/nemar.on004752`). The official NEMAR record describes 15 epilepsy patients performing a verbal working-memory task, with simultaneous scalp EEG and depth iEEG, electrode coordinates/labels, and trial-level behavior. The release metadata identify its license as CC0. The source page lists 11.7 GB for the archive; the pinned manifest contains 816 raw EEG/iEEG BIDS files totaling 10.23 GB, before small root metadata files. Preserve the release citation and source version in all derived reports.

The selected raw EEG/iEEG payload is downloaded to `data/track_b/on004752_v1.0.0/`. All 816 files (10,984,433,222 bytes) passed an independent size/checksum audit against the pinned manifest. The manifest contains 68 paired sessions across 15 participants. The eLife paper reports 71 sessions; the three additional sessions are not present as paired files in this pinned release. The project is explicitly limited to the 68 released pairs and does not assert why the other sessions are absent. Do not redistribute the recordings in project releases; provide the source DOI and reproducible acquisition instructions instead.

## What this dataset can test

The paired recordings support a **real-data prediction task**: fit on scalp EEG and evaluate prediction of measured iEEG contact waveforms on held-out trials. The active candidate uses a within-participant held-load split and late-maintenance windows, as specified in `B2_NEUROFLOWNET_SPEC.md`. The full protocol, final preprocessing, matched baselines, and scoring rule remain unfrozen until B2–B5 are complete.

The dataset has no ground-truth network for unobserved regions. It cannot establish that a fitted edge is a true anatomical connection, that directed statistical relationships are causal, or that the model reconstructed the entire brain. Held-out iEEG prediction is evidence about predicting those measured contacts under the stated split; it is not proof that every latent network edge is correct.

This dataset has already been used by prior studies, including the WBEN method being reproduced. Our result must be described as a reproducible reanalysis and a real-data challenge on the same cohort, not an independent replication cohort or a novel whole-brain estimator. Any methodological contribution needs a precise prior-art distinction and a measurable gain on a prespecified real-data endpoint.

## Outcome exposure and split discipline

The B1 metadata check inspected event tables for `sub-01`, `sub-02`, and `sub-03`. Those participants are development-only and cannot later serve as a confirmatory test set. No event-table values or signal samples from `sub-04` through `sub-15` may be inspected for analysis until B5 has a completed protocol lock and preflight. Downloading and checksum-verifying those files does not itself expose their values to analysis.

The exploratory audit covers 14 sessions across the three development participants. Event tables have matching trial/task fields and 8-second inclusive sample bounds. Their `onset` values equal the one-based formula `begSample / SamplingFrequency`; converting the first sample to zero-based time, `(begSample - 1) / SamplingFrequency`, makes all paired boundaries exactly match. The apparent 4.5 ms EEG/iEEG difference is an indexing convention in the event table, not a measured lag. A follow-up loaded one real 8-second trial and confirmed the released data can be resampled to the WBEN paper's common 50 Hz grid with 400 samples per modality. The source acquisition paper reports the EEG, ECoG, and LFP were recorded by the same Neuralynx ATLAS system; WBEN specifies the same 8-second epoch representation and 50 Hz downsampling. This supports a bounded event-relative reproduction. It does not establish sub-sample timing, reproduce the original continuous EDF/NLX alignment procedure, or license finer-grained phase or causal claims. See `B1_SYNC_SOURCE_AUDIT.md` and `outputs/track_b/20261022T182700Z_b1_alignment_verification/alignment_feasibility.json`.

## Data pipeline decisions still required

Before model fitting, B1 documented and verified:

- Exact sampling rates and recording lengths from every included EDF header and sidecar.
- Channel types, references, units, bad-channel flags, and consistent channel ordering.
- The meaning and alignment of `Artifact`, trial events, task phases, and participant behavior fields.
- Paired event/epoch alignment by the one-based sample convention and event-relative 50 Hz grid; this does not prove continuous-stream synchronization.
- A causal, anti-aliased resampling policy for 200 Hz scalp and 2,000 Hz iEEG data, including the target rate and filter provenance.
- The contact-to-region assignment and how repeated contacts in a region are combined or held out.
- Whether available scalp channels and coordinates support the intended forward operator; the cohort does not provide individual MRIs in the reviewed metadata.
- A split that groups all sessions from a participant together for any participant-generalization claim.
- A real-data endpoint that is supported by the protocol and does not misuse withheld iEEG as complete network ground truth.

The participant split is not yet protocol-locked. Participants 1–3 are development-only after their event rows and one real trial were inspected. Participants 4–15 remain reserved for confirmation until B5 protocol lock and access preflight. This leaves a feasible participant-aware evaluation set, but not an independent external cohort. B2/B5 must define whether held-out participants contribute only prespecified within-participant training trials or are entirely excluded from fitting. Report participants, not windows, as independent uncertainty units. If the remaining cohort cannot support a meaningful comparison, narrow the claim or report exploratory results.

To preserve that split, the all-participant BIDS audit used `scripts/track_b/audit_on004752_bids.py --headers-only`. It checked 68 sessions across all 15 participants: EDF header structure, BIDS sampling-rate sidecars, channel-table dimensions, paired file presence, and declared file sizes, without opening event rows or signal samples. All 68 sessions passed structural checks. Two EDF start-time fields are malformed: sub-06/ses-04 iEEG is `10.28.60`, and sub-14/ses-06 EEG is `14.23.60`. Since standard MNE cannot parse those timestamps and the analysis does not require absolute recording time, the primary analysis will exclude those two paired sessions by a metadata-only technical rule, leaving at most 66 eligible pairs. The original EDFs remain untouched. A separate channels-table audit found cutoff columns appear reversed (`low_cutoff=1000`, `high_cutoff=0.5`); sidecar `HardwareFilters` and the acquisition paper identify the hardware passband as 0.5–1000 Hz. Treat the channels-table fields as a metadata defect, not as preprocessing instructions. Detailed event values from sub-04 through sub-15 remain reserved until B5.

## Existing data and excluded routes

Localize-MI is already present in the workspace and contains real high-density scalp EEG during intracranial stimulation. Its source locations are known, but the recordings are stimulation artifacts rather than spontaneous physiological activity. It is useful as Track A’s development dataset, not as WBEN’s paired spontaneous EEG/iEEG evaluation. The new Track B primary dataset is on004752.

The OSF 89ndr candidate has one iEEG contact per participant and does not support the current multi-contact spatial holdout. Other datasets may be reconsidered only if primary-source documentation shows they materially improve the real-data endpoint and their license and access terms permit use.

## Sources and evidence

- NEMAR on004752 dataset record: <https://nemar.org/dataset/on004752> (v1.0.0, CC0, paired EEG/iEEG, 15 participants, 11.7 GB archive).
- Original task and recording methods: Dimakopoulos et al., [eLife 2022, e78677](https://elifesciences.org/articles/78677). The paper reports 71 total sessions and describes task phases, acquisition, and preprocessing. This build is limited to the 68 paired sessions in the pinned release.
- WBEN method being reproduced: Yang and Liu, [NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html), Appendix A.4 specifies 8-second epochs, 200/2,000 Hz sampling rates, and common 50 Hz downsampling.
- Authors' analysis repository: <https://github.com/vdimakopoulos/verbal_working_memory>. Its README records the preprocessing and analysis workflow; inspect the synchronization scripts against the BIDS release before defining alignment.
- Pinned dataset manifest: `outputs/track_b/20261022T174414Z_b1_on004752_real_data/nemar_manifest_v1.0.0.json`.
- Download selection and checksums: `outputs/track_b/20261022T174414Z_b1_on004752_real_data/raw_eeg_ieeg_file_manifest.json` and `download_status.jsonl`.
- Independent full-file integrity result: `outputs/track_b/20261022T174414Z_b1_on004752_real_data/independent_integrity_audit.json`.
- Dataset description and citation instructions: `outputs/track_b/20261022T174414Z_b1_on004752_real_data/dataset_description.json` and `README.md`.
- Development-only header/event metadata audit: `outputs/track_b/20261022T174414Z_b1_on004752_real_data/development_metadata_audit_sub01_03.json`.
- All-participant header-only audit, with no event rows or samples read: `outputs/track_b/20261022T174414Z_b1_on004752_real_data/all_participants_header_only_audit.json`.
- Prior data screen and historical metadata-only audits: [`B1_PHYSIOLOGICAL_DATASET_SCREEN.md`](B1_PHYSIOLOGICAL_DATASET_SCREEN.md) and [`B1_LOCAL_DATA_AUDIT.md`](B1_LOCAL_DATA_AUDIT.md).
- WBEN prior-art and paper-method audit: [`B0_WBEN_NEURIPS_2025_AUDIT.md`](B0_WBEN_NEURIPS_2025_AUDIT.md).

## Synchronization-source audit

The 22 October source audit found that the authors' public MATLAB synchronization script is not directly reproducible from the pinned BIDS files. The script uses a difference of two channels in a continuous EDF and channel 15 from a separate Neuralynx `.mat` file, bandpasses the streams at 5–30 Hz, cross-correlates them, and cuts the scalp stream to a trial window corresponding to the NLX trial. It is hard-coded to participant 37/session 4. The exact identity of the channels and the BIDS conversion's handling of this step are not established by the script itself.

The BIDS release exposes 19 scalp channels at 200 Hz and 48 depth-SEEG channels at 2,000 Hz in the audited development sessions. Across 136 channel tables (EEG and iEEG for 68 paired sessions), none has a channel named for sync, trigger, or stimulation. The development EEG/iEEG sidecars declare `TriggerChannelCount: 0`. The distributed EDF files contain 50 sequential 8-second epochs per session; trial boundaries are represented in each modality's `events.tsv`. Custom MATLAB scripts were used for BIDS conversion but are not present in the pinned dataset repository.

For the 14 development pairs from sub-01 through sub-03, event rows have the same trial order and task labels. The tables use one-based inclusive sample bounds, but encode onset as `begSample / SamplingFrequency`. Correcting the one-based index to the zero-based timestamp `(begSample - 1) / SamplingFrequency` makes every paired trial boundary identical; the apparent 4.5 ms difference disappears. Thus the offset is an indexing convention, not a measured synchronization error. The real-data check confirms the first released epoch can be read as 19 × 1,600 EEG samples and 48 × 16,000 iEEG samples, which resample to 19 × 400 and 48 × 400 at 50 Hz. Together with the acquisition report and WBEN preprocessing specification, this supports the event-relative 50 Hz endpoint.

**Historical B1 decision:** PASS for reproducing/challenging WBEN on event-relative 50 Hz epochs, using at most 66 paired sessions after the two predeclared malformed-timestamp exclusions. This remains valid evidence for the superseded WBEN route only.

**Active B1 decision:** PASS for real-data compatibility of the held-load waveform candidate at 200 Hz, limited to the development-only event alignment, sample-shape/resampling, and task-window checks documented in `B1_CLOSEOUT.md`, `outputs/track_b/20261023T_b1_200hz_candidate_task_audit/SESSION.md`, and `outputs/track_b/20261023T_b2_task_window_source_audit/SESSION.md`. It does not certify the full preprocessing pipeline, exact NeuroFlowNet reproduction, or held-load model performance. The participant-level confirmation set remains unopened and must be protocol-locked at B5. Do not claim arbitrary continuous-stream synchronization, sub-sample temporal precision, ground truth for unobserved edges, or causal connectivity. The source paper reports 71 sessions while the pinned release contains 68; the reason for the three-session difference is not known and is not inferred.

Evidence: [`B1_SYNC_SOURCE_AUDIT.md`](B1_SYNC_SOURCE_AUDIT.md), [`alignment verification report`](../../outputs/track_b/20261022T182700Z_b1_alignment_verification/alignment_feasibility.json), [`alignment audit session`](../../outputs/track_b/20261022T182700Z_b1_alignment_verification/SESSION.md), [`source audit session`](../../outputs/track_b/20261022T181119Z_b1_sync_source_audit/SESSION.md), and [`metadata audit JSON`](../../outputs/track_b/20261022T181119Z_b1_sync_source_audit/bids_alignment_metadata_audit.json).
