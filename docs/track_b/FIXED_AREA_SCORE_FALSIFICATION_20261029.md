# Fixed-area parcel-score falsification

**Date:** 29 October 2026\
**Status:** algebraic design audit; no EEG/SEEG samples read, no WSGZP outcomes used\
**Scope:** the guaranteed parcel-mass score proposed in `NOVELTY_TARGET_SELECTION_20261029.md`

## Decision

Do **not** freeze the proposed guaranteed parcel-mass ranking as the primary
researcher decision. Its conservative lower-envelope definition has an exact
degeneracy: a parcel receives score zero whenever the compatible set contains
even one explanation with no source mass in that parcel. If the set contains
alternatives supported in disjoint parcels, every parcel can score zero even
though each alternative individually fits the observation. A resulting
abstention would correctly express worst-case ambiguity, but it cannot support
the proposed ranked follow-up shortlist in that case.

This rejects one scoring rule. It does **not** show that source-family
observability is useless, and it does not establish or refute a novel method.

## Exact argument

For a nonempty compatible set `K(y)`, the proposed parcel score is

```text
g_j(y) = inf_{x in K(y)} M_j(x) / M(x),
```

where `M_j(x)` is the nonnegative source mass in parcel `j` and `M(x)` is the
total source mass. Assume `M(x) > 0` for every compatible candidate. Since
`M_j(x) / M(x) >= 0`, if there is any `x_j^0 in K(y)` with `M_j(x_j^0)=0`, then

```text
0 <= g_j(y) <= M_j(x_j^0) / M(x_j^0) = 0,
```

so `g_j(y)=0`. This follows directly from the infimum; no optimization
implementation or EEG observation is needed to establish it.

For a purely algebraic example, let `K` contain one admissible explanation
whose mass lies entirely in parcel A and another whose mass lies entirely in
parcel B. Then `g_A=g_B=0`: each explanation avoids the other parcel. This is
an identity about the score, not simulated neural data or evidence about a
participant.

## Consequence for the novelty claim

The proposed score cannot be described as a useful location-ranking method
until a pre-outcome argument shows that its compatible set has enough shared
mass to produce a nonzero, stable ranking on the intended task. No such
measured-data demonstration exists, and no outcome-blind dataset analysis has
established this condition. Relaxing the infimum, adding family weights, or
choosing the area budget after viewing SEEG labels would change the estimand
and create outcome-tuning risk.

The underlying held-out decision question—whether a frozen scalp-derived
shortlist captures more *sampled responsive SEEG contacts* than matched
baselines—remains potentially testable if geometry, preprocessing, licensing,
and protocol gates are resolved. That endpoint is positive-contact
prioritization only. It is not whole-cortex source truth, calibrated source
coverage, or proof of endogenous source recovery. Even a positive result would
be an empirical utility finding, not automatically a novel algorithm.

## Required next step

Before any signal analysis, either:

1. retain this score only as a deliberately conservative ambiguity diagnostic,
   and define a separate shortlist rule using independent, prospectively
   justified evidence; or
2. replace it with a mathematically specified nondegenerate decision rule,
   then show outcome-blind that it is identifiable, stable, and not equivalent
   to GBF, direct constrained fitting, established patch/resolution methods,
   or standard set-valued inverse analysis.

Do not choose between these options using held-out SEEG outcomes. Until one is
justified and the other data/provenance gates pass, the novelty outcome remains
**no novel method supported**; the bounded software contribution remains the
supported route.

## Relation to existing evidence

The score was proposed in `docs/track_b/NOVELTY_TARGET_SELECTION_20261029.md`.
`CALIBRATION_IDENTIFIABILITY_AUDIT_20261029.md` separately establishes that
WSGZP's sparse positive SEEG contacts cannot calibrate whole-cortex spatial
coverage or the truth of an ambiguity label. `PROTOCOL_LOCK.md` remains
UNLOCKED, and the WSGZP signal gate remains closed. This note adds an
algebraic falsification of the candidate ranking rule; it does not change any
gate status or authorize signal access.
