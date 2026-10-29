# B8 commit-bound recheck: 0d54fe0

**Source commit:** `0d54fe09b5ee08c8ffefb72197f737e99987c585`
**Date:** 29 October 2026
**Outcome:** source manifest and software release checks pass; B8 remains open.

## Reproduced checks

- `verify_source_snapshot.py` passed on the clean commit. It verified 302
  source-only files against `SOURCE_SNAPSHOT_MANIFEST.json`; the report records
  the Git tree and manifest hash.
- `run_b8_release_tests.py` passed on the same clean commit: **181/181**
  workspace tests, with no skips or failures.
- The extracted Git source archive passed **179/181** tests, with two
  documented skips and no failures. The skips cover the repository evidence
  gate test, because those local outputs are excluded from the archive, and a
  WSGZP dataset-dependent audit, because the dataset is excluded.
- The archive imported `observable_geometry` from its extracted `src/` tree.
  Archive SHA-256:
  `d329741b0a4fd0f32061b16d2c89d3139e94c744fa2f704df246b1e7065da91c`.

Machine-readable records:

- `outputs/track_b/20261024_b8_release_checks/source_snapshot_verification_0d54fe0.json`
- `outputs/track_b/20261024_b8_release_checks/test_run_0d54fe0.json`
- `outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_0d54fe0.json`
- `reviewer_handoff/B8_Independent_Review_20261024/observable_geometry_source_0d54fe0.zip`

The output folders and reviewer handoff are local, ignored artifacts; the
commands and exact commit are recorded here so the checks can be repeated.

## What this does and does not establish

The recheck establishes a clean, hash-verified source snapshot and passing
software tests for this commit. It does not establish that the tool recovers
endogenous neural sources, changes a researcher decision beyond direct fitting
or existing methods, or supports a novel-method claim. The development wheel
parity remains tied to commit `1e83192`; package source and project metadata
were unchanged between that commit and `0d54fe0`, but this recheck did not build
or independently install a new wheel.

B8 remains open pending a current candidate handoff, a fresh wheel check if a
release candidate is required, and an attributable independent external
review/reproduction. B4–B7 remain pivoted. The WSGZP participant geometry,
preprocessing and trial-pairing issues still prevent valid held-out source
recovery claims; the current scientific result remains bounded model and
software evidence with novelty unproven.
