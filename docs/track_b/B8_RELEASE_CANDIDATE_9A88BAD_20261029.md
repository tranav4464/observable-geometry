# B8 exact-commit release candidate: 9a88bad

**Source commit:** `9a88bad1b0f9ff48fced1d352d5e36d1c0de4c89`  
**Package:** `observable-geometry 0.1.3.dev0`  
**Gate status:** B8 remains `IN_PROGRESS`. This is software/package verification, not scientific validation.

## Verified evidence

- Commit-bound workspace suite: **211 passed, 0 skipped, 0 failed**.
- Extracted source archive: **209 passed, 2 documented skips, 0 failed**. The skips concern repository-only evidence checks and a dataset-dependent check because datasets are excluded from the archive.
- Source archive SHA-256: `8aad5783b9bf6041b330c51fd14d121be3bc5451fcfcaa91397e4c55246bd8ab`.
- Wheel SHA-256: `acbb91388bc20cb91727a0ea2a2c8b8be4b1bfb79fb0cc66885c95647c33427f`.
- Wheel provenance verification passed all 7 checks. All 18 packaged Python modules match the committed source.
- A fresh isolated install with Python 3.12.14, NumPy 2.5.4, and SciPy 1.18.1 passed installation and provenance checks.
- The installed CLI exactly reproduced all **40,980** ranked model-only source pairs, score arrays, and summary metrics. The replay accessed only `leadfield`, `noise_covariance`, `coordinates_m`, and `source_ids`; it did not access EEG/iEEG sample arrays.
- The original data-free 9a88 handoff archive had SHA-256 `f8d36cd9d10b848b0a9bed1a603d9528c65693704ca1b848315f0694b11bd9fe`. Its embedded project-scope page cited the preceding 8c7e740 candidate, so it has been superseded by a refreshed packet. The current archive path and SHA-256 are recorded in `B8_REVIEW_HANDOFF_9A88BAD_20261029.md`.

Detailed run evidence is in `outputs/track_b/20261029T_commit_release_9a88bad/SESSION.md` and the associated JSON reports. The prior 8c7e740 candidate is historical and superseded by this exact-HEAD candidate.

## Claim boundary

These checks establish reproducible package behavior against one sealed participant model. They do not establish endogenous neural-source recovery, WSGZP registration validity, calibrated localization uncertainty, researcher decision benefit, population generalization, or a novel-method advantage. B8 remains open pending a current, hash-verified independent-review handoff, unaffiliated outside review, and a release-version decision.
