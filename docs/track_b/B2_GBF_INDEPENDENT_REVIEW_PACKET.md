# Independent technical review packet: GBFs B2

**Review status: NOT YET REVIEWED.** The authoring team prepared the active specification, but this packet does not constitute independent approval. B2 remains IN_PROGRESS, and downstream implementation/evaluation gates remain blocked until the required review is recorded.

**Review this frozen specification:** `B2-GBF-2026-10-23-v10`, SHA-256 `1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062`. The immutable review copy and checksum manifest are [`B2_GBF_SPEC_review_v10.md`](../../outputs/track_b/20261023T160054Z_b2_gbf_specification_v10/B2_GBF_SPEC_review_v10.md) and [`review_spec_manifest.json`](../../outputs/track_b/20261023T160054Z_b2_gbf_specification_v10/review_spec_manifest.json). Version 10 adds angle-based source-resolution prior art from Pascual-Marqui and Biscay-Lirio (1993) and conductivity-ensemble sensitivity prior art from Vorwerk et al. (2024); the v9 math, tolerances, and claim limits are retained. Earlier versions remain preserved; reviews must name the exact version and hash they assessed.

## Review question

Does the specification correctly define a transparent, useful, bounded tool for comparing nominal scalp signatures of spatially separated focal-source hypotheses under one verified Localize-MI participant-specific forward model, without overstating what the data or calculation establish?

## Read these active materials

1. [`B2_GBF_SPEC.md`](B2_GBF_SPEC.md): exact estimand, equations, input contract, output semantics, thresholds, comparator, failure cases, data boundary, and falsification rules.
2. [`PROJECT_DEFINITION.md`](PROJECT_DEFINITION.md): active project and claim scope.
3. [`GBF_BUILD_PLAN.md`](GBF_BUILD_PLAN.md): gate sequence and deliverable.
4. [`FOUNDATION_PROTOCOL.md`](../FOUNDATION_PROTOCOL.md): frozen Track A source family, covariance/reference choices, outputs, and limits.
5. [`nominal.py`](../../src/observable_geometry/nominal.py) and [`test_nominal.py`](../../tests/test_nominal.py): implementation and invariant coverage.
6. [`recompute_b2_gbf_cpu64.py`](../../scripts/track_b/recompute_b2_gbf_cpu64.py), SHA-256 `58dc22a654cfde5ae7cfd4372fdafb205b60a304ab5687b763d7233d237cec38`: standalone v10 verifier. Syntax/help, a combined 16-test regression, and a metadata-only access-boundary audit passed; see [`v10 validation record`](../../outputs/track_b/20261023T160133Z_b2_v10_verifier_boundary/SESSION.md). It does not import the production scoring implementation and statically references only the named `leadfield` and `noise_cov` keys from `prepared_bundle.npz`; it has not been run on real model arrays and has not recomputed the real score.
7. [`test_b2_independent_calculator.py`](../../tests/test_b2_independent_calculator.py), SHA-256 `9a4d172d55c400cb3d07a34d4e882b1f2951de4b81246d41392d5984cc753909`, and [`unit_test_run.json`](../../outputs/track_b/20261023T_b2_verifier_analytical_tests/unit_test_run.json): four small algebraic matrix tests passed. They are not simulated or recorded EEG and do not validate the real-data result.
8. [`code_contract_audit.json`](../../outputs/track_b/20261023T_b2_gbf_specification_v2/code_contract_audit.json): author-side static source-to-spec audit; not independent review or numerical validation.
9. [`unit_test_run.json`](../../outputs/track_b/20261023T_b2_gbf_unit_tests/unit_test_run.json): 8 existing algebraic invariant tests passed; not a real-data score recomputation or independent review.
10. [`unit_test_run.json`](../../outputs/track_b/20261023T_b2_gbf_covariance_scale/unit_test_run.json): 9 algebraic invariant tests passed, including scalar covariance-scale invariance; not real-data score validation or independent review.
11. [`case_audit.json`](../../outputs/track_b/20261023T_b1_gbf_case_audit/case_audit.json) and [`case_validation.json`](../../outputs/b1_gbf_case_validation_20261023/case_validation.json): real-case data and forward-model contract checks.
12. [`orientation_audit.json`](../../outputs/track_b/20261023T_b2_gbf_orientation_audit/orientation_audit.json): metadata-only verification of the raw and derived orientation contract.
13. [`run_manifest.json`](../../outputs/tracka_release_20261022_v2/run_manifest.json), [`mne_resolution_report.json`](../../outputs/tracka_release_20261022_v2/mne_resolution_report.json), and [`nominal_ambiguity_pairs.csv`](../../outputs/tracka_release_20261022_v2/nominal_ambiguity_pairs.csv): sealed implementation, comparator, and existing real-data outputs.
14. [`B0_GBF_EXTENSION_SCREEN.md`](B0_GBF_EXTENSION_SCREEN.md): closest prior art and no-novelty boundary.
15. [`safe regression run`](../../outputs/track_b/20261023T155321Z_b2_safe_regression/SESSION.md): 13 passing algebraic/implementation tests and a passing read-only gate validation. Its first pytest attempt failed collection because `PYTHONPATH` omitted `src`; the corrected rerun passed. This evidence is not external review or real-model validation.
16. [`access-boundary guard tests`](../../outputs/track_b/20261023T155842Z_b2_access_guard_tests/SESSION.md): 3 new AST tests show the metadata auditor recognizes allowed model keys, detects `data` as an unexpected key, and rejects dynamic keys; 16 tests pass in the combined regression run. Test SHA-256: `3e4b6d902e79027138ea47897431b94f12f02b3142712b013d0cd244d5b2b922`. These are source-boundary tests, not real-data validation.
17. [`v10 specification freeze and validation`](../../outputs/track_b/20261023T160054Z_b2_gbf_specification_v10/SESSION.md) and [`v10 verifier validation`](../../outputs/track_b/20261023T160133Z_b2_v10_verifier_boundary/SESSION.md): v10 adds two directly relevant prior-art sources; the unchanged score contract passes the stated code checks. The frozen v10 copy/hash supersedes v9 for review. No real model arrays were accessed and the v10 verifier has not recomputed the real score.

The repository also contains `scripts/track_b/validate_b2_math.py`, which tests a historical covariance-sensitivity/WBEN calculation. It is not a validator for this active GBFs specification and is not included as B2 evidence.
## Questions for the reviewer

- Are the source family, units, fixed orientation, reference, covariance scaling and rank handling internally consistent with the real case and code?
- Is the distinction between the GBFs geometric-basis inverse and the separate vertex-level forward-signature diagnostic clear enough? Does the software's stated use match that separation?
- Does the normalization and absolute cosine correctly express the stated amplitude- and polarity-invariant *nominal* comparison? Is the residual interpretation precise and appropriately limited?
- Is the 20 mm Euclidean exclusion stated clearly enough, and are the 0.95/0.99 values correctly bounded as descriptive display thresholds rather than inferential cutoffs?
- Are the ranked alternative locations a coherent output for the stated researcher use? Does that use claim more practical value than has been demonstrated?
- Is the relationship to MNE resolution-matrix/PSF/CTF, Kalogianni-style separability, and Scherg et al.'s normalized leadfield cross-correlation represented accurately? Does the specification distinguish their estimands without minimizing the mathematical overlap?
- Are any inputs, outcomes, or interpretations outside the verified one-participant pulse-artifact case implied by the specification?
- What equations, implementation checks, or limitations must change before the score is recomputed independently or a B3 reusable interface is implemented?
- Are the predeclared exact-match rules and numeric tolerances adequate for comparing the independent float64 calculation with the sealed Track A outputs?
- Is the separate float32 residual replay check appropriate given the square-root sensitivity as the cosine approaches one?
- Recommendation: **PASS / HOLD FOR CHANGES / FAIL OR PIVOT**. List blocking issues and the smallest defensible remedy.

## Required review response

The reviewer should name the exact spec version and SHA-256 reviewed, summarize scope, answer the questions above, list blocking and nonblocking findings, and state whether the reviewer is unaffiliated with the implementation. A same-chat self-review is not independent sign-off. Do not access new participant outcomes or run model fitting as part of this review.

## Primary sources

- Kalogianni et al. (2018), [Spatial resolution for EEG source reconstruction](https://doi.org/10.1016/j.jneumeth.2018.02.016).
- Hauk, Stenroos & Treder (2022), [Towards an objective evaluation of EEG/MEG source estimation methods](https://doi.org/10.1016/j.neuroimage.2022.119177).
- Scherg et al. (2022), [Relative Source Power](https://doi.org/10.1016/j.clinph.2021.10.005). Appendix A normalizes leadfield vectors and uses their cross-correlation matrix in a probe-plus-shield inverse, a close mathematical overlap with normalized column comparisons.
- Stenroos & Hauk (2009), [On Forward Model Uncertainty in EEG Source Localization](https://www2.imm.dtu.dk/pubdb/pubs/6017-full.html); Stenroos et al. (2010), [SOFOMORE](https://doi.org/10.1007/s11265-010-0527-0).
- Wan et al. (2008), [Electromagnetic source imaging: Backus–Gilbert resolution spread function-constrained and functional MRI-guided spatial filtering](https://pmc.ncbi.nlm.nih.gov/articles/PMC6871235/), DOI [10.1002/hbm.20424](https://doi.org/10.1002/hbm.20424). This is the source-ambiguity paper linked in the active prior-art discussion.
- Mikulan et al. (2020), [Localize-MI dataset](https://doi.org/10.1038/s41597-020-0467-x).
