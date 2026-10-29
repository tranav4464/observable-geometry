# Novelty resume audit: Observable Geometry

**Date:** 29 October 2026\
**Purpose:** resume the novelty search from the current evidence without changing
the sealed Track A release or opening the WSGZP signal gate.

## Decision standard

The goal is to test whether Observable Geometry's source-family analysis
improves a specific researcher decision beyond established methods. Novelty
is an outcome, not a requirement to be manufactured. This audit does not
authorize EEG/SEEG sample access or change the B4-B7 gate statuses.

## Candidate method under the strongest challenge

The existing source-complexity quantity is

```text
q*(tau) = min{q : delta_q <= tau},
```

where `delta_q` is the smallest whitened residual among alternatives supported
on at most `q` declared cortical windows under one forward model, an exclusion
rule, and a moment budget. For two selected constructed fields in one
participant model, the project has independently replayed a global `q=1`
lower bound and feasible `q=2` upper bounds. Those establish conditional
`q*=2` intervals only for the declared model and source family. They do not
establish the number of biological generators or source recovery.

The `q*=2` sandwich is an elementary implication of nested model classes:
if `U2 < L1`, then `q*(tau)=2` for `U2 <= tau < L1`. The project does not
claim this inequality as a new theorem. The unrestricted two-window witness
also relied on mixed signs within both patches; the same frozen candidates
under one-sign-per-patch constraints no longer crossed the one-unit stress
threshold. Full-mesh `q=2` optimality remains unproved.

## Prior-art result

The targeted primary-source check confirms that the ingredients are already
well populated:

* Bai and He (2006) estimate source number from measured scalp EEG. Source
counting is not new, even though their model-order estimand differs from the
project's counterfactual number of compact alternative windows.
* Friston et al. (2008) use empirical Bayes to select multiple compact cortical
  source priors. Multiple sparse patches are not new.
* Juditsky and Nemirovski (2019) provide near-optimal estimation of linear and
  N-convex functionals over finite unions of convex compact sets under indirect
  noisy observations. A source-family union and functional recovery are not
  new by themselves.
* PATCH-AP (Giri et al., 2025) models smooth, spatially extended cortical
  patches. Smooth-patch assumptions are not new.
* The 2026 GBF study and XDL-ESI (2024) already analyze source localization or
  extent using the same iES-CCEP/WSGZP cohort. A new source map, CCEP window, or
  stimulated-contact comparison alone is not a distinct contribution.
* Time-dependent inverse methods are established, and GBF already reports
  spatiotemporal CCEP reconstruction. A time-resolved ambiguity curve would
  need a specific incremental decision value; temporal variation alone is not
  novelty.

Primary references: [Bai & He (2006)](https://doi.org/10.1109/TBME.2006.876620),
[Friston et al. (2008)](https://doi.org/10.1016/j.neuroimage.2007.09.048),
[Juditsky & Nemirovski (2019)](https://doi.org/10.1093/imaiai/iaz011),
[PATCH-AP (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12700762/),
[GBF (2026)](https://www.nature.com/articles/s41551-026-01664-0), and
[XDL-ESI (2024)](https://doi.org/10.1016/j.neuroimage.2024.120802).

## Current novelty verdict

**No novel method is supported by the present evidence.** The `q*(tau)` output
is a potentially useful model-conditional diagnostic, but its current
mathematics has not shown a distinct guarantee, computational advantage over
direct constrained fitting, or measured-data decision benefit. Existing
source-family results are conditional model calculations, and the primary
held-out WSGZP comparison is not protocol-locked or authorized.

One empirical question remains worth testing after the gates pass: whether
defensible source-family constraints change the *focal-versus-ambiguous
interpretation* of measured post-artifact CCEP scalp responses in a reproducible
subset of participants, beyond GBF, XDL-ESI, direct fitting, and matched
resolution/patch baselines. Sparse responsive SEEG contacts can provide
positive-contact corroboration only; they cannot establish whole-cortex source
truth or calibrate the ambiguity label. A result here could be a new empirical
finding or a useful software contribution, but it is not currently novel.

## Work that can proceed now

1. Compare the exact `q*(tau)` estimand and certificate against model-order,
   multiple-sparse-prior, finite-union, and disjunctive optimization methods.
   Reject the method claim unless an unhandled theorem or certified cost/tightness
   advantage survives that comparison and independent replay.
2. Solver development may continue on algebraic unit cases, and approved model
   arrays may be inspected for model-only operator checks. Do not use a
   forward-model-generated field as an experimental observation or as
   physiological evidence. Any algorithmic performance comparison on
   observation fields must wait for a measured field under a locked protocol.
   Direct constrained fitting remains the answer-equivalence oracle.
3. Keep candidate empirical evaluation closed until coordinate/forward-model
   review, released-array preprocessing semantics, and a frozen participant
   split and endpoint satisfy their gates. The paper's study-level
   coregistration statement and BIDS `T1w` declaration are relevant provenance,
   but the current review still flags participant-level geometry and
   preprocessing checks as incomplete.
4. Do not add ML unless a learned component beats a matched deterministic
   baseline while preserving the certificate. No such role is established.

The fixed-area lower-envelope ranking proposed in
`NOVELTY_TARGET_SELECTION_20261029.md` has now received a separate algebraic
falsification: `FIXED_AREA_SCORE_FALSIFICATION_20261029.md` shows that any
parcel avoided by one member of the compatibility set has guaranteed mass
zero. The ranking must not be frozen or tuned after outcome access. This
rejects that scoring rule, not the broader empirical question.

## Outcome rule

If no distinct guarantee or decision advantage survives these tests, preserve
the reproducible software contribution and report **no novel method supported**.
Do not call a model-only discrepancy, an alternative name for `q*(tau)`, or a
numerically different fit a discovery.
