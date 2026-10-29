# B8 exact-commit release candidate: 8c7e740

**Source commit:** `8c7e74001bb8a561def390e0b6645627765c15aa`  
**Package:** `observable-geometry 0.1.3.dev0`  
**Gate status:** B8 remains `IN_PROGRESS`; this is package and one-model numerical verification, not scientific validation.

## Verified evidence

- Commit-bound release runner: **211/211 workspace tests passed**; source archive: **209 passed, two documented skips, zero failures**.
- The Git source archive SHA-256 is `9e3593e474c1dec6d46c0bdb09c1b1cba39c3288a22d20687a6eb43182f59c34`.
- The wheel built from the extracted exact-commit archive passed all seven source/version/license checks for the staged source and 18 package modules.
- A fresh Python 3.12.14 environment with NumPy 2.5.4 and SciPy 1.18.1 installed the wheel. All ten installation, provenance, output-manifest and access-contract checks passed.
- Its installed CLI exactly reproduced the sealed sub-01 model-only reference: all **40,980 ranked pairs**, score arrays, and summary metrics matched. The run allowlist was limited to `leadfield`, `noise_covariance`, `coordinates_m`, and `source_ids`.
- The source-only snapshot manifest is refreshed to include this report and the updated gate records. The clean-tree snapshot verifier is recorded in `outputs/track_b/20261029T_current_quality_audit/source_snapshot_verification_current.json`; this snapshot excludes datasets and run outputs.

## Artifacts

- Source archive: `reviewer_handoff/B8_Independent_Review_20261024/observable_geometry_source_8c7e740.zip`
- Wheel: `outputs/track_b/20261029T_commit_release_8c7e740/wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl`
- Wheel SHA-256: `94a1cc802eea30e3fa6600dd847f609eee32fac9221fd5546a7826d10b273cb8`
- Workspace test report: `outputs/track_b/20261024_b8_release_checks/test_run_8c7e740.json`
- Source-archive test report: `outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_8c7e740.json`
- Wheel-source report: `outputs/track_b/20261029T_commit_release_8c7e740/wheel_source_verification.json`
- CLI parity report: `outputs/track_b/20261029T_commit_release_8c7e740/candidate_cli_parity.json`
- Installation report: `outputs/track_b/20261029T_commit_release_8c7e740/candidate_installation_verification.json`

## Limits and remaining gate conditions

This verifies reproducible package behavior for one sealed participant-specific forward model. It does **not** establish endogenous neural-source recovery, physiological validity, calibrated uncertainty, researcher decision benefit, population generalization, or a novel-method advantage. WSGZP MRI-to-electrode registration remains unverified. B8 remains open pending attributable unaffiliated review and a release-version decision; the broader scientific goal also requires geometry-supported measured-data validation and evidence of researcher value.
