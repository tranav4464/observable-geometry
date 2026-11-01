# Scientific and submission review, 1 November 2026

**Scope:** Observable Geometry's accepted TKS software and the 7–10 minute article. This is an internal skeptical review, not an independent researcher endorsement.

## Equation and implementation check

For leadfield columns `g_i` and covariance `C`, the command eigendecomposes the symmetric covariance, retains eigenvectors above the declared relative eigenvalue cutoff, and computes supported-subspace whitened columns `z_i = Lambda_+^(-1/2) U_+^T g_i`. It rejects a leadfield with material components outside covariance support. For two valid columns, the ranked score is `rho_ij = |z_i^T z_j| / (||z_i|| ||z_j||)`. The stored unit-target profiled residual is `sqrt(1-rho_ij^2)`. This follows by minimizing the norm of `u_i - a u_j` over a signed scalar `a` for unit vectors. The absolute value therefore discards polarity and amplitude; neither nuisance convention should be mistaken for physiological equivalence.

The code applies a Euclidean coordinate exclusion, excludes self-pairs and invalid columns, then sorts by descending cosine with source index as the deterministic tie break. It reports directed top-k alternatives. Analytic tests cover polarity, orthogonality, covariance rank and invalid inputs; a new joint sensor-permutation test confirms that consistently reordered leadfield rows and covariance axes preserve the output. These checks establish code/equation agreement for declared arrays. They cannot prove that a user-supplied covariance, sensor reference, electrode registration or coordinate frame is physically correct.

## Scientific verdict

| Claim | Verdict | Evidence or limitation |
|---|---|---|
| The software reports distant pairs with similar model-predicted scalp patterns | **Supported** | Public-clone command and licensed model-only replay; exact output hashes in the fresh-clone check. |
| The accepted one-model summary is numerically reproducible | **Supported within same-input scope** | 40,980 directed rows and score/summary files match prior hashes; separate CPU64 calculation is recorded in B2/B8. |
| The output differs from an MNE PSF summary | **Supported descriptively** | B7 reports paired rank correlations of 0.480 and 0.434 on one model. Distinct values do not prove distinct decisions. |
| The report improves a researcher's source attribution decision | **Unsupported** | No held-out, predefined decision comparison against direct leadfield similarity or PSF/CTF. B7 correctly pivoted. |
| The output localizes endogenous neural events or generalizes across participants | **Unsupported** | The main result is model-only. The stimulation pulse is an electrical artifact, and WSGZP geometry is not accepted for source analysis. |
| The cosine or profiled residual is a novel mathematical method | **Unsupported** | Angle-based leadfield separability and inverse-resolution work are prior art. The current contribution is a bounded, auditable software workflow. |

GBF inverse reconstruction and `distinguish` share forward-model provenance but solve different tasks. The GBF reproduction used a limited mode count and did not reproduce every paper benchmark. The diagnostic compares forward columns and does not run GBF inversion. PSF/CTF results depend on an inverse operator; direct normalized leadfield similarity does not. That distinction explains the report's workflow, but direct similarity maps remain a close baseline and an unproven decision-value competitor. The 0.95 score cutoff is descriptive, not a statistical error probability or an accepted reporting threshold.

## Article and reviewer path

The article uses the same 236-channel, 8,196-vertex, rank-235, 20 mm, top-five model contract as the submission. It identifies 40,980 as directed rows, states the one-participant unit of analysis and avoids p-values over spatially dependent vertices. It separates the model-only result, the rejected stimulation-pulse route and future measured-data validation. The article is about 2,000 words, within the requested reading-time range. Its claim-to-evidence map is `docs/tks/article-claim-audit.md`; the public README, submission, demo and article link to one another. Local Markdown links were checked for existence. Final destination checks should be repeated in the eventual publishing interface.

The strongest realistic use case is pre-interpretation inspection of specific distant alternatives under a declared model. The strongest open scientific test is whether this report changes a predefined researcher decision correctly beyond direct leadfield similarity and matched resolution diagnostics on independently verified measured data. The current software is ready for a bounded TKS submission. A scientific novelty or physiological recovery claim is not ready.
