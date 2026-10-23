# B2 coordinate crosswalk: MNI152Lin to MNI152NLin6Asym

> **Historical WBEN/on004752 route audit, superseded 23 October 2026.** The candidate coordinate transform is not used in the active GBFs/Localize-MI tool. See `PROJECT_DEFINITION.md` and `GATE_REGISTER.json` for the active route.

**State:** candidate transform audited on development contact metadata. It resolves the template-space mismatch for a declared mapping variant, but it does not reproduce WBEN's unspecified contact-assignment rule or establish subject-specific anatomical accuracy.

## Why the direct lookup was withdrawn

The dataset authors' pinned localization script calls FieldTrip `ft_volumenormalise` with `spmversion='spm12'`, then applies the resulting `individual2sn` warp to electrode coordinates. FieldTrip 20200315 defaults this call to SPM12 OldNorm and `spm/toolbox/OldNorm/T1.nii`; SPM documents this template as derived from the linear ICBM152 T1 average. This supports **MNI152Lin** as the likely source template. The BIDS electrode tables call x/y/z “MNI coordinates” but omit `*_coordsystem.json`, and no export manifest proves row-for-row identity with the localization script output. Treat source-space identity as a well-supported inference, not verified metadata.

The previous audit sampled the Harvard–Oxford maximum-probability atlases in **MNI152NLin6Asym** using the coordinates unchanged. TemplateFlow records Harvard–Oxford in this nonlinear FSL space. The identity lookup is withdrawn; its 374/760 result is historical only.

## Audited cross-template transform

The candidate transformation is the EasyReg field pair distributed by [NiSpace-data](https://github.com/LeonDLotter/NiSpace-data), pinned at commit `8b3bb0e8ba47a8a2b7c42b801e23b6b7cecf5c26`. Its project documentation lists `MNI152Lin` as a source and `MNI152NLin6Asym` as a target, describes the fields as absolute RAS coordinates, and distinguishes the source-grid point-forward field from the target-grid image-resampling field. We linearly interpolated the source-grid `dir-backward_field` at the released contact positions to obtain target-space RAS-mm coordinates. The paired `dir-forward_field` was used to map those coordinates back for round-trip consistency.

The source repository declares CC BY-NC-SA 4.0. The transform files are kept under ignored local data; they are not bundled into the project. Any public release of the transform or transformed mapping must preserve attribution and be checked against the license's noncommercial/share-alike terms. The audit records both field SHA-256 hashes and the pinned source commit.

## Real metadata audit results

The reproducible script `scripts/track_b/audit_dev_ho_mapping_easyreg.py` reads only the released `*_electrodes.tsv` files for sub-01 through sub-03, the transform fields, and the Harvard–Oxford atlas. It does not read event rows, EEG/iEEG samples, or sub-04 through sub-15.

- All 760 development contacts fell inside the source transform field.
- The paired-field round-trip error had a 0.0077 mm median, 0.0496 mm 95th percentile, and 0.1394 mm maximum. This checks numerical field direction and interpolation consistency; it does **not** establish anatomical correctness of the warp.
- The transformed point-in-atlas variant assigned 366/760 contacts (48.2%) to a non-background cortical or named deep-gray/brainstem label. This is a candidate mapping count, not evidence that the labels are anatomically correct or that the method predicts anything.
- Of 352 contacts assigned by both the historical identity lookup and this transformed lookup, 320 retained the same label (90.9%). The exact three coarse labels shared across all three development participants remained Temporal Pole, Left Amygdala, and Right Hippocampus. The remaining label changes and assignment changes are preserved in the CSV.

These differences show that the prior identity assumption changed actual assignments. The transform provides a reproducible crosswalk for an explicitly named analysis variant. It does not provide individual MRI registration, correct postoperative shift, account for contact dimensions, or prove that the released points came from the exact source-script outputs.

## Relation to WBEN and B2 decision

WBEN describes a 69-region Harvard–Oxford state representation and position-based assignment/averaging of iEEG contacts, but its accessible methods do not specify the atlas image version, template conversion, target coordinates, tie handling, distance cutoff, or out-of-atlas policy. Therefore the transformed point lookup is **not** a faithful reproduction of WBEN's observation matrix. If the project uses it, the configuration must explicitly name this as a crosswalk variant and report sensitivity to alternative assignment rules. It cannot justify a “true anatomical” network claim.

B2 remains open. The space mismatch is now technically addressable for a candidate mapping, but the target task, contact/region inclusion rule, prior-art distinction, split, preprocessing, metrics, baselines, and contribution decision still need to be frozen. Do not open reserved participant outcomes before B5.

## Provenance

- Original localization script at pinned revision: [Main_4_Region_assignment_200226.m](https://github.com/vdimakopoulos/verbal_working_memory/blob/395ae136372be9772cdbeb09bccd677fda01b5d6/Channel%20Localization/Main_4_Region_assignment_200226.m)
- FieldTrip 20200315 normalization defaults: [`ft_volumenormalise.m`](https://github.com/fieldtrip/fieldtrip/blob/20200315/ft_volumenormalise.m)
- SPM OldNorm template provenance: [SPM template documentation](https://github.com/spm/spm/blob/main/spm_templates.md)
- Harvard–Oxford source-space documentation: [TemplateFlow release record](https://github.com/templateflow/templateflow/releases)
- Transform source, field convention, and license: [NiSpace-data pinned repository](https://github.com/LeonDLotter/NiSpace-data/tree/8b3bb0e8ba47a8a2b7c42b801e23b6b7cecf5c26) and [NiSpace transform documentation](https://nispace.readthedocs.io/en/latest/generated/nispace.transforms.mni_to_mni.html)
- Audit implementation and output: `scripts/track_b/audit_dev_ho_mapping_easyreg.py`; `outputs/track_b/20261024T_b2_easyreg_point_transform/`
