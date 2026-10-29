# WSGZP extracted-dataset integrity check

**Date:** 28 October 2026\
**Scope:** archive inventory, file sizes, and CRC replay only. No EEG/iEEG signal values were analyzed.

## Result

The extracted tree `wsgzp datset/extracted/ccepcoreg` matches the multi-volume archive inventory:

- 2,914 archive files and 2,914 extracted files
- no missing or extra files
- no file-size mismatches
- total uncompressed size: 25.89 GiB
- every extracted file matched the archive entry CRC: 0 mismatches across 27,798,537,813 bytes

The six archive volumes (`ccepcoreg-bids.z01`–`.z05` and `.zip`) also match the byte counts and SHA-256 values in `wsgzp datset/data/WSGZP_DOWNLOAD_MANIFEST.json`. The archive parts and manifest were retained. A requested cleanup attempt to remove the verified duplicate archive parts was rejected by the execution policy, so the archives remain on disk.

## What this verifies

This verifies that the extracted files are byte-consistent with the downloaded archive entries and that the downloaded archive parts match the recorded manifest. It supports using the extracted dataset as a complete local copy. It does not verify dataset scientific validity, coordinate registration, preprocessing, or source-localization accuracy.

## Reproduction

The inventory was read from the archive directory with 7-Zip's listing mode. A streaming CRC32 pass compared each extracted file with its archive entry; each file was read in 8 MiB blocks. The separate download manifest was checked against archive-part byte sizes and SHA-256 values. The check did not materialize or analyze EEG/iEEG samples.

## Next data-model gate

The dataset is locally complete, but the WSGZP forward-model gate remains open. A participant-specific scalp/skull/brain model, electrode/MRI overlay review, source space, covariance, and forward operator are still required before WSGZP signal fitting. The coordinate-only audit does not satisfy those requirements.
