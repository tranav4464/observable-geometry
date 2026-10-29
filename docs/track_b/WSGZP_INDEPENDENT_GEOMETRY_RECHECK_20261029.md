# WSGZP independent geometry recheck

**Date:** 29 October 2026  
**Scope:** released scalp-electrode coordinates and T1w MRIs only. No EEG/SEEG recording samples were opened.

## Result

I independently re-read the released coordinate tables and participant MRIs for all 36 participants. The check mapped the declared millimetre coordinates into each MRI's NIfTI qform world frame, counted points inside the image field of view, checked the fiducial orientation, and measured distance to nonzero MRI voxels at full image resolution. It also produced an orthogonal MRI overlay for sub-25.

- 36 participants and 6,660 scalp-electrode points were processed.
- 57 points fell outside the MRI field of view, across sub-05, sub-07, sub-10, sub-16, sub-21, sub-29, sub-32, and sub-33. Sub-32 has 29 out-of-field points and a cropped MRI.
- The median, across participants, of each participant's median distance to a nonzero MRI voxel was 10.07 mm. This is a crude proximity statistic, **not** a distance to a segmented scalp surface. Some cap sensors may also sit outside the skin surface.
- The inspected MRIs use qform code 1 and sform code 0, so there is no second NIfTI transform in these files to cross-check the assumed world frame against.
- The sub-25 slice overlay is consistent with the points lying around the head boundary in several views, but it is a selected-slice sanity check, not a complete 3D scalp-surface review or an independently reviewed registration.

I then built a second, explicitly approximate outer-head envelope at full resolution: for each MRI, I thresholded intensities at `>1`, `>10`, and `>40`, retained the largest connected component, filled enclosed holes, and measured each in-field electrode's distance to the nearest boundary voxel. This is a reproducible surface-proximity sensitivity screen, not a validated scalp segmentation; boundary-voxel distances also have approximately voxel-scale discretization error.

- The median of participant-level median distances was 10.12 mm, 10.17 mm, and 10.61 mm at the three cutoffs, respectively. Across all in-field points, the median was 9.96–10.40 mm and the 90th percentile was 16.42–16.85 mm.
- The cohort aggregate changes little with threshold, but participant-specific results are not uniformly stable: sub-25's median shifted by 5.34 mm and sub-34's by 2.69 mm between cutoffs `>1` and `>40`. Therefore the cohort-level stability cannot be used to certify each participant.
- At cutoff `>10`, the median distances were largest for sub-32 (38.39 mm) and sub-22 (16.19 mm). The NAS fiducial for sub-32 was 17.4 mm from this approximate envelope, versus 0.5 mm for each ear fiducial; the cropped scan is not adequate for whole-cap QC.

The threshold-screen details are in the local, ignored artifact `outputs/track_b/20261029_independent_wsgzp_geometry_check_001/outer_envelope_screen.json`, SHA-256 `F3958EF9772E65F82D80E9AAC33B529A6CF509E1B96B01EC65D5E185A52F7722`. This participant-level QC file and the MRI overlay are intentionally not included in GitHub. The aggregate results and hashes are recorded here. No universal pass/fail tolerance was found in the sources reviewed, so none was invented.

The first machine-readable result is the local, ignored artifact `outputs/track_b/20261029_independent_wsgzp_geometry_check_001/geometry_check.json`, SHA-256 `1EA96031938D5F8F6DA55C23D47B929144C16CB35DD74D3FB5DC6039F5D83F5B`. The illustrative local overlay is `outputs/track_b/20261029_independent_wsgzp_geometry_check_001/sub25_orthogonal_overlay.png`, SHA-256 `A2DF76042995679F4109776922B455E396A9459056A8FCA4B1A8EAAD89642214`.

## What the literature establishes

Parmigiani et al. report that scalp-electrode positions and anatomical fiducials were digitized with SofTaxicOptic and coregistered with each participant's pre-implant 3D T1 MRI. Thus the study paper supports that registration was part of the acquisition workflow. The public curation code then exports coordinates from its `.hpts` input directly into the BIDS electrode table and labels them `T1w`; the inspected exporter does not show which upstream transform produced those `.hpts` values. The dataset archive and public file inventory inspected so far do not include the original digitizer files, the participant-specific transform, or registration QC.

BIDS expects the coordinate sidecar to define the electrode coordinate system and units; its example explicitly describes axis direction and origin. The released sidecar's `T1w` label does not spell out axis directions or origin, and its `IntendedFor` names `sub-XX_T1.nii` while the released scan is `sub-XX_T1w.nii`. MNE's established coregistration workflow uses MRI skin-surface distances and visual inspection of sensor/head-shape alignment. Those are stronger checks than being inside the MRI volume or near nonzero voxels.

## Decision

**Independent check: partial plausibility support; registration remains unverified.** The evidence does not show that the released points are wrong. It also does not authenticate their participant-specific transform or quantify registration error. Do not use this check alone to approve source-localization results or treat SEEG contacts as validated spatial ground truth. Keep sub-32 out of whole-cap geometry analysis unless its MRI coverage is resolved.

The next practical verification is a documented MRI scalp segmentation, a full 3D overlay of all 185 sensors and fiducials for each candidate participant, sensor-to-surface residuals under a tolerance justified by the acquisition method, and review by a second person. Separately, obtain the original `.hpts` files, exact transforms and QC, or written confirmation that released coordinates are already in the anonymized T1w frame. If reconstructing a new alignment, label it as a new independent registration, not recovery of the original transform.

## Reproducibility notes

The check used the extracted `ccepcoreg` dataset at `C:\Users\TRANAV\OneDrive\Desktop\TKS\wsgzp datset\extracted\ccepcoreg`, the workspace `.venv` Python environment with NiBabel and SciPy, and a fresh output directory. The full-resolution proximity check thresholded MRI voxels at intensity greater than zero solely to ask whether coordinates are near recorded head tissue; it did not segment skin. The image overlay interprets released XYZ as the MRI's qform world coordinates and labels that as a hypothesis.

## Sources

- Parmigiani et al. (2022), [primary dataset paper, *Brain Stimulation*](https://doi.org/10.1016/j.brs.2022.04.007): reports digitization of scalp electrodes/fiducials and coregistration with pre-implant MRI.
- Mikulan et al. (2020), [simultaneous intracerebral stimulation and hd-EEG dataset paper, *Scientific Data*](https://doi.org/10.1038/s41597-020-0467-x): describes the predecessor dataset and its MRI/source-localization resources.
- [Pinned ccepcoreg BIDS exporter](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/export_bids.py#L53-L61) and [coordinate-writing helpers](https://github.com/iTCf/ccepcoreg/blob/8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L87-L107): evidence for how the released BIDS coordinates are written.
- [BIDS EEG coordinate specification v1.6](https://bids-specification.readthedocs.io/en/v1.6.0/04-modality-specific-files/03-electroencephalography.html): defines the role of coordinate-system and unit metadata.
- [MNE MRI/head coregistration documentation](https://mne.tools/stable/generated/mne.coreg.Coregistration.html): documents fiducial fitting, head-shape fitting and MRI skin-surface distances.
