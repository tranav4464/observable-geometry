# WSGZP scalp-surface verification: local tooling feasibility

**Date:** 29 October 2026  
**Status:** Feasibility check only; WSGZP registration remains unverified  
**Data inspected:** MRI file metadata and package/tool availability. No EEG/SEEG samples accessed.

## Question

Can the current Windows workspace run an established MRI head/scalp-surface workflow to make the released WSGZP electrode coordinates independently inspectable against each participant's anatomy?

## Local findings

- The extracted WSGZP tree contains participant T1w scans. The inspected sub-01 scan is a 256 × 256 × 256, 1 mm isotropic NIfTI with qform code 1 and sform code 0. Prior audits found no participant T2w scans, digitizer `.hpts` files, saved registration transforms, or supplied scalp meshes.
- The project Python environment can import MNE, nibabel, NumPy, and SciPy. It has no `charm`, `mri_watershed`, `mne_watershed_bem`, `mri_synthstrip`, or `recon-all` command. It has no PyTorch, MONAI, SimpleITK, scikit-image, VTK, or ANTsPy modules.
- The machine has approximately 3.43 GB free on C:. No other filesystem drive is mounted in this environment.

## Established workflow options

MNE's documented watershed path obtains the scalp surface from FreeSurfer's `mri_watershed` tool. The resulting outer-skin surface is intended for inspection of MRI/channel alignment. This dependency is not installed in the current environment ([MNE implementation documentation](https://mne.tools/stable/documentation/implementation.html)).

SimNIBS documents `charm` as a route to individualized head models from T1w MRI alone, while noting that a T1-only scan may produce less accurate skull segmentation than T1 plus T2. Its workflow includes visual inspection of the generated segmentation report ([SimNIBS head-model documentation](https://simnibs.github.io/simnibs/build/html/tutorial/head_meshing.html)). `charm` is not installed here. No installation or large model download was attempted because the only available filesystem has limited free space and the present task is to assess feasibility, not to alter the machine environment.

## Interpretation and decision

The installed environment cannot currently produce the documented participant scalp surface needed for the planned independent overlay review. The earlier threshold-based MRI proximity calculations remain exploratory triage; they are not a substitute for a scalp segmentation, registration provenance, or independent validation.

This is a tooling constraint, not evidence that WSGZP coordinates are wrong or that verification is impossible. A valid next attempt requires a machine or volume with enough space to run a documented head-segmentation workflow, followed by visual review of the segmentation and sensor/fiducial overlays. The review must use criteria fixed before inspecting candidate overlays and should include a second reviewer. Sub-32 additionally needs a full-coverage MRI or documented exclusion from whole-cap checks because the released scan is cropped.

Even a good overlay would establish anatomical plausibility under the released coordinate declaration, not recover the original historical transform. The original digitizer points, exact transform, or independent held-out registration points are still needed to validate that transform itself. Do not fit a participant-specific forward model or claim anatomical registration accuracy on the basis of this feasibility check.

## Reproducibility note

This check used read-only command discovery, Python module availability queries, disk-space inspection, and NIfTI header inspection for sub-01. It did not install software, modify dataset files, fit a coordinate transform, or read neural recordings.
