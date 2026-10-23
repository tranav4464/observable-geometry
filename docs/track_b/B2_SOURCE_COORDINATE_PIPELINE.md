# B2 primary-source audit: electrode-coordinate pipeline

> **Historical WBEN/on004752 route audit, superseded 23 October 2026.** This atlas-coordinate investigation is not used by the active Localize-MI GBFs build. See `PROJECT_DEFINITION.md` and `GATE_REGISTER.json` for the active route.

**Status:** dataset-side pipeline recovered; direct lookup into MNI152NLin6Asym is invalid; exact WBEN Harvard–Oxford contact map remains unresolved.

## What the dataset authors’ code does

The pinned original repository revision `395ae136372be9772cdbeb09bccd677fda01b5d6` contains `Channel Localization/Main_4_Region_assignment_200226.m`. The script loads an ACPC-aligned subject MRI and electrode positions, then:

1. Calls FieldTrip `ft_volumenormalise` with `cfg.nonlinear = 'yes'` and `cfg.spmversion = 'spm12'`.
2. Applies the returned `individual2sn` warp to both electrode positions and channel positions.
3. Labels the transformed coordinates as `mni`.
4. Loads FieldTrip’s Brainnetome maximum-probability map `BNA_MPM_thr25_1.25mm.nii`, requests labels at the MNI coordinates, and chooses the label with the largest voxel count.

The script does not set a custom normalization template, `spmmethod`, or `templatecoordsys`. At FieldTrip 20200315, `ft_volumenormalise` defaults `spmmethod` to `old`, `templatecoordsys` to `spm`, and, for SPM12, selects `spm/toolbox/OldNorm/T1.nii`. SPM’s template documentation says this image derives from the linear ICBM152 T1 average, resampled to 2 mm and smoothed with an 8 mm Gaussian. Thus the original localization code provides a much stronger provenance trail than the released BIDS metadata alone.

## What this establishes, and what it does not

It establishes the method used by the authors’ published electrode-localization script to transform contact coordinates and assign Brainnetome labels. It supports interpreting the released coordinates as intended standard-space coordinates and the supplied anatomical labels as Brainnetome-derived. It does not independently prove that every coordinate row in NEMAR `on004752` was exported from this exact output file, because the script’s local input/output paths refer to individual subject files and no direct row-by-row export manifest was found.

It also does not recover WBEN’s exact Harvard–Oxford contact map. WBEN describes a 69-region state representation, nearest-neighbor aggregation of source locations in MNI, assignment of iEEG channels to HO regions by electrode positions, regional averaging, and a binary `C` selector. The paper does not state the exact HO atlas image/version/space convention used for electrode lookup, coordinate conversion, nearest-neighbor reference set, tie rule, distance limit, or out-of-atlas handling. The earlier lookup applied identity coordinates to an atlas in MNI152NLin6Asym despite source provenance indicating SPM12 OldNorm's linear ICBM152-derived space; it is therefore withdrawn, not merely provisional. WBEN’s `fsaverage` electrode co-registration may be used for a different geometry step; its role in the HO mapping must be traced before asserting equivalence or conflict.

## Consequence for the project

The earlier statement that the exact dataset-side normalization template was unknown is superseded: the original code and pinned FieldTrip defaults indicate the SPM12 OldNorm path. The active blocker is that the released BIDS coordinates do not identify this template in a sidecar, row-level identity with the source output is unproven, and the previous atlas lookup used no cross-template transform. Published tooling documents possible MNI152Lin-to-MNI152NLin6Asym deformation fields, but the inspected NiSpace interface resamples images; using its field for point coordinates requires auditing field direction, RAS convention, interpolation, and validation. That candidate does not resolve WBEN's own contact-assignment rules. Until both issues are resolved, do not use the old lookup or call a regional implementation faithful. B2 remains open; no model fitting on reserved outcomes is authorized.

## Primary sources

- Original localization code, pinned revision: https://github.com/vdimakopoulos/verbal_working_memory/blob/395ae136372be9772cdbeb09bccd677fda01b5d6/Channel%20Localization/Main_4_Region_assignment_200226.m
- FieldTrip 20200315 `ft_volumenormalise`: https://github.com/fieldtrip/fieldtrip/blob/20200315/ft_volumenormalise.m
- SPM template documentation: https://github.com/spm/spm/blob/main/spm_templates.md
- Dataset localization paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC6972902/
- WBEN paper: https://openreview.net/pdf/799e82c424dc3dcfa7cfcf45da2f0882ca3ef973.pdf
- Harvard–Oxford atlas documentation: https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html
- TemplateFlow documents Harvard–Oxford in MNI152NLin6Asym: https://github.com/templateflow/templateflow/releases
- NiSpace documents EasyReg-based inter-template image resampling and field conventions: https://nispace.readthedocs.io/en/latest/generated/nispace.transforms.mni_to_mni.html
- BIDS iEEG coordinate metadata: https://bids-specification.readthedocs.io/en/stable/modality-specific-files/intracranial-electroencephalography.html
