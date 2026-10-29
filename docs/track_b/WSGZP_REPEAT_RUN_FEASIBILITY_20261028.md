# WSGZP candidate repeated-run feasibility audit

**Initial metadata audit:** 28 October 2026\
**Official exporter semantics checked:** 29 October 2026\
**Evidence class:** metadata-only; no signal samples read\
**Purpose:** determine whether the released WSGZP derivative provides a basis
for an independent same-condition run-repeat endpoint relevant to the
Observable Geometry novelty test.

## Question and method

The audit enumerated paired EEG and iEEG BIDS epoch TSVs under the extracted
`ccepcoreg` derivative. Within each participant, it compared exact `trial_type`
sets across distinct run tables and recorded epoch counts, available metadata
columns, and TSV SHA-256 hashes. It did not open NPY, FIF, or other recording
arrays; did not read EEG/SEEG values; and did not treat row order as event
identity.

Implementation: `scripts/track_b/audit_wsgzp_repeat_run_conditions.py`\
Machine-readable outputs (v1 is preserved; v2 adds the pinned run-ID
semantics finding):
`outputs/track_b/20261028_wsgzp_repeat_run_audit/repeat_run_inventory_v3.json`

Reproduce from the `observable_geometry` directory:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_repeat_run_conditions.py `
  --dataset-root "C:\Users\TRANAV\OneDrive\Desktop\TKS\wsgzp datset\extracted\ccepcoreg" `
  --output outputs\track_b\20261028_wsgzp_repeat_run_audit\repeat_run_inventory_v3.json
.venv\Scripts\python.exe -m pytest tests\test_wsgzp_repeat_run_conditions.py -q
```

## Result

The inventory covered 323 paired run tables and found no missing EEG/iEEG
modality table. All 323 paired run tables had identical condition-string
sets across EEG and iEEG metadata. Two distinct-run pairs repeated the same
exact condition within the same participant at the metadata level. Applying
the paper's stated minimum of 25 retained trials as an eligibility check
leaves only sub-14 as a potential candidate based on counts; neither pair has
verified acquisition independence:

| Participant | Runs | Exact condition | EEG epochs | iEEG epochs |
|---|---|---|---:|---:|
| sub-14 | 01 / 02 | `K'7-8 5ma 0.5ms 0.5hz parallel gr_wh` | 37 / 36 | 40 / 40 |
| sub-36 | 06 / 07 | `O1-2 3ma 1ms 1hz parallel gr_wh` | 13 / 25 | 15 / 30 |

The EEG and iEEG epoch TSVs expose `duration`, `zero_time`, and `trial_type`
only. They contain no event/trial identifier or onset/sample index that
would establish trial correspondence. The EEG and iEEG epoch counts differ
within both candidate pairs.

## Published-study eligibility discrepancy

The primary data paper reports 30 or 40 consecutive stimulation trials per
session and says that the analyzed set retained 323 of 379 sessions after
excluding nine sessions with evoked epileptic spikes and 47 sessions with
fewer than 25 retained trials. The released derivative has 323 paired run
tables, but sub-36 run 06 contains only 13 EEG and 15 iEEG epochs. This is
below the paper's stated 25-trial threshold and is not explained by the
metadata or exporter evidence inspected so far. It may reflect a difference
in what the paper counts versus what the derivative exports, or a selection
or curation mismatch; the cause is unknown.

Consequently, the sub-36 runs 06/07 pair is **not an eligible repeat candidate
for a paper-matched analysis unless its membership and trial-count semantics
are reconciled**. Run 07 has 25 EEG and 30 iEEG epochs, but that does not
rescue the pair when run 06 is below the published minimum. Sub-14 runs 01/02
both exceed 25 rows in both modalities, but remain only a candidate pair:
acquisition independence, chronology, event overlap, and preprocessing
independence are still unknown. The 323-run count matching the paper's 323
retained sessions does not resolve this run-level discrepancy.

The paper's threshold is an eligibility cross-check, not proof that each TSV
row is a unique retained trial or that the released derivative exactly
matches the paper's analysis set. Ask the data custodians to reconcile the
selection table, trial counts by modality, and the two candidate run pairs
before any repeatability analysis.

Machine-readable cross-check: `outputs/track_b/20261029_wsgzp_repeat_run_paper_check.json`.

The public OSF file index was checked separately and lists only the six
archive parts under `/data/` plus `eeg_badtrials.json` under
`/additional_info/`; it provides no run-map or session-selection table. See
`WSGZP_PUBLIC_FILE_INDEX_AUDIT_20261029.md` and its machine-readable listing.

Source: Parmigiani et al. (2022), [dataset paper, DOI
10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007), Methods
sections 2.4–2.6. The article states the session trial counts and the 323/379
retention with the stated exclusions. This audit does not independently
recreate the authors' session-selection table.

The pinned curation repository does not let us assign a session or
independence meaning to these released run IDs. It contains one helper that
creates `run_id` as a sequential within-subject counter and another that
derives `run_nr` from sorted filenames. The BIDS exporter reads a generated
`runs_table.csv` and passes each row's run ID into the output name, but that
table is not included in the repository and the published code does not
establish which helper produced the released mapping. Therefore the run
numbers establish distinct exported run tables, not chronology, session
separation, or statistical independence. See the [run-ID helpers](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L876-L961)
and [exporter input](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/export_bids.py#L365-L450).

## Interpretation and decision

These are **candidate same-condition run-table repeats**, based solely on
exact matching condition labels in distinct run tables. The metadata and
exporter do not establish whether they were independent acquisitions, how far
apart they occurred, whether the runs were in one session, whether epochs
overlap, or whether any preprocessing
(including artifact/ICA estimation) was fitted jointly. The two participants
also do not provide a confirmatory sample for a general repeatability claim.

Therefore:

- The earlier blanket statement that no same-condition run pair had been
  identified is superseded by this metadata inventory.
- The independent-repeat gate remains **unresolved**, not passed.
- Do not split events or rows, claim EEG–SEEG trial matching, or use this
  finding as a primary validation endpoint.
- After the protocol, geometry, and signal-access gates close, the two pairs
  are not a repeatability dataset. Only sub-14 passes the paper's simple
  25-row screen, and it is a single-participant pair with unverified
  acquisition and preprocessing independence. If those facts are confirmed,
  it could support a descriptive within-participant run comparison, not a
  confirmatory repeatability estimate or generalization claim. Sub-36 remains
  excluded from a paper-matched repeat test unless its count/selection
  discrepancy is reconciled.
- This metadata result does not establish source localization, neural
  repeatability, physiological source recovery, or a novel method.

The custodian query was updated to ask about these exact pairs. It remains a
draft and has **not** been sent. `docs/track_b/PROTOCOL_LOCK.md` remains the
authoritative gate for any signal access; this audit does not authorize signal
analysis.

## Integrity

The v3 audit output records `signal_samples_read: false` and
`recording_arrays_opened: false`, includes the input TSV hashes, and records
the pinned run-ID semantics source. The v1 output is retained unchanged. The
script's tests check detection of candidate repeats and the explicit
independence limitation. Current artifact hashes are recorded in the task
summary and can be regenerated with `Get-FileHash` before a release.
