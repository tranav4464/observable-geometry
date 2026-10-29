# Measured-data acquisition and analysis status

**Date:** 28 October 2026  
**Protocol:** COG-2026-10-28-v1  
**Primary WSGZP archive:** downloaded and extracted; package integrity matches the six-part download manifest
**Signal-value analysis:** not performed in the metadata, license, and epoch-index audits recorded here

This is an access and provenance checkpoint, not a scientific result. The
presence of downloaded recordings does not authorize confirmatory analysis or
establish that the data can answer the novelty question.

## WSGZP acquisition and reuse terms

The complete multipart archive is in `wsgzp datset/data/`; its extracted
dataset is in `wsgzp datset/extracted/ccepcoreg/`. All six archive components
match their recorded byte counts and SHA-256 values in
`wsgzp datset/data/WSGZP_DOWNLOAD_MANIFEST.json`. The extracted package-level
`LICENSE` declares CC BY-NC-SA 4.0, and `dataset_description.json` independently
declares `CC-BY-NC-SA 4.0`.

The package terms permit noncommercial use subject to attribution and
ShareAlike requirements. Keep the data and participant MRI outside Git and
respect any additional privacy, ethical, or institutional constraints. The
license resolves the earlier package-license uncertainty; it does not clear
the scientific or protocol gates.

The metadata and epoch-index audits used BIDS JSON/TSV files, the bad-trial
JSON, and NPY headers only. They did not load EEG or SEEG sample values for
analysis. The trial-index audit found count agreement for 317/323 EEG runs,
but the mask semantics/order are undocumented and six runs disagree. It does
not establish independent event identity, non-overlap, or EEG–SEEG trial
pairing. See `WSGZP_METADATA_AUDIT_20261028.md` and
`WSGZP_PREPROCESSING_PROVENANCE_20261028.md`.

## Other data routes

HDEEG-IED-SurgOutcome has not been acquired or analyzed. Its dataset-specific
EBRAINS access terms and the outcome-blind eligibility/QC crosswalk remain
unresolved. No surgical-outcome or clinical claim is authorized.

ds004752 remains a separately documented historical scalp-to-iEEG benchmark;
it does not validate the current participant-specific GBF source-family
certificate or establish novelty for this extension.

## Why WSGZP analysis is still gated

The 2026 GBF article already analyzes this data route, so WSGZP can support
only a carefully delimited secondary question, not independent cohort
validation. The intervention contact is not complete ground truth for later
distributed CCEPs; SEEG supplies sparse positive observations. Exact trial
matching is unavailable in the released metadata, preprocessing is inherited
and incompletely traceable at the exported-array level, and participant
coordinate/forward-model review remains open. The confirmatory protocol is
still `UNLOCKED`.

Do not fit models or inspect confirmatory outcomes until the prior-art delta,
valid endpoint, geometry/forward construction, source-family definitions,
uncertainty set, participant split, calibration, baselines, stopping rule,
and independent preflight are resolved and frozen. If these gates cannot be
met, report that the dataset does not support the proposed novelty test.

## Reproducible records

* Download-part hashes and sizes: `wsgzp datset/data/WSGZP_DOWNLOAD_MANIFEST.json`.
* License SHA-256: `e75267dc97f015d72a6571e3a761519b1466f47da98d12f3a6d4c5f726fe2a60`.
* Dataset-description SHA-256: `60e16737e8b487dc0876a70f4d920e0537f23928adc48741cfa13fda5987ab94`.
* Metadata audit: `outputs/track_b/20261028_wsgzp_metadata_audit/audit.json`.
* Trial-index feasibility audit: `outputs/track_b/20261028_wsgzp_trial_index_feasibility/trial_index_audit.json`.
