# Per-field relative tail-closed frontier: model-only refinement

**Date:** 29 October 2026\
**Status:** implemented and independently replayed on saved model operators\
**Novelty status:** no novel method claim; this is a generalized-eigenvalue normalization of the existing S-lemma bound.

## What changed

The existing `tail_closed_margin_frontier` reports a conservative margin using
the global denominator `||B||_2`. The declared relative-separation question is
instead whether every retained field in a subspace remains separated from all
allowed alternatives by a fraction of that particular field's gain. Let `B` be
the retained operator, `C = D D.T` the omitted-family sensor Gram, and
`G = B.T B`. For coefficient budget `||z|| <= eta ||c||`, define

```text
H(t) = t B.T (C + t I)^(-1) B - t eta^2 I.
```

At a fixed positive multiplier `t`, a `k`-dimensional retained subspace `V`
has relative margin `delta` when

```text
V.T [H(t) - delta^2 G] V is positive definite.
```

On the effective row space of `B`, `G` is positive definite. The largest
possible `delta^2` at fixed `t` is therefore the `k`th largest generalized
eigenvalue of `(H(t), G)`. Maximizing over the finite multiplier grid yields a
numerically computed, attainable lower bound for each rank. The code maps the
generalized eigenvectors back to coefficient space and stores an orthonormal
basis for direct replay. Rank-deficient directions in `B` are excluded from
the generalized problem; they cannot have positive margin for `t > 0`.

This corrects the scale of the reported diagnostic for its declared relative
estimand. It does not introduce a new optimization principle: the generalized
eigenvalue reduction is standard linear algebra applied to the existing
S-lemma expression. The multiplier search is a finite logarithmic grid, not a
continuous global optimizer. Float64 replay is not outward-rounded formal
verification.

## Reproduction and independent replay

Run from the repository root, using only the previously approved finite-mesh
operator Grams. The scripts do not read EEG/SEEG samples or outcomes:

```powershell
python scripts\track_b\run_tail_closed_relative_frontier.py `
  --operator-grams ..\research\gbf_omitted_activity_20261024\implicit_tail_001\operator_grams.npz `
  --reference-result ..\research\gbf_omitted_activity_20261024\tail_closed_002\result.json `
  --out outputs\track_b\20261029T_relative_frontier_002 `
  --grid-size 2049

python scripts\track_b\verify_tail_closed_relative_frontier.py `
  --run outputs\track_b\20261029T_relative_frontier_002 `
  --out outputs\track_b\20261029T_relative_frontier_002\independent_check_001.json
```

The verifier independently reconstructs `H(t)` with a direct linear solve,
checks input hashes, and replays the generalized minimum eigenvalue of every
positive-margin saved basis. It also checks JSON/NPZ agreement, rank-frontier
monotonicity, and that the error-inflated margins do not exceed nominal ones.

The updated source package also built as a development wheel and imported the
new API directly from the wheel archive (not from the source checkout):
`outputs/track_b/20261029T_relative_frontier_wheel_002/observable_geometry-0.1.2-py3-none-any.whl`,
SHA-256 `792B050FA354403653178F6B5344984779D8B2E0891BF55E2B440C6B9EB281EB`.
This is a local verification artifact, not a published release.

## Results on the saved one-model operator

The run used `retained_operator` and `full_tail` from
`implicit_tail_001/operator_grams.npz`, with `eta=1` and the existing one-sided
Gram error bound `1.562616836961929e16`. It is a model-only calculation on one
participant-specific forward model and a declared shifted-FEM tail prior.

| Relative-margin threshold | Largest robust retained rank on 2,049-point grid |
|---:|---:|
| 1% | 22 |
| 2% | 21 |
| 5% | 19 |
| 10% | 15 |

The corresponding legacy global-gain-normalized sweep reported ranks 18, 16,
11 and 8 at those numeric cuts. **Those counts are not a valid head-to-head
performance comparison:** the denominators differ. The legacy statistic is a
more conservative scale bound; the new statistic is the explicitly
per-retained-field relative margin. The revised counts must not be interpreted
as increased physiological resolution or as a decision benefit.

Independent direct-matrix replay passed for all 28 nominal and 25
error-inflated positive-rank bases. The largest reported squared-margin excess
over the replay was `1.37e-13`; the maximum relative-margin discrepancy was
`1.34e-12`. The result is saved at
`outputs/track_b/20261029T_relative_frontier_002/`, with input and code hashes
in `result.json` and replay details in `independent_check_001.json`.

## Same-objective comparison with fixed subspaces

To avoid comparing unlike margin definitions, a second run evaluates each
saved rank on the same error-inflated operator, coefficient budget, and
2,049-point multiplier grid. For each fixed subspace it directly computes
`max_t lambda_min(V.T H(t) V, V.T B.T B V)` using Cholesky normalization.
Comparators are the bilateral interleaved low-mode basis and the leading
sensor-SVD basis. Results are descriptive only; the candidate subspaces were
selected to optimize this objective.

| Relative-margin cut | Optimized subspace | Sensor-SVD | Bilateral low modes |
|---:|---:|---:|---:|
| 1% | 22 | 19 | 0 |
| 2% | 21 | 19 | 0 |
| 5% | 19 | 17 | 0 |
| 10% | 15 | 13 | 0 |

All **75 rank/family rows** passed an independent direct-solve replay. The
largest reported squared-margin excess was `5.28e-16`, and the largest margin
difference was `3.38e-14`. See
`outputs/track_b/20261029T_relative_baseline_002/result.json` and
`independent_check_001.json`.

The comparison is reproducible with:

```powershell
python scripts\track_b\compare_relative_frontier_baselines.py `
  --operator-grams ..\research\gbf_omitted_activity_20261024\implicit_tail_001\operator_grams.npz `
  --frontier-run outputs\track_b\20261029T_relative_frontier_002 `
  --reference-result ..\research\gbf_omitted_activity_20261024\tail_closed_002\result.json `
  --out outputs\track_b\20261029T_relative_baseline_002

python scripts\track_b\verify_relative_frontier_baselines.py `
  --run outputs\track_b\20261029T_relative_baseline_002 `
  --out outputs\track_b\20261029T_relative_baseline_002\independent_check_001.json
```

This is not evidence that the optimized method outperforms an independent
algorithm: the optimized subspace is chosen to maximize this very metric, so
its advantage over fixed bases is expected. At each fixed `t`, maximizing the
minimum generalized Rayleigh quotient over rank-`k` subspaces is exactly the
top-`k` generalized-eigenvalue solution. Therefore direct generalized-eigen
fitting is the same optimization written directly, not an algorithmically
distinct competitor. The result confirms a model-conditional representation
difference versus fixed bases, but no new guarantee, computational advantage,
calibrated threshold, or researcher decision value. The cuts are retrospective
and must not be interpreted as measured-noise detectability.

## Interpretation and next requirement

This supplies a better-scaled model-conditional diagnostic for the current
software. It does **not** show that the source-family assumption is
physiological, calibrate the margin as a noise probability, improve a
researcher decision, localize endogenous sources, generalize across
participants, or establish novelty. The result remains conditional on the
finite source mesh, one forward model, the tail Gram and its error inflation,
and the coefficient budget.

Before making a performance claim, compare this relative objective with
matched direct constrained-subspace optimization and established resolution
metrics using a predeclared decision and admissible measured endpoint. WSGZP
signal analysis remains gated because participant-level geometry and
preprocessing provenance are unresolved. Preserve this run as a model-only
software check, not a substitute for that validation.
