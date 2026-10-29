# WSGZP independent-registration feasibility check

**Date:** 29 October 2026
**Scope:** Local geometry files and available software only; no EEG/SEEG samples accessed.

## Evidence inspected

The extracted WSGZP BIDS tree contains participant T1w MRIs, scalp-electrode TSVs and coordinate sidecars. The local filename search found no WSGZP digitizer-point files (`.hpts`, `.elp`, `.sfp`, `.pos`, `.mrk`), saved registration transforms (`.h5`, `.hdf5`, `.xfm`), or derived surface meshes (`.surf`, `.gii`, `.stl`, `.vtk`, `.ply`). Earlier public-inventory and curation-repository checks also found no additional WSGZP geometry files; see `WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md`.

The active Python environment has MNE 1.13.2, nibabel 5.4.2, and SciPy 1.18.1. No `recon-all`, `mri_watershed`, `mri_synthstrip`, ANTs `antsRegistration`, FSL `flirt`, SimpleITK, scikit-image, or VTK installation was found in the checked environment. Thus, the current workspace has no ready participant-specific scalp-surface segmentation pipeline or supplied surface to use for an independently reviewed re-registration.

## Decision

An independent registration is **not currently executable to publication-grade QC** from the local files and installed tools alone. A point-cloud fit to the released electrodes or a generic cap template would be a newly estimated alignment, not recovery or validation of the historical digitizer-to-MRI transform. Three fiducials can define a rigid transform, but their residual after fitting is not an independent accuracy check. Additional held-out head-shape points or landmarks, a sufficiently complete MRI scalp surface, and independent overlay review are needed to assess it.

The next valid route is to obtain the original digitizer points/transform and registration QC from the dataset curator. If those are unavailable, a separately named independent reconstruction can be considered only after a participant-specific surface pipeline and independent validation points are available. Sub-32's MRI omits part of the superior head, so it cannot validate the whole cap through an MRI-surface fit without a full-coverage image. The direct-qform field-of-view counts in `WSGZP_COORDINATE_COMPATIBILITY_SCREEN_20261029.md` remain triage evidence only.

## Reproducibility

This check was performed with read-only file inventory and Python import/command availability queries. It did not install tools, change MRI data, fit a transform, or read neural recordings. The geometry provenance request and conditional reconstruction acceptance checks are in `WSGZP_COORDINATE_PROVENANCE_REQUEST.md`.
