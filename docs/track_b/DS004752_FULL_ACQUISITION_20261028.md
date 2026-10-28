# ds004752 full-release acquisition and integrity audit

**Acquired:** 28 October 2026  
**Release:** NEMAR `on004752` v1.0.0 (derived from OpenNeuro ds004752 v1.0.1)  
**License declared by release:** CC0  
**Raw-data directory:** `observable_geometry/data/raw_20261028/ds004752_v1.0.0_full/`

## Download result

The NEMAR manifest contained **923 files** and **12,829,887,301 bytes**.
All files were downloaded or resumed from partial content. The manifest and
per-file verification record are stored as `NEMAR_MANIFEST.json` and
`DOWNLOAD_CHECKS.json` in the raw-data directory. No SHA-256 mismatch was
reported for entries whose manifest checksum algorithm is SHA-256; entries
using NEMAR's Git-object checksum were verified for the declared byte size and
their computed SHA-256 is retained in the verification record.

## BIDS structural check

The archive contains 15 subjects, 68 scalp-EEG EDF recordings, 68 iEEG EDF
recordings, 68 EEG event files and 68 EEG channel files. The release metadata
declares CC0 and identifies the OpenNeuro source DOI.

## EDF header check and exclusion record

MNE opened **134 of 136** EDF headers. Two files contain an invalid EDF start
time with a seconds field of `60`, which MNE correctly rejects:

* `sub-06/ses-04/ieeg/sub-06_ses-04_task-verbalWM_run-01_ieeg.edf`
* `sub-14/ses-06/eeg/sub-14_ses-06_task-verbalWM_run-01_eeg.edf`

The original bytes are preserved and must not be edited in place. These files
are excluded from any analysis until a documented, lossless parser repair is
independently validated, or they are explicitly treated as missing. This is a
data-quality limitation, not evidence against the dataset or the COG method.

No neural signal has been used for calibration or a novelty claim from this
download. The full release is a measured-data benchmark and remains separate
from the permission-gated iES-CCEP/WSGZP and HDEEG primary routes.
