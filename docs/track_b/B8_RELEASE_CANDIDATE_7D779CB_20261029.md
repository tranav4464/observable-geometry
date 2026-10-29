# B8 release-candidate verification: 7d779cb

**Verification target:** `7d779cb2e6e47edcccfd6bf52eda63e6f626c730`  
**Package:** `observable-geometry 0.1.3.dev0`  
**Result:** Software/package checks PASS; formal B8 remains IN_PROGRESS.

This report supersedes the 9a88bad exact-commit report for the current repository snapshot. The 7d779cb changes after 9a88bad were documentation-only; this candidate nevertheless received a fresh commit-bound workspace/source-archive test run, rebuilt wheel, isolated installation, and model-only CLI replay.

## Verified checks

- Full workspace: **211 passed, 0 skipped, 0 failed** under Python 3.12.14.
- Git source archive: **209 passed, 2 documented skips, 0 failed**. The skips are the full-workspace evidence-path check and a WSGZP dataset-dependent check; neither is silently counted as passed.
- Source archive SHA-256: `ea48c7d305cf5f0b3b678c7b934d1e410d2b738ca7bb9165fd9a6fd968fda57e`.
- Rebuilt wheel SHA-256: `bb82a6ec86ed7fbb4536d012abcd1ef63d1388804e8593e07f7a2a14d370b54d`.
- Wheel/source verification: all seven checks passed, including all 18 packaged modules, current README/project metadata, and BSD-3-Clause license metadata.
- Fresh isolated installation: Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1. The installed modules match the wheel and the installed CLI implementation hash matches its run manifest.
- The installed CLI replay exactly matched the prior clean-wheel reference for **40,980** ranked pairs, all score arrays, and summary values. The bundle/export access manifests confirm that only the approved model arrays were read; no EEG/iEEG sample arrays were accessed.
- The full-workspace gate validator passed with **385 evidence paths checked**. The working tree was clean at the tested source commit.

Machine-readable records are local under `outputs/track_b/20261024_b8_release_checks/` and `outputs/track_b/20261024_b8_source_archive_tests/` for commit `7d779cb`, and `outputs/track_b/20261029T_commit_release_7d779cb/`. The raw 0.1.3.dev0 wheel and local model-derived run outputs are not published in the repository.

## Interpretation and limits

These checks establish software behavior, package provenance, and numerical parity for one sealed participant model. They do **not** establish endogenous source recovery, valid WSGZP MRI-to-electrode registration, calibrated localization uncertainty, improved researcher decisions, population generalization, clinical utility, or a novel method. The two outreach reviews provided useful document-level feedback but did not reproduce or witness the clean installation and model replay required by the B8 outside-check criterion.

Therefore B8 remains `IN_PROGRESS`. Closing the software-release gate still requires an attributable independent reviewer to assess the current hash-identified candidate and its evidence, plus a recorded release-version decision. No review or signature is imputed to either outreach reviewer.
