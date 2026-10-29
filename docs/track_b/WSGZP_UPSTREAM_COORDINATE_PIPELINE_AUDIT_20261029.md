# WSGZP upstream scalp-coordinate pipeline audit

**Date:** 29 October 2026\
**Evidence class:** public curation source and metadata only; no EEG/SEEG arrays read\
**Purpose:** determine exactly what the public BIDS curation code establishes about scalp-electrode coordinate provenance.

## Pinned source examined

The public repository is [`iTCf/ccepcoreg`](https://github.com/iTCf/ccepcoreg), checked at commit [`8721fc04328c00b131659915dfbfa569bd342b54`](https://github.com/iTCf/ccepcoreg/tree/8721fc04328c00b131659915dfbfa569bd342b54), committed 8 April 2026. The source-file SHA-256 values retrieved from that commit are:

| File | SHA-256 |
|---|---|
| `export_bids.py` | `D8807AFB62944102EC461E93F2004AC3FCB5BE3B5378BAD10BBD335248F6B2AE` |
| `fx_bids.py` | `0B5D3C817E939F3BC20C1E0C2C2C6E86EC42C317E3BC3A260388DC5823BF6EEF` |

## What the source code does

In `export_bids.py`, the exporter constructs a path to `{subj_name}_egi_dig.hpts` and passes that same file to `make_coordsys_eeg_json` and `make_electrodes_eeg_tsv` ([pinned exporter](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/export_bids.py#L53-L61)). In `fx_bids.py`, both helpers parse the file's `kind`, channel label, and `x/y/z` values directly. The coordinate-sidecar helper writes `EEGCoordinateSystem: T1w`, `EEGCoordinateUnits: mm`, and the LPA/NAS/RPA values read from that file. The electrode-table helper selects EEG rows and writes their `x/y/z` values, rounded to two decimals ([pinned sidecar helper](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L87-L107), [electrode export](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L134-L149)).

The helper `load_trans` also exists in `fx_bids.py`; it reads an HDF5 matrix and wraps it as an MNE `head`-to-`mri` transform ([pinned helper](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L329-L335)). The checked BIDS exporter does not call `load_trans` and contains no transform-application step. This establishes that the public exporter does not itself demonstrate how the source `.hpts` values were produced or transformed before export.

The same module's `load_bids` helper reads the BIDS-declared electrode coordinates and constructs an MNE montage with `coord_frame='head'`, while the sidecar labels those coordinates `T1w`; this path also does not call `load_trans` ([pinned loader](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L290-L335)). This is a coordinate-contract inconsistency in the example loader. We inspected its source only; we did not invoke it or materialize EEG arrays.

## Interpretation and limit

This code audit **does not prove that the released scalp coordinates are wrong**. The dataset paper reports that electrode positions were digitized with SofTaxicOptic and coregistered to the participant's pre-implant MRI. The `.hpts` values could already be in the MRI frame before the exporter reads them. The public repository does not document that upstream operation or link a transform file to the exported values, so the code alone cannot distinguish pre-transformed points from points whose frame was mislabeled.

The study-level MRI-registration method is reported, but the exact provenance of the released participant coordinates remains unresolved. Do not apply `load_trans` speculatively, fit a new transform and call it recovered provenance, or use the current points as independently verified ground truth. To clear the gate, obtain the raw digitizer data and saved transform or authoritative confirmation that the `.hpts` values are already in the anonymized T1w frame, plus reviewed participant overlays and registration QC. This is consistent with the existing acceptance checks in [`WSGZP_COORDINATE_PROVENANCE_REQUEST.md`](WSGZP_COORDINATE_PROVENANCE_REQUEST.md).

### Primary-method cross-check (29 October 2026)

The primary Parmigiani et al. dataset paper's Methods state that hd-EEG
electrode and anatomical-fiducial positions were digitized with a SofTaxicOptic
system and coregistered with a pre-implant 3D-T1 MRI. The earlier source paper
for this cohort describes the scalp-electrode/fiducial digitization against
pre-implant MRI and specifies an MRI-to-MRI ANTs transform when the EEG
digitization MRI differed from the pre-implant MRI. A later XDL-ESI analysis
of the same 36-participant dataset also reports that the scalp positions were
aligned to the pre-implant 3D-T1 MRI before it constructed a participant head
model. These sources make the intended MRI-space interpretation plausible and
show that MRI alignment was part of the study workflow; the question is not
whether the paper describes coregistration at all.

They still do not establish the exact linkage from each participant's
digitizer output and transform to the released `.hpts` and BIDS coordinates,
whether anonymization preserved the relevant world-coordinate mapping for
each individual file, or explain the `sub-32` anomaly. The BIDS sidecar and
exporter therefore have a plausible study-level basis, but participant-level
geometry remains unverified. Keep `sub-32` excluded and require independent
visual sensor-to-scalp QC for any participant used to build a forward model.
Do not invent a numeric coordinate-uncertainty radius: none of the inspected
sources supplies a per-participant registration-error bound. This update
narrows the provenance gap; it does not clear the WSGZP geometry gate or
support a novelty claim.

Sources: Parmigiani et al. (2022), [primary dataset paper, DOI
10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007);
Mikulan et al. (2020), [primary dataset paper, DOI
10.1038/s41597-020-0467-x](https://doi.org/10.1038/s41597-020-0467-x);
Jiao et al. (2024), [XDL-ESI, DOI
10.1016/j.neuroimage.2024.120802](https://doi.org/10.1016/j.neuroimage.2024.120802).

## Consequence for the novelty test

Without a cleared participant-specific sensor-to-MRI geometry, a measured-data difference cannot fairly be attributed to the proposed source-family report rather than registration error. Thus the held-out source-family/SEEG-contact decision test remains **not ready to run**. The finding narrows a provenance gap; it is not itself a novelty result. Even after the geometry gate closes, novelty still requires a preregistered decision advantage against GBF, direct constrained fitting, and matched resolution/patch baselines.

## Reproduction

This report records the commit and source hashes above. The repository tree lists only the exporter, helper module, README, and a getting-started notebook. The reviewed exporter calls the raw-digitizer helpers directly; repository search found no call to `load_trans` in the exporter or notebook. The sources inspected are linked at the pinned commit so that later changes to `main` do not alter the evidence.

## Local download re-scan (29 October 2026)

The complete local `wsgzp datset` directory, including the multipart download
and extracted BIDS tree, was re-scanned for `.hpts`, `.h5`, `.hdf5`, and `.mat`
files, and for filenames containing `transform`, `digitizer`, or
`registration`. The search returned **zero candidate geometry files**. This
confirms that the missing source points/transform are not merely stored under
an alternate filename in the downloaded package. It does not rule out a
separate public or custodian-held source archive. No signal arrays were read
in this filename-only check, and the coordinate gate remains open.

### Expanded user-workspace search (29 October 2026)

The filename search was expanded to the TKS workspace, Downloads, Documents,
and the user profile, looking for the source digitizer extensions (`.hpts`,
`.elp`, `.sfp`, `.pos`, `.mrk`), transform containers (`.h5`, `.hdf5`, `.xfm`)
and WSGZP/`ccepcoreg`/`egi_dig`/digitizer name matches. No additional
WSGZP-specific digitizer or transform artifact was found. The search did find
unrelated Localize-MI head-to-surface transform files and source-estimate
`.mat` outputs for ds004752; neither is a WSGZP scalp-to-T1w registration and
neither is substituted. The extracted WSGZP BIDS electrode tables, coordinate
sidecars and participant T1w MRIs are present, but they do not supply the
missing original registration record or participant-level QC. This search was
filename-only; no EEG/SEEG sample values were accessed.

### Live OSF public-inventory recheck (29 October 2026)

The public OSF JSON:API file inventory was re-queried recursively using
`scripts/track_b/audit_wsgzp_public_geometry_inventory.py`. It returned nine
entries (two folders and seven files): the five multipart archive segments,
the matching ZIP, and `eeg_badtrials.json`. No additional source digitizer or
registration/QC file was exposed in the public storage tree. The audit only
requested file/folder metadata; it did not request archive content. The
response hashes, script hash, and full metadata listing are recorded in
[`WSGZP_PUBLIC_GEOMETRY_INVENTORY_RECHECK_20261029.md`](WSGZP_PUBLIC_GEOMETRY_INVENTORY_RECHECK_20261029.md)
and the local ignored output referenced there. This confirms that no separate
public geometry file is currently listed, but it does not validate the
released T1w coordinate contract or close the participant-geometry gate.
