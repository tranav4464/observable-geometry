# B1 synchronization-source audit

> **Historical NeuroFlowNet/on004752 route evidence, superseded 23 October 2026.** This audit concerns a different dataset and estimand. It does not establish feasibility or evidence for the active GBFs/Localize-MI project; consult `PROJECT_DEFINITION.md` and `GATE_REGISTER.json`.

**Run:** `20261022T181119Z_b1_sync_source_audit`
**Gate:** B1, alignment feasibility now PASS for event-relative 50 Hz epochs
**Scope:** primary-source code, BIDS metadata, development event rows, and one real development trial's signal arrays. No outcomes or samples from sub-04 through sub-15 were read.

## Decision question

Can the released on004752 BIDS files reproduce or independently validate the authors' continuous scalp–intracranial synchronization procedure well enough to approve WBEN's paired time-series endpoint?

## Primary-source procedure

The authors' public MATLAB repository was pinned at commit `395ae136372be9772cdbeb09bccd677fda01b5d6`. Its `Synchronize NLX-EDF/Main_Synchronize_NLX_EDF.m` has SHA-256 `70EFD92B686ABDEA20362FFAC3D1F7622D4F4481285C1542C7D8236859C43895`; the source copy and upstream Apache-2.0 license are preserved in this run folder.

The script hard-codes participant 37 and session 4. It loads a continuous EDF and a separate Neuralynx `.mat` file, uses scalp `EDF channel 2 - channel 1` and `NLX channel 15`, filters both 5–30 Hz, cross-correlates the streams, and cuts scalp channels 49–67 to a trial window corresponding to the NLX trial. The source calls the selected channels synchronization channels in variable names and comments, but does not establish that either is a digital hardware trigger. This script demonstrates that the authors used a signal-based lag estimate in this particular workflow. It is not proof that the same raw channels, rate, or alignment procedure apply to every BIDS recording.

The eLife methods report that the scalp EEG, ECoG, and LFP were recorded on a Neuralynx ATLAS system at 4,000 Hz and downsampled to 500 Hz for the publication analyses. The public BIDS release instead has 19 scalp channels at 200 Hz and 48 depth-SEEG channels at 2,000 Hz in the audited development session. Its `channels.tsv` files contain no channel named for sync, trigger, or stimulation; the EEG and iEEG sidecars each declare `TriggerChannelCount: 0`. The BIDS README says the EDF files contain continuous recordings and that `events.tsv` gives trial starts and ends. It says BIDS conversion used bids-starter-kid plus custom MATLAB scripts, but those conversion scripts are not in the pinned release repository. Thus the exact signal-based synchronization inputs and conversion history cannot be reproduced from the released files on the current evidence.

## Development-only event and sample audit

The reusable metadata audit is `outputs/track_b/20261022T181119Z_b1_sync_source_audit/bids_alignment_metadata_audit.json`. It scanned channel metadata for all 68 paired sessions and read event rows only for the 14 sessions belonging to `sub-01` through `sub-03`, which are designated development-only. The follow-up real-data audit is `outputs/track_b/20261022T182700Z_b1_alignment_verification/alignment_feasibility.json`; it checked event-index arithmetic across those same 14 sessions and loaded one real trial from sub-01/ses-01 only. No event rows or signal samples from sub-04 through sub-15 were read.

In all 14 development sessions:

- EEG and iEEG event tables have the same `nTrial` order, number of rows, and task labels.
- Both streams have 8-second trial intervals. The EEG sampling rate is 200 Hz and the depth-iEEG rate is 2,000 Hz.
- The event tables store one-based inclusive sample bounds (`begSample`, `endSample`) and calculate `onset` as `begSample / SamplingFrequency`. That formula makes the first onset 0.005 s for 200 Hz EEG and 0.0005 s for 2,000 Hz iEEG, creating the apparent 4.5 ms difference.
- Converting the one-based start index to a zero-based sample time, `(begSample - 1) / SamplingFrequency`, makes the paired start and end boundaries exactly equal in all rows of all 14 development sessions. The 4.5 ms difference is therefore an event-table indexing convention, not evidence of a measured physical inter-stream delay.
- Each modality contains the same 8-second trial window. For sub-01/ses-01/trial-1, the actual EDF arrays contain 19 × 1,600 scalp samples and 48 × 16,000 intracranial samples. Anti-aliased polyphase resampling from 200/2,000 Hz to 50 Hz yields 19 × 400 and 48 × 400 values, all finite. This was a shape/feasibility check only; no model was fit and no signal values were saved.
- No channel metadata names a sync, trigger, or stimulation channel.

This supports matching released trial windows and placing each modality on a common event-relative grid for the published 50 Hz analysis. The eLife acquisition report says scalp EEG, ECoG and LFP were recorded by the same Neuralynx ATLAS system; the WBEN paper then describes this exact dataset as paired 8-second epochs at 200 Hz EEG and 2,000 Hz iEEG, both downsampled to 50 Hz. The BIDS event-boundary arithmetic and real-array check agree with that representation. This is sufficient for a bounded reproduction of the event-locked 50 Hz task. It does **not** validate arbitrary alignment of the authors' separate continuous EDF/NLX files, sub-sample physical timing, phase claims finer than the shared grid, or causal interpretation.

## Decision

**B1 passes for the event-relative 50 Hz reproduction/challenge endpoint.** The project may pair the released 8-second trials by `nTrial` and task labels, convert the one-based inclusive start index to zero-based time, and resample each stream to the published 50 Hz grid. The two sessions with malformed absolute EDF timestamps (sub-06/ses-04 and sub-14/ses-06) are excluded from the primary analysis before outcome access, leaving at most 66 paired sessions. The primary WBEN endpoint must remain prediction of measured held-out contacts/signals under the declared split. It may not claim exact sub-sample synchronization, validation of arbitrary continuous recordings, ground truth for unobserved regions, or causal network edges.

The exact analysis target, filter/resampling implementation, contact-to-region mapping, model settings, split, and metrics remain for B2/B5. WBEN's 50 Hz event-relative representation is now feasible; any higher-resolution timing, phase-coupling, or directional claim needs separate evidence and must not be smuggled in as part of this gate.

The 68-session file inventory is the available paired set in the pinned release. The source paper reports 71 behavioral sessions. The three-session difference remains unexplained; analyses are limited to the released pairs and the two predeclared technical exclusions, with no implication that the release contains all 71 paper sessions.

## Reproduction commands and artifacts

The source file and license are preserved at:

- `outputs/track_b/20261022T181119Z_b1_sync_source_audit/Main_Synchronize_NLX_EDF.m`
- `outputs/track_b/20261022T181119Z_b1_sync_source_audit/UPSTREAM_LICENSE.txt`
- `outputs/track_b/20261022T181119Z_b1_sync_source_audit/bids_alignment_metadata_audit.json`
- `outputs/track_b/20261022T181119Z_b1_sync_source_audit/SESSION.md`

The metadata audit command is recorded in the session record. Its inputs are the local pinned BIDS channel tables and the event tables for `sub-01` through `sub-03` only. Re-running it on another participant's events would change that participant's exposure status and is not authorized by this audit.

## Sources

- Dimakopoulos et al., eLife 2022, [paper and methods](https://elifesciences.org/articles/78677), especially the task, participants, and acquisition/preprocessing methods.
- Yang and Liu, NeurIPS 2025, [WBEN paper](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html), especially Appendix A.4 for event epoch length, sampling rates, and common 50 Hz downsampling.
- Authors' [analysis repository](https://github.com/vdimakopoulos/verbal_working_memory), pinned at commit `395ae136372be9772cdbeb09bccd677fda01b5d6` for the source script copied in this run.
- Pinned [NEMAR on004752 release](https://nemar.org/dataset/on004752) and [dataset repository](https://github.com/nemarDatasets/on004752), which describe simultaneous modalities, trial boundaries, and the custom BIDS conversion.
