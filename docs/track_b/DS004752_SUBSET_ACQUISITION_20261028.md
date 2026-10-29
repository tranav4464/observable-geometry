# ds004752 measured subset acquisition

**Acquired:** 28 October 2026  
**Release:** NEMAR `on004752` v1.0.0, derived from OpenNeuro
`ds004752` v1.0.1  
**License:** CC0 (declared in `dataset_description.json`)  
**Scope:** participant `sub-01`, session `ses-01` only

This is a measured-data smoke-test subset, not the primary iES-CCEP or HDEEG
validation cohort. It contains one simultaneous scalp EEG recording and one
intracranial EEG recording from the published BIDS release, plus channel,
electrode, event and acquisition metadata. The downloaded subset is 79,886,488
bytes. The raw files are under:

`observable_geometry/data/raw_20261028/ds004752_v1.0.0/`

`DOWNLOAD_CHECKS.jsonl` records the manifest checksum identifier and the
computed SHA-256 for every fetched file. The EDF signal hashes verified for
this session are:

* EEG: `sub-01_ses-01_task-verbalWM_run-01_eeg.edf`, 19 channels at 200 Hz.
* iEEG: `sub-01_ses-01_task-verbalWM_run-01_ieeg.edf`, 48 channels at 2000 Hz,
  SHA-256 `8296A9020841CA6A5202C95750F41F628AAD218552A6B7D9A69063CAA9FFCF6C`.

MNE successfully opened both EDF headers without loading the full signals into
memory. No signal preprocessing or outcome inspection has been performed from
this acquisition, and it is not yet part of the COG primary calibration.

## Why this does not close the primary-data gate

The WSGZP multipart archive has since been downloaded, extracted and verified
against its six-part manifest; the package declares CC BY-NC-SA 4.0. This
supersedes the earlier statement that its archive and reuse terms were
unresolved. The metadata/provenance audits did not analyze signal sample
values, and the WSGZP analysis gate remains closed pending geometry, endpoint,
event/provenance and protocol review. HDEEG remains unacquired because
retrieval is governed by EBRAINS terms.
