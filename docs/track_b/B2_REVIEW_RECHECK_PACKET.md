# B2 remediation recheck packet

> **Superseded 24 October 2026:** The submitted reviewer decision authorized the registered computation, and that run passed. See [`B2_GATE_CLOSEOUT_20261024.md`](B2_GATE_CLOSEOUT_20261024.md). This packet is retained as the pre-run re-review request and evidence index.

The original review found a verifier false-pass, incomplete provenance evidence, and no enforced runtime access boundary. Those were blocking findings. This packet presents the corrected artifacts for a fresh, independent decision on the frozen B2 specification.

## Review against

- Frozen estimand: [`B2_GBF_SPEC.md`](B2_GBF_SPEC.md), spec `B2-GBF-2026-10-23-v10`, SHA-256 `1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062`.
- Original verifier, preserved unchanged: [`recompute_b2_gbf_cpu64.py`](../../scripts/track_b/recompute_b2_gbf_cpu64.py), SHA-256 `58dc22a654cfde5ae7cfd4372fdafb205b60a304ab5687b763d7233d237cec38`.
- Corrected independent verifier: [`recompute_b2_gbf_cpu64_v11.py`](../../scripts/track_b/recompute_b2_gbf_cpu64_v11.py), SHA-256 `0927f600bc4843319f96c2f8cdb0e64753861e926d665e55417a76855d17f57e`.
- Detailed disposition and exact remediation: [`B2_REVIEW_REMEDIATION.md`](B2_REVIEW_REMEDIATION.md).

## Evidence to inspect

1. [`test_b2_verifier_hardening.py`](../../tests/test_b2_verifier_hardening.py) and the recorded [full test run](../../outputs/track_b/20261023T_b2_review_remediation/test_run_full.json). The false-pass case and malformed parity arrays are tested.
2. [Provenance audit JSON](../../outputs/track_b/20261023T_b2_review_remediation/provenance_audit_final/provenance_audit.json), covering channel/order identity, head-model geometry, coordinate and orientation metadata, reference projection, covariance support, `_psd_eigh`, and artifact hashes.
3. [`audit_b2_provenance.py`](../../scripts/track_b/audit_b2_provenance.py), which reproduces that audit from model arrays and metadata without reading recorded EEG sample values.
4. [Runtime access-boundary audit](../../outputs/track_b/20261023T_b2_review_remediation/access_boundary_audit_final.json) and [`audit_b2_v11_access_boundary.py`](../../scripts/track_b/audit_b2_v11_access_boundary.py). The synthetic archive test must deny its `data` member before NumPy reads it. This is a process-level wrapper, not an OS sandbox.
5. [Incident disclosure JSONL](../../outputs/track_b/20261023T_b2_review_remediation/incident_disclosure.jsonl). It explicitly records the earlier decompression of a 236 × 2,081 float64 EEG array, the disclosed lack of downstream use, and the limit that no complete OS-level trace independently proves that non-use.
6. [`METHOD_MATRIX.md`](METHOD_MATRIX.md) and the prior-art section in the remediation record. Review the explicit overlap with Babadi et al. (2014) mutual coherence, Scherg et al. (2022) normalized leadfield cross-correlation, and Hauk et al. (2022) resolution/PSF/CTF; also review Phillips et al. (2026) as broad context and the unresolved exact overlap for Phillips et al. (2025).

## Questions for the independent reviewer

- Does v11 reject every false-pass case covered by the corrected comparator, and are its dtype, sentinel, shape, finite-mask, rank, and tolerance checks consistent with v10?
- Do the provenance results support the declared one-model setup, including exact channel order, 236 retained channels, 8,196 fixed-orientation vertices, average-reference rank 235/236, and the leadfield/covariance projection checks?
- Is the access guard and incident disclosure adequate for the project's governance requirements, given that the guard is process-level and the incident's non-use account is not independently proven by a full execution trace?
- Does the updated prior-art matrix accurately bound the mathematical overlap and avoid novelty claims for cosine or mutual coherence?
- Recommend **PASS / HOLD FOR CHANGES / FAIL OR PIVOT** for the frozen v10 estimand, and state explicitly whether to authorize the registered v11 CPU64 recomputation against sealed Track A arrays.

The original review packet and its HOLD FOR CHANGES report remain preserved. This recheck packet does not imply approval. The registered real-array recomputation has not been run; it remains blocked until an independent reviewer records approval against the exact hashes above. No model fitting is authorized by this packet.
