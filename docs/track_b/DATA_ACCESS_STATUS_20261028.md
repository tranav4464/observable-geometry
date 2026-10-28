# Measured-data acquisition status

**Date:** 28 October 2026  
**Protocol:** COG-2026-10-28-v1  
**Primary neural recordings downloaded:** no

This is an access/provenance checkpoint, not a scientific result. The primary
validation must use measured recordings, but data must not be treated as
permitted merely because a landing page is public.

## What was acquired

Metadata-only files are in
`observable_geometry/data/metadata_20261028/` and are listed with SHA-256
hashes in `DATA_ACQUISITION_MANIFEST.json`:

* the WSGZP `eeg_badtrials.json` file;
* the official UNIGE HDEEG dataset page;
* CC0 ds004752 dataset description, participant table and README.

No neural recording, MRI, outcome, or signal archive was opened or used in
this checkpoint. These files cannot enter calibration or the novelty claim.

## Why the two primary archives remain gated

The WSGZP OSF project exposes multipart signal files but its project license is
labelled **Other** and instructs users to read `license.txt` in storage. The
visible metadata listing does not expose that file. We therefore need the
custodian's permission or an authorized route that exposes the exact terms
before downloading or using the signal archive.

The HDEEG dataset page identifies the EBRAINS dataset and its contents, but
retrieval is controlled through EBRAINS dataset-specific access terms. An
EBRAINS account and accepted terms, or written custodian confirmation, are
required before raw data access.

The ds004752 metadata identifies a CC0 OpenNeuro release. Its full archive is
large, so the metadata was downloaded first; raw files can be fetched after the
participant/session subset and disk budget are locked.

## Next access gate

Before any raw download, record the accepted license/terms, dataset version,
archive manifest and expected SHA-256 values. Then download into a separate
read-only raw-data directory and run a metadata-only BIDS/channel/geometry
audit. Do not inspect held-out outcomes before the COG split, preprocessing,
source-family definitions, uncertainty grid, metric and stopping rule are
frozen.
