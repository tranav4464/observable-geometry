# WSGZP metadata-contract recheck

**Date:** 29 October 2026
**Audit ID:** `WSGZP-METADATA-2026-10-29-v2`
**Scope:** BIDS metadata, TSV rows, MRI/geometry file hashes, and NumPy array headers only. No EEG/iEEG samples were loaded or analyzed.

## Result

The metadata-only audit covered all 36 participants and 323 paired EEG/iEEG runs. It confirmed two blockers relevant to any cross-modal source-imaging validation:

1. **Scalp coordinate metadata are nonconformant and registration provenance is still unresolved for all 36 participants.** Each scalp EEG sidecar declares `EEGCoordinateSystem: T1w` and `AnatomicalLandmarkCoordinateSystem: T1w`, omits `EEGCoordinateSystemDescription`, and populates `IntendedFor` with `sub-XX_T1.nii`; the released MRI is named `sub-XX_T1w.nii`. The target path is absent in every case. The BIDS 1.6.0 EEG coordinate keywords are described in the official [EEG specification](https://bids-specification.readthedocs.io/en/v1.6.0/04-modality-specific-files/03-electroencephalography.html) and [coordinate-systems appendix](https://bids-specification.readthedocs.io/en/v1.6.0/99-appendices/08-coordinate-systems.html): `T1w` is not a listed EEG coordinate-system keyword. The appendix requires the coordinate system to identify origin and axis orientation; `T1w` alone does not do this or document the digitizer-to-MRI transform. A pinned BIDS Validator run (`bids-validator@1.14.10`) reproduced schema errors for both fields when the same coordinate sidecar was placed in a valid metadata-only BIDS fixture. The validator did not report those field errors when run directly on the derivative tree, whose `dataset_description.json` is malformed; the fixture isolates the coordinate-schema check. This establishes metadata nonconformance, **not that the numeric sensor coordinates are anatomically misplaced**. The false `IntendedFor` MRI target is a separate unresolved association issue.

2. **The exported epochs do not support verified trial-level EEG/iEEG pairing.** In 319/323 runs, retained EEG and iEEG epoch counts differ. None of the epoch tables has a shared unique event identifier, onset, or sample index. All 323 runs share stimulation-condition labels, which supports only a candidate run/condition-level average comparison after the signal-processing and repeated-run semantics are independently established. Do not pair arrays by row order.

Additional metadata finding: 50 good-channel/run entries lack exact native SEEG geometry, all in `sub-33`; the affected channels are listed in the preceding [WSGZP metadata audit](WSGZP_METADATA_AUDIT_20261028.md). MRI, scalp geometry, native/MNI SEEG geometry, and paired run files are present for all participants, but presence alone does not validate geometry or preprocessing.

## Reproduction

From the project root, using the project's Python 3.12.14 virtual environment and pytest 9.1.1:

```powershell
\.venv\Scripts\python.exe -m pytest tests/test_wsgzp_metadata_audit.py -q
\.venv\Scripts\python.exe scripts/track_b/audit_wsgzp_extracted_metadata.py `
  --dataset-root "C:\Users\TRANAV\OneDrive\Desktop\TKS\wsgzp datset\extracted\ccepcoreg" `
  --output outputs/track_b/20261029_wsgzp_metadata_contract_audit/audit.json
```

The focused tests passed **7/7** after updating the coordinate-contract classifier and adding a regression test for the metadata-only validator fixture. The latest full project suite passed **180/180** tests, and the read-only gate-register validator passed with 296 evidence paths. Those checks verify software behavior and evidence paths, not geometry or signal-analysis validity.

### BIDS Validator run (metadata/structure only)

The official root BIDS tree was checked with `bids-validator@1.14.10` and `--ignoreNiftiHeaders`; it reported no errors or warnings, but its summary included only the 36-subject MRI tree because the validator does not recurse into derivatives by default. This is **not** a clean validation of the EEG/iEEG exports. A separate run on `derivatives/epochs` exited with errors: non-BIDS `*_epochs.*` filenames (including `.npy` arrays), invalid trailing-comma JSON in `dataset_description.json`, missing derivative `dataset_description.json` after parse failure, nonconforming `channels.tsv` `type` values, and subject-file consistency warnings. The command reported `dataProcessed: false`; no EEG/iEEG sample array was materialized by this audit.

Because the derivative descriptor is invalid, the direct derivative run did not surface the two coordinate-keyword fields. To isolate the check reproducibly without copying signal data, `scripts/track_b/validate_wsgzp_coordinate_metadata.py` creates a valid minimal metadata fixture from one participant's original `*_coordsystem.json` and `*_electrodes.tsv`. The pinned validator rejects both `T1w` fields. The metadata audit independently finds the same declarations for all 36 participants. This is a targeted schema check, not a substitute for validating or repairing the original derivative dataset. The official BIDS 1.6.0 specification remains the version-specific basis for the finding.

Commands used:

```powershell
npx --yes --package=bids-validator@1.14.10 bids-validator `
  "C:\Users\TRANAV\OneDrive\Desktop\TKS\wsgzp datset\extracted\ccepcoreg" `
  --ignoreNiftiHeaders --json
npx --yes --package=bids-validator@1.14.10 bids-validator `
  "C:\Users\TRANAV\OneDrive\Desktop\TKS\wsgzp datset\extracted\ccepcoreg\derivatives\epochs" `
  --ignoreNiftiHeaders --json
.venv\Scripts\python.exe scripts\track_b\validate_wsgzp_coordinate_metadata.py `
  --dataset-root "C:\Users\TRANAV\OneDrive\Desktop\TKS\wsgzp datset\extracted\ccepcoreg" `
  --participant sub-01 `
  --output-directory outputs\track_b\20261029_bids_validator\coordinate_metadata_reproduction_004
```

Machine-readable outputs are local under ignored `outputs/track_b/20261029_bids_validator/`. The coordinate-only runner copies 2 metadata files from sub-01, verifies rejection of both coordinate fields, and records the validator's detailed schema diagnostics; it does not copy or load neural samples. Use a fresh output directory on reruns because the script refuses to overwrite prior evidence. The manifest SHA-256 is `9ea15184846ad558607980074c82c305877ca78db5a47766d0da789c06ac1cdc`, validator JSON SHA-256 is `cc66d732ef292cb74a066d767068f29ae74642e8fc22347bed0583ad92b4690f`, and runner source SHA-256 is `07ca9fd0728ab6295b574bbff6f6741d23bc3fc23260c0121c73c5d6dc6abcdd`. The source dataset was not modified.

The full machine-readable report is written locally to the ignored `outputs/track_b/20261029_wsgzp_metadata_contract_audit/audit.json`. Its SHA-256 is `cde7d92f6e1ea820ca826a682f70e316c25e5c7a7321e4974093271a4bc032c3`. The metadata audit script SHA-256 is `18dfdb2dd8975d5008ac344dc6bef22b5d78ed5d33b9497600cdad9efc72eee6`.

## Consequence for the project

Do not fit source models on WSGZP or claim physiological source recovery based only on these exports. First obtain authoritative coordinate-frame/transform clarification and reviewed participant overlays, reconstruct the processing and scale semantics, and define a valid run-level endpoint without pretending it is trial-paired. If those conditions cannot be met, retain WSGZP as an audited but unusable source-recovery route and keep the project's validated software claim bounded to its existing evidence.
