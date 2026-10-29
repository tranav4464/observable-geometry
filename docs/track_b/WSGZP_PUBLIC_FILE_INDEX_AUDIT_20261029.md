# WSGZP public file-index audit

**Checked:** 29 October 2026 (18:38 UTC)\
**Evidence class:** public file metadata only; no EEG/SEEG samples read\
**Purpose:** determine whether publicly indexed WSGZP files resolve the
released-run mapping and trial-count discrepancy.

## Inventory

The public OSF v2 file API lists six files under `/data/`: the multipart
`ccepcoreg-bids.zip` archive (`.z01`–`.z05` plus `.zip`). Under
`/additional_info/`, it lists only `eeg_badtrials.json`. The extracted BIDS
root contains a README describing 323 sessions from 36 participants,
`participants.tsv`, and per-participant derivative `scans.tsv` files. The
sub-36 `scans.tsv` lists run filenames but no acquisition timestamps. The
metadata tables list epoch duration, zero-time and run-level `trial_type`,
not original event IDs or trigger indices.

No public OSF file-index entry or extracted-file search located a generated
`runs_table.csv`, event table, run chronology/session crosswalk, or the
paper's 379-to-323 selection table. The official curation repository's
exporter consumes an external `runs_table.csv`; its exact released input is
not in the indexed dataset files. This is a bounded negative finding about
the checked public file inventory, not proof that the authors do not retain
those records elsewhere.

## Consequence for the novelty route

The public derivative cannot currently resolve whether sub-36/run-06, with
13 EEG and 15 iEEG metadata rows, belongs to the paper's analyzed 323-session
set despite the publication's exclusion of sessions with fewer than 25
retained trials. The sub-14 pair is the only same-condition candidate whose
four modality-specific row counts all meet 25, but the file inventory does
not establish that it is two independent acquisitions or independent
preprocessing. Therefore the public files do not support a confirmatory
repeatability analysis.

This does not by itself block a participant-held-out, in-observation
compatibility analysis with sparse SEEG-positive corroboration, but that
endpoint is weaker than source-recovery truth and must beat matched methods
to support an empirical contribution. It also does not solve the open
geometry/forward-model and protocol-lock gates. No signal fitting is
authorized by this inventory.

## Reproduction record

Machine-readable listing: `outputs/track_b/20261029_wsgzp_osf_file_index.json`.
It records the API endpoint, returned paths, timestamp and evidence boundary.
The public OSF project is [OSF: WSGZP](https://osf.io/wsgzp/). The relevant
primary paper is Parmigiani et al. (2022), [DOI
10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007).
