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

### Complete public curation-repository history check (29 October 2026)

To check whether the missing geometry was removed from the current branch, the
public `iTCf/ccepcoreg` repository was cloned with its complete reachable
history. The seven reachable commits are `ba84ce6aa5ae80f0ff97b6309c7fb9e56391d106`,
`7fb9cb502d33807022129310e9edfae4e43e911e`,
`0fe8f75f252ce5dd8f3cdae435f32f3fc628d1f6`,
`10f4ef1b343ee4800bfcaafc8e6980140a0e525a`,
`6da4eb9d54f888c7ea54eed2e24d2559ba1c06ab`,
`9d7ffe240c2064d40e95fc1b48110e301a3aa164`, and the already audited
`8721fc04328c00b131659915dfbfa569bd342b54`. No reachable commit contains a
digitizer, fiducial, transform, or registration/QC data file. The earlier
`load_trans` helper is present in `fx_bids.py`, but none of the three historical
versions of `export_bids.py` calls it. The exporter reads
`{subj_name}_egi_dig.hpts` and passes its coordinates to the BIDS writers;
this history check therefore does not recover the upstream transform or
prove the exported points' coordinate frame. This closes the repository-history
search only; it does not close participant geometry or justify source fitting.

Reproduce the history inventory without downloading dataset contents:

```powershell
git clone https://github.com/iTCf/ccepcoreg.git tmp/ccepcoreg_upstream_history_20261029
git -C tmp/ccepcoreg_upstream_history_20261029 log --all --format="%H %s"
git -C tmp/ccepcoreg_upstream_history_20261029 log --all --name-only --pretty=format:
git -C tmp/ccepcoreg_upstream_history_20261029 log --all -G "load_trans\\(" -- export_bids.py
```

### Author-provided viewer check

The related [iTCf/CoregView](https://github.com/iTCf/coregview) repository was
also inspected at commit `f5cc77239d48f95f321bd24e90800fc1dd500350` as a
possible independent visual-QC route. `coregview_main.py` (SHA-256
`8088d4d3d3ac2b782ec1e64e9eaa68bc294a79aecda3b3934062fd1a4158bc6c`) loads
MNE's `EGI256` layout and a template `info-epo.fif`; the source explicitly
marks subject-specific digitizer loading as a TODO. `coregview_info.py` (SHA-256
`78c6dfa231888211900d35eb27cc5433c0defa08d294039961899b7436a1d91e`) points
to a separate EBRAINS dataset path. CoregView may visualize data after
registration, but this inspected version does not independently validate the
released WSGZP participant coordinates or recover their missing transform.
This is a software-capability finding, not a geometry result.

### EBRAINS public Knowledge Graph route recheck (29 October 2026)

Because the dataset paper also points to EBRAINS, the public EBRAINS dataset
connector was checked as a separate metadata-only route. The official
`FZJ-INM1-BDA/siibra-python` source was cloned at commit
`970e6128a2e0aadfc36705462f4298b9d50cc128`. In that snapshot,
`EbrainsPublicDatasetConnector` queries the released dataset record by its
dataset ID and reads the version's file listing. Its request implementation
always attaches a bearer token (`EbrainsRequest.auth_headers`). The inspected
source hashes are `321423089803E1AFB4E64C7F4CE339AABD16174F3A4737E8FA35F4D716B79D8F`
for `siibra/retrieval/repositories.py` and
`C02D3A2B6F9CB13A59985E335D28593B3630C5DC9BE8425CA8A7321456655A32` for
`siibra/retrieval/requests.py`.

A direct unauthenticated GET to the connector's documented released-dataset
query for record `b1c3e79e-ca4a-4a05-9235-b93cf1cb678d` returned HTTP 401. No
EBRAINS token was available in the process environment, and no login flow or
credential request was initiated. Thus the EBRAINS file listing was **not
retrieved**. This result is not evidence that the EBRAINS record lacks geometry
files; it establishes that an authenticated EBRAINS account is required to
inspect that route from this environment. The anonymous OSF listing remains
the only retrieved public file inventory, and the WSGZP geometry gate remains
open. No archive or neural signal data were downloaded or accessed in this
check.

Reproduction basis: the connector implementation is in the pinned
[`siibra-python` repository](https://github.com/FZJ-INM1-BDA/siibra-python/tree/970e6128a2e0aadfc36705462f4298b9d50cc128/siibra/retrieval).
The route template in that source is
`https://core.kg.ebrains.eu/v3-beta/queries/bebbe365-a0d6-41ea-9ff8-2554c15f70b7/instances?stage=RELEASED&dataset_id={dataset_id}`.
