# Two-sided fixed-field audit API

`observable_geometry.track_b.two_sided_audit` is a small, reusable software
layer for a **declared, pre-whitened** source-family comparison. It does not
estimate a source map from EEG by itself and does not establish a new
mathematical method.

## Inputs and equation

The caller supplies one fixed sensor field `y`, a target forward atom `t`,
an allowed target amplitude interval `[a_min,a_max]`, and one or more
alternative branches. A branch contains signed forward atoms `A`,
nonnegative coefficient caps `c`, and a total coefficient budget `B`.
Its source fields are `A w` for `0 ≤ w ≤ c` and `sum(w) ≤ B`.
Patch membership, sign choices, area weighting and units must be decided
and documented by the caller. Distinct sign/patch choices need distinct
branches. **All arrays must use the same sensor order, reference, whitening,
forward units and field amplitude convention.** The API does not verify
these scientific provenance conditions from the arrays alone.

The target residual is solved exactly over its amplitude interval. Each
alternative branch is fitted by constrained least squares. The returned
weights give a feasible upper bound `U` on the branch's best residual.
For a returned unit sensor direction `h`, the lower bound is
`L=max(0, hᵀy - support(hᵀA))`, where the capped-budget support is computed
by filling the largest positive coefficients first. This inequality is a
standard weak-dual bound. A failed optimizer can widen `[L,U]`, but cannot
turn an unresolved comparison into a certified exclusion.

For a union of branches, `min(L_j)` and `min(U_j)` bound the best
alternative residual. At declared tolerance `tau`, the API reports:

| Output | Meaning within the declared families and tolerance |
| --- | --- |
| `target_only_fits` | Target residual ≤ tau and every alternative lower bound > tau. |
| `ambiguous_both_fit` | Target residual ≤ tau and an alternative feasible upper ≤ tau. |
| `alternative_only_fits` | Target residual > tau and an alternative feasible upper ≤ tau. |
| `neither_fits_abstain` | Target residual > tau and every alternative lower bound > tau. |
| `unresolved_alternative_bounds` | Available alternative bounds straddle tau; compute more before classifying. |

The decision is **conditional on one supplied forward operator**. For an
uncertainty ensemble, call `audit_model` separately for each forward model
while holding `y` fixed. Agreement at sampled endpoints is not a certified
statement about values between them. A tolerance in whitened units needs a
separate noise/model-error calibration before it can support a statistical
error claim.

## Minimal example

```python
import numpy as np
from observable_geometry.track_b.two_sided_audit import CappedBranch, audit_model

y = np.array([1.0, 0.0])       # fixed, pre-whitened illustrative field
target = np.array([1.0, 0.0])  # target forward atom at unit amplitude
alternative = CappedBranch(
    name="example alternative",
    atoms=np.array([[0.0], [1.0]]),
    caps=np.array([1.0]),
    budget=1.0,
)
result = audit_model(y, target, (0.0, 1.0), (alternative,),
                     tolerance=0.25, model_name="illustration")
assert result.decision == "target_only_fits"
```

The present Localize-MI research result in
`research/gbf_omitted_activity_20261024/FIXED_FIELD_FORWARD_RESULTS_20261027.md`
uses a synthetic field and two physically rebuilt conductivity endpoints.
It is an example of why the `neither_fits_abstain` state matters, **not**
an empirical claim about the source of a participant's neural recording.
