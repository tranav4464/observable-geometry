# B2 independent-review remediation and recheck request

> **Status update, 24 October 2026:** The supplied independent human review approved the named v11 registered recomputation, which passed. See [`B2_GATE_CLOSEOUT_20261024.md`](B2_GATE_CLOSEOUT_20261024.md). This remediation record below preserves the pre-run state and remains historical evidence of the HOLD response and fixes.

## Decision and scope

The reviewer recommended retaining the GBF-based nominal source-distinguishability route, while blocking the next real-array recomputation until four conditions are addressed: harden the parity checker, provide auditable forward-model provenance, enforce the signal-access boundary at runtime and preserve the access incident, then obtain independent gate approval before recomputing the registered real artifacts.

The first three conditions have been addressed in versioned remediation artifacts and tested. The missing prior-art discussion identified by the reviewer has also been added with the overlap stated conservatively. The fourth condition is intentionally still open: no registered CPU64 recomputation against the sealed Track A arrays was run. The reviewer explicitly conditions that action on independent gate approval. The supplied review is not signed by an unaffiliated human EEG/MEG methods expert, so it cannot by itself serve as that external approval.

No model fitting was performed. No claim of physiological source recovery, empirical discrimination probability, robust localization, or methodological novelty is made.

## Frozen artifacts and new implementation

The v10 mathematical specification remains byte-identical: `docs/track_b/B2_GBF_SPEC.md`, SHA-256 `1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062`. The original v10 verifier remains unchanged: `scripts/track_b/recompute_b2_gbf_cpu64.py`, SHA-256 `58dc22a654cfde5ae7cfd4372fdafb205b60a304ab5687b763d7233d237cec38`. Sealed Track A outputs were not edited.

The hardened verifier is a separate v11 file: `scripts/track_b/recompute_b2_gbf_cpu64_v11.py`, SHA-256 `0927f600bc4843319f96c2f8cdb0e64753861e926d665e55417a76855d17f57e`. It retains independent computation and uses runtime key allowlists for the two NPZ archives. Every requested key is appended and fsynced to the access log before access; an unapproved key is denied before NumPy materializes the member. The guard is a Python process-level control, not an OS sandbox or tamper-proof audit system.

### Parity-checker correction

`compare_sealed()` now checks:

- shape and stored dtype contracts;
- exact candidate indices, validity mask, counts, and ranking;
- source-index domain and invalid-source sentinel rules;
- expected populated slots and NaN-only unused slots;
- identical finite-value masks for calculated and sealed scores/residuals, so a missing or extra nonfinite value cannot disappear from comparison;
- finite score/residual ranges and finite, nonnegative norm values; and
- the preregistered numeric tolerances.

`tests/test_b2_verifier_hardening.py` adds ten focused regressions, including the reviewer's false-pass counterexample and malformed, missing, nonfinite, and misaligned values. These complement, rather than replace, the existing independent calculator and nominal implementation tests.

### Head-model provenance

The machine-readable audit is `outputs/track_b/20261023T_b2_review_remediation/provenance_audit_final/provenance_audit.json` (SHA-256 `7f2a8a961615df82b913969aa51690ba900b8a8a141caa26ca57746a35533de3`). It records source and artifact hashes, MNE forward conversion arguments, channel identity/order, electrode correspondence, coordinate frame and units, fixed orientation, common-average projection, covariance symmetry and supported eigenspace, and agreement of the prepared leadfield/covariance with their forward/reference construction.

Key results: 236 retained channels; 8,196 fixed-orientation source vertices; exact source-coordinate correspondence; maximum electrode-position discrepancy 0.0082 mm; leadfield reference-projection relative error `3.77e-16`; covariance reference-projection relative error `5.67e-16`; covariance symmetry relative error `1.11e-15`; and supported covariance rank 235/236, consistent with average reference. The audit read model arrays and metadata only, not EEG trial samples or the recorded `data` member. It also embeds and hashes the `_psd_eigh` implementation. This is reproducible provenance evidence, not independent external sign-off.

### Runtime access boundary and incident disclosure

The source/runtime boundary audit is `outputs/track_b/20261023T_b2_review_remediation/access_boundary_audit_final.json` (SHA-256 `80402edec414b35c9af894681d9997316ce6bc41f3efa4b12877eb4517aad6`). It confirms that the verifier has literal prepared-bundle allowlist entries `leadfield` and `noise_cov`, and that a synthetic archive's `data` key is denied before the NumPy member read. The recorded dummy log shows successful access to the two allowed keys and denial of `data`. Neither the dummy test nor the provenance audit opened project EEG samples through the guarded route.

Incident disclosure, retained as a separate process append-only record at `outputs/track_b/20261023T_b2_review_remediation/incident_disclosure.jsonl`:

> During earlier metadata inspection, the sealed `prepared_bundle.npz` was opened with `allow_pickle=False` and its `data` member was indexed. NumPy decompressed a 236 × 2,081 float64 EEG array into memory. The values were not printed, plotted, filtered, summarized, or used in calculations. This was signal-array access and must not be described as “no signal access.” This account is based on the operator's recorded disclosure; no complete OS-level execution trace exists to independently prove subsequent non-use. The reviewer judged the disclosed event alone insufficient to require discarding the development case or pivoting. The new guarded path prevents the same accidental member read through its wrapper and emits key-access events, but is not a system-wide sandbox.

The JSONL is append-only by the audit procedure (append mode plus fsync); it is not cryptographically immutable, write-once storage. Preserve the original file and append any later correction as a new line rather than rewriting the disclosure.

## Prior-art correction

`docs/track_b/METHOD_MATRIX.md` now includes Babadi et al. (2014), which explicitly defines mutual coherence for normalized measurement/leadfield columns and uses a coherence constraint in a subspace-pursuit MEG inverse method. This is a close conceptual and mathematical precedent. Accordingly, the B2 cosine/coherence quantity itself is not novel. The bounded distinction is that B2 computes covariance-whitened pairwise forward-pattern similarity for a fixed model and reports nominal ambiguity; it does not use coherence to select a sparse inverse support. This difference in use does not establish a new method.

The matrix also adds Phillips et al. (2026), a broad EEG source-inference review, as contextual prior art about forward/inverse modeling and limits. It is not an identical algorithm or empirical comparator. The separate Phillips et al. (2025) scalp/sEEG information-theoretic paper remains in the matrix with task-level overlap unresolved from the accessible full methods. The existing Hauk et al. (2022) and Scherg et al. (2022) entries remain and their overlap is stated explicitly. Primary-source links are in the matrix.

## Verification completed

- Full repository tests: `PYTHONPATH=src .venv\Scripts\python.exe -m pytest -q` — **98 passed**. Running pytest without `PYTHONPATH=src` fails import collection for the local package; that is an environment invocation issue, and the documented invocation passes.
- Provenance audit: **PASS**, model arrays and metadata only; no EEG sample read during that audit.
- Runtime access audit: **PASS**, including synthetic `data`-member denial before member read.
- Targeted parity/access/independent calculator/nominal tests: **26 passed** as part of the full 98-test suite.
- Frozen v10 specification and verifier hashes checked; both remain unchanged.
- No registered real-array recomputation, model fit, or alteration of sealed Track A outputs was performed.

These results establish that the corrected verifier passes its regression suite and the cited provenance/access assertions are reproducible. They do not establish that the sealed Track A real outputs pass an independent v11 recomputation.

## Required independent re-review

Please provide this record and the linked v11 verifier, regression tests, audit JSON, incident disclosure, frozen v10 specification, and original review packet to an unaffiliated technical reviewer. Ask the reviewer to:

1. Inspect the finite-mask/sentinel/dtype comparator changes and independently run the negative regression tests.
2. Check the provenance audit's source hashes and reconstruction claims against the referenced forward, channel, electrode, covariance, and Track A artifacts.
3. Inspect the runtime guard and dummy denial test, and confirm the incident disclosure is complete enough for the intended governance process.
4. Reassess prior art, especially Babadi et al. (2014), Scherg et al. (2022), Hauk et al. (2022), and Phillips et al. (2026), without treating the cosine/coherence score itself as novel.
5. Record an explicit PASS/HOLD/FAIL recommendation for the frozen v10 estimand and authorize or decline the next registered CPU64 recomputation. The reviewer must identify the exact spec and code hashes reviewed and disclose independence.

Only after that independent gate approval should the v11 verifier be run on the sealed real model arrays with a fresh unique run ID and output directory. Its immutable report must include exact index/validity/count agreement, score and norm tolerances, residual replay, near-tie diagnostics, input/output hashes, and the access log. A failure must be recorded, not repaired by altering frozen v10 or sealed Track A outputs.

## Sources

- Babadi et al. (2014), [A Subspace Pursuit-based Iterative Greedy Hierarchical solution to the neuromagnetic inverse problem](https://doi.org/10.1016/j.neuroimage.2013.09.008), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3946905/).
- Phillips et al. (2026), [Inferring neural sources from electroencephalography: foundations and frontiers](https://doi.org/10.1088/1741-2552/ae3e16).
- Hauk, Stenroos & Treder (2022), [Towards an objective evaluation of EEG/MEG source estimation methods](https://doi.org/10.1016/j.neuroimage.2022.119177).
- Scherg et al. (2022), [Relative Source Power](https://doi.org/10.1016/j.clinph.2021.10.005).
