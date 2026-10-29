# WSGZP public geometry-file inventory recheck

**Date:** 29 October 2026\
**Scope:** OSF JSON:API file/folder metadata only\
**Signal samples accessed:** no\
**Result:** no separately published candidate digitizer or registration files found

## Method

The read-only script recursively queried the public OSF storage listing for
node `wsgzp`. It followed folder metadata links and inspected names, paths,
sizes, and metadata hashes only. It did not request file-download URLs or
open the dataset archives. Candidate names included common digitizer and
transform formats (`.hpts`, `.elp`, `.sfp`, `.pos`, `.mrk`, `.h5`, `.hdf5`,
`.xfm`, `.mat`, `.fif`) and explicit registration/digitizer/fiducial terms.

## Result

The live listing returned nine entries: two folders and seven files. The
`data` folder contains five multipart ZIP segments and the matching ZIP
archive; `additional_info` contains only `eeg_badtrials.json`. The metadata
inventory contained **zero separate geometry candidates**. The participant
electrode TSVs, T1w MRIs, and coordinate sidecars are inside the already
downloaded BIDS release, but the OSF listing exposes no additional source
digitizer points or registration transform/QC files.

This confirms the public storage layout, not the correctness of the BIDS
coordinates. Combined with the earlier extracted-tree filename scan, it
narrows the remaining geometry gap to unavailable source provenance or
curator confirmation. The EEG sidecars declare `T1w`/mm and the primary paper
reports digitization/coregistration, but the exact participant-level linkage
from digitizer files to released coordinates and reviewed registration QC is
still not independently established. Do not use this inventory as a geometry
pass or as permission to fit signals.

## Reproduction

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_public_geometry_inventory.py `
  --output outputs\track_b\20261029T_wsgzp_public_inventory_recheck_003\osf_inventory.json
```

The output records all three API-response SHA-256 values and the audit-script
SHA-256 (`0f47edfb58b77403f34437eee56141a2b500958ed97862019f90a8b4834c7e09`).
The saved JSON SHA-256 is
`72e8f26eed6261b8e598b9201109f495d5822fdfd6ee721ba208cd1bcf5c0b3e`.
The output is local under the ignored `outputs/` directory; do not cite it as
a public release artifact unless it is deliberately added to a review bundle.

Source endpoint: [OSF public file listing API](https://api.osf.io/v2/nodes/wsgzp/files/osfstorage/).
