# B2 gate closeout — 24 October 2026

**Gate decision: PASS for the frozen B2 specification and registered pre-recomputation checks.** The scope is nominal pairwise source-signature distinguishability under the single verified Localize-MI forward model and covariance. This pass establishes numerical reproducibility for that calculation only. It does not validate physiological source recovery, empirical localization accuracy, calibrated uncertainty, robustness to alternate head models, population generalization, or a novel cosine/coherence method.

## Reviewed and executed artifacts

- Frozen spec `B2-GBF-2026-10-23-v10`, SHA-256 `1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062`.
- v11 independent CPU64 verifier, SHA-256 `0927f600bc4843319f96c2f8cdb0e64753861e926d665e55417a76855d17f57e`.
- The supplied independent review identifies reviewer Dr. Anurag Sinha, Caltech, BCI/ML expertise, declares independent human technical review, and explicitly approves only the registered parity recomputation. This is recorded in `outputs/track_b/20261023T_b2_review_remediation/reviewer_remediation_rereview_20261024.txt` and `authorization_record_20261024.json`.

**Review-record hash discrepancy:** the supplied review's printed v11 SHA-256 is malformed and not hexadecimal. The named verifier file itself was independently hashed locally and matches the valid v11 digest above. The review explicitly names the v11 file path and authorizes that registered v11 computation; the malformed digest is retained as a review-document transcription defect, not silently corrected in the original review text.

## Registered recomputation result

Run: `outputs/track_b/20261024T_b2_v11_cpu64_registered_run/independent_recompute_report.json`
Run ID: `20261023T190737Z_b2_v11_cpu64` (UTC; corresponds to 24 October in the project timezone).
Device/dtype: CPU / float64.
Run output hashes and access logs are recorded in the report and adjacent JSONL files.

All registered comparisons passed:

- Top-five candidate ranking: exact match.
- Valid-source mask: exact match.
- Eligible-candidate counts: exact match.
- Maximum absolute score difference from sealed float32 values: `2.980014734976777e-08`, within `1e-7`.
- Legacy float32 residual replay maximum difference: `0.0`, within `1e-7`.
- Whitened norms: `np.allclose` passed at `rtol=1e-8`, `atol=1e-15`; maximum absolute difference `8.106231689453125e-06` and maximum relative difference `3.922115315945256e-15`.
- Runtime access log records only allowed model and comparison arrays; no recorded EEG `data` key was accessed.

The supplemental [`near_tie_diagnostics.json`](../../outputs/track_b/20261024T_b2_v11_cpu64_registered_run/near_tie_diagnostics.json) reports the top-two score margin for all 8,196 source rows with at least two alternatives. There are zero exact ties. The minimum margin is `2.2802913273167746e-06`; median is `0.008113707490464361`. Margins are descriptive for this fixed model and covariance, not probabilities of source confusion.

## Scope and next gate

The remediation full suite records 98 passing tests, and the targeted parity/access/nominal tests pass 23/23. The supplied reviewer did not independently rerun all 98 tests or reproduce the provenance measurements from original source files; those limits remain explicit. The reviewer and access audits do not convert the one-case nominal diagnostic into source-localization validation.

B2 is recorded as **PASS** because the review explicitly approved the named v11 run and the registered checks passed. B3 may now begin: implement the reviewed GBFs reproduction and nominal distinguishability workflow in separate, versioned code, preserving Track A. B3 completion remains its own gate. B4–B8 remain unpassed and must retain their own evidence and review conditions; in particular, any broader evaluation requires its own feasible real-data design and a protocol lock before held-out outcomes are accessed.
