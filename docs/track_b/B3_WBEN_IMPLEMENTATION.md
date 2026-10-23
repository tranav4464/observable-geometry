# Historical B3 route: independent WBEN state-space reference

> This is retained as historical implementation evidence. WBEN is not the active Track B baseline. The active B3 objective is specified in `B3_NEUROFLOWNET_IMPLEMENTATION.md`; do not use the results below to claim progress on that gate.

**Status: NOT PASSED.** The code and deterministic checks below are historical implementation evidence only. Earlier synthetic checks are excluded from the active real-data-only evaluation and cannot support Track B performance claims. The model still needs paper-fidelity review and permitted real-development-recording validation after B1 and B2 pass.

## Implemented scope

The former CPU/float64 K=1 linear-Gaussian implementation is preserved at `archive/historical_wben/src/observable_geometry/track_b/wben.py`. It is not installed or maintained as part of the active GBFs package.

The primary branch maximizes log likelihood minus the L1 penalty, matching the sparsity-promoting Eq. (4) reading in Yang and Liu (NeurIPS 2025). Its row-wise convex M-step uses cyclic coordinate descent with exact scalar soft-threshold updates. This is a transparent optimizer for the stated objective, but it does not reproduce the paper's named FASTA routine. The alternate `penalty_sign="plus"` branch records the literal plus-sign reading printed in Eq. (12) and Algorithm 1. That objective is non-concave in each transition row. Its M-step uses exact one-coordinate global maximizers in cyclic coordinate ascent and returns a stationary result, not a certificate of global optimality. This branch exists to expose the publication ambiguity; it must not be described as promoting sparsity.

## Verification

The former tests and verifier are preserved under `archive/historical_wben/`; do not run them for the active project. Their historical results below are not current validation evidence.

The tests compare posterior means, each smoothed covariance, adjacent-time cross-covariances, and marginal log likelihood against an independently assembled dense joint-Gaussian posterior. They verify both sensor-space and state-space information-form updates, including the case of more sensors than latent states and correlated observation noise. They also check KKT conditions for the L1 row solution, a known-truth transition update, both penalty-sign branches, both initializers, an unobservable zero-signal control, explicit non-convergence under rank-deficient observation, finite-horizon unstable transitions, invalid configurations, and a small end-to-end fit using the paired synthetic scalp/iEEG operators. That integration test checks interface and numerical compatibility only; it uses a two-step EM budget and is not an accuracy or convergence claim. The independent numerical evidence is in `outputs/track_b/b3_wben_reference_20261022_v9/b3_reference_verification.json`.

The dense-posterior maximum absolute differences were below `3e-16` for posterior moments and below `9e-16` for log likelihood. A 700-sample, fully observed, two-state stable synthetic case converged in three EM updates; its transition Frobenius error was approximately `0.0569`. An all-zero observation operator recovers zero transitions under a zero-signal control. A rank-deficient observation case returns non-convergence explicitly rather than disguising it as a successful fit. These are development checks under controlled conditions, not a broad recovery result.

## Limits and next scientific checks

This is an independent implementation of the state-space equations, not a bit-for-bit author-code reproduction. It uses cyclic coordinate descent rather than a reproduced FASTA package configuration, and the alternate plus-sign objective is only solved to a coordinate-stationary point. The first evidence uses an identity/abstract observation operator, not a realistic BEM lead field. No participant data or held-out confirmatory data were used. The implementation does not establish general edge-recovery accuracy, causal connectivity, source identifiability, or superiority over prior methods.

Before the B3 gate can fully pass, the remaining audit must decide whether the optimizer settings are adequately matched for an equation-level reproduction and record an independent code review. B4 robustness and benchmark claims remain unstarted.

## Optimizer source

The [official FASTA repository](https://github.com/tomgoldstein/fasta-matlab) describes FASTA as a forward-backward splitting solver and lists FISTA among its supported variants. Track B uses an independent coordinate-descent solver for the convex quadratic-plus-L1 subproblem; the FASTA reference is retained for later matched solver validation, not as the current implementation claim.
