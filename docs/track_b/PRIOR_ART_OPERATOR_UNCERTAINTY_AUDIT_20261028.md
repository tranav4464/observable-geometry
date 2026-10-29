# Prior-art audit: uncertain forward operators and sparse source outputs

**Date:** 28 October 2026\
**Purpose:** test whether continuous forward-model uncertainty or source
complexity is, by itself, a novel-method direction for Observable Geometry\
**Status:** novelty threat identified; no new-method claim supported\
**Data boundary:** literature/code review only; no WSGZP signal values read

## Project object being compared

The proposed certificate uses a measured sensor field `y`, a participant
leadfield `L(θ)` with admitted forward perturbation `θ ∈ U`, and source-family
sets `F_j`. Its compatibility object is

```text
C(y; τ) = ⋃_j ⋃_{θ∈U} { x ∈ F_j : ℓ(y, L(θ)x) ≤ τ }.
```

The intended output is a range of spatial functionals over this set, plus an
auditable focal/ambiguous/unsupported decision. This is a joint
set-valued-recovery problem over a union of structured source families and an
uncertain observation operator. The project must not equate the fact that this
combined object is written in one EEG-specific notation with a new method.

## Closest primary mathematical work

### 1. Robust recovery with an uncertain sensing matrix

Bekri, Juditsky and Nemirovski study indirect observations with uncertain
observation matrix. Their model includes

```text
ω = A[η]x + ξ = Ax + D[η]x + ξ,   η ∈ U,
```

and their target is a linear image `Bx` for `x` in a convex compact/ellitopic
set. They derive confidence-risk bounds and construct linear or polyhedral
estimates under random and structured norm-bounded operator uncertainty. In
the uncertain-but-bounded case, their analysis explicitly imposes uniform
constraints over `x` and `η`; their polyhedral-estimate bound is obtained by
convex optimization. See the model and risk definition in the paper's
equations (1), (7), and the structured-uncertainty development in §3,
especially equations (60)–(74).

**Overlap:** a leadfield perturbation `L(θ)` is an uncertain sensing operator.
If `L(θ)` is represented by an affine/structured perturbation and a fixed
source branch is convex, robustness to that perturbation is established
mathematical territory. Replacing generic `A[η]` by an EEG leadfield or
sampling a denser forward ensemble is not a new robust-inverse principle.

**Limit of the overlap:** the paper estimates prescribed linear images under
its signal-set and uncertainty assumptions. It does not, from the inspected
sections, directly provide the exact full spatial identified set over all
EEG source families and a nonconvex union. Therefore it is a priority threat,
not proof that every possible Observable Geometry implementation is
identical. A claimed difference must identify a new theorem/algorithm beyond
the applicable branchwise robust-estimation result.

Primary sources: [Bekri, Juditsky & Nemirovski, English 2025 journal version](https://doi.org/10.31857/S0005117925080038),
[official article page](https://journals.rcsi.science/0005-2310/article/view/304786),
[English preprint, arXiv:2309.06563](https://arxiv.org/abs/2309.06563).

### 2. Recovery over unions of convex sets

Juditsky and Nemirovski study near-optimal recovery of linear and
N-convex functionals when the unknown signal lies in a finite union of
convex compact sets under indirect noisy observations. This overlaps the
project's source-family union and several parcel-mass or linear spatial
functionals. A finite family list, branchwise convex solver, functional
range, or a new label for the resulting set is not enough for novelty.

Primary source: [Juditsky & Nemirovski, 2020, DOI 10.1093/imaiai/iaz011](https://doi.org/10.1093/imaiai/iaz011),
[arXiv:1804.00355](https://arxiv.org/abs/1804.00355).

### 3. Sparse signals and linear images

Juditsky and Nemirovski's September 2026 preprint studies estimating a linear
image `Bx` from `ω=Ax+ξ` when `x` belongs to a convex compact set and is
`s`-sparse, using `ℓ1`-minimization without requiring a null-space or RIP
assumption on `A`.

**Equation-level update (full arXiv HTML inspected 28 October 2026):** the
problem statement (Eq. (1)) is `ω=Ax+ξ`, with `x∈X` and `Cx` `s`-sparse,
and the target is either a linear functional `gᵀx` or a linear image `Bx`
(Introduction, §1). Its basic estimate (Eq. (2)) is an `ℓ₁`-minimizing
Dantzig-style fit under a contrast residual constraint; the general
polyhedral estimate is Eq. (7). Propositions 4.2–4.3 give high-probability
error bounds for recovering sparse `Cx`; §4.1.3 treats linear images `Bx`
when `B=FC`; §5 constructs computable risk bounds for quadratic error; and
§6 gives sparse-hypothesis tests with an explicit reject/undecided outcome.
Thus “recover spatial source values,” “bound parcel-like linear summaries,”
or “abstain when sparse hypotheses are not separated” are not, in
isolation, a novelty claim. The paper does not directly establish an EEG
guarantee for topology-constrained cortical support under a continuously
uncertain leadfield; that remaining difference is a research question, not
evidence of novelty. Its numerical illustrations are simulations and do not
count as measured-data validation for this project.

Primary source: [Juditsky & Nemirovski, 2026 preprint, arXiv:2609.06182](https://arxiv.org/abs/2609.06182), especially §1 Eqs. (1), (2), (7), §§4–6 and Propositions 4.2–4.3.

### 4. Exploring near-optimal solution sets

Skaf and Boyd (2010) define the convex `ε`-suboptimal set and compute
bounding boxes, diameter estimates and ellipsoidal approximations by solving
a modest number of related convex programs. They explicitly motivate this in
estimation: a large near-optimal set means substantially different parameter
values are nearly as plausible. Thus reporting spatial extent or ambiguity
around a fit is also established for convex problems. Our possible distinction
would have to address the structured nonconvex source-family/uncertain-operator
case with a validated advantage, not simply visualize a near-optimal set.

Primary source: [Skaf & Boyd, “Techniques for exploring the suboptimal set,”
Optimization and Engineering 11 (2010)](https://stanford.edu/~boyd/papers/expl_subopt.html).

### 5. Set-valued inverse solutions and alternative-source uncertainty

The set-valued output is itself an established inverse-problem idea. In
set-membership inverse methods, a measurement tolerance and model constraints
define a feasible parameter set; interval/set-inversion methods propagate
measurement uncertainty to a range of compatible solutions. In M/EEG,
Bayesian methods including SESAME explicitly represent uncertainty over
multiple source configurations and note that a single best source estimate
conceals the existence of alternatives. Thus “report a set instead of one
map” is a useful product choice, not a novelty claim by itself.

Relevant primary/practice sources: [Dealing with Inconsistent Measurements
in Inverse Problems: An Approach Based on Sets and Intervals (2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7274699/),
[SESAMEEG (2024)](https://doi.org/10.3389/fnhum.2024.1359753).
These works do not establish that every EEG connected-patch/forward-uncertainty
functional has already been computed; they prevent us from claiming the
general set-valued uncertainty idea as new.

### 6. EEG-specific noise-feasible search and connected-support optimization

Srebro (1996) explicitly frames the bioelectric inverse problem as searching
a measurement-noise-constrained feasible set for physiologically plausible
source solutions, using regularized inverses to restrict that search. This is
direct EEG-specific prior art against a “first noise-compatible source set”
claim. The accessible PubMed abstract describes a model-system test in a
three-shell spherical head replica; it does not resolve the precise family
union, operator uncertainty, calibration, or held-out decision questions in
this project. Primary record: [DOI 10.1016/0013-4694(95)00263-4](https://doi.org/10.1016/0013-4694(95)00263-4).

The 2023 AAAI paper *Electrophysiological Brain Source Imaging via
Combinatorial Search with Provable Optimality* (ESI-A*) formulates a fixed-size
support search under a least-squares data-fit objective, grows connected
candidate supports on the cortical mesh, and uses an A* heuristic with an
optimality guarantee. It reports synthetic evaluations and real epilepsy EEG
comparisons to resection/seizure-onset references. This preempts a generic
claim to be the first exact or optimal graph search for connected cortical
sources, and directly overlaps any proposed connected-patch enumeration
accelerator. The paper returns a best fixed-size support; the inspected
formulation does not produce a calibrated set of all compatible source
families over continuous participant-specific leadfield uncertainty. This
remaining object difference requires more than rebranding ESI-A* with a
robustness wrapper. Primary source: [AAAI proceedings PDF](https://ojs.aaai.org/index.php/AAAI/article/download/26471/26243),
especially Eqs. (1)–(4), pp. 12491–12492, search construction and algorithm,
and its real epilepsy-data evaluation, pp. 12496–12497.

## Exact reduction of the proposed compatibility object

After whitening, write the observed sensor response as `z=W y`, the uncertain
forward operator as `A(θ)=W L(θ)`, and the calibrated tolerance as `τ`. For a
fixed forward instance `θ`, source family `j`, and convex family branch
`F_{j,b}`, the branch-compatible set is

```text
K_{j,b,θ}(z) = {x ∈ F_{j,b} : ||z - A(θ)x||₂ ≤ τ}.
```

For a fixed `θ`, this is convex whenever `F_{j,b}` is convex. A finite
uncertainty grid and finite branch list produce a finite union of such sets.
For a linear spatial functional `hᵀx`, the lower and upper reported values
are

```text
underline_h(z) = min_{j,b,θ}  min_{x ∈ K_{j,b,θ}(z)} hᵀx
overline_h(z)  = max_{j,b,θ}  max_{x ∈ K_{j,b,θ}(z)} hᵀx.
```

This is ordinary constrained functional optimization per branch, followed by
union aggregation. A finite grid approximation, a list of feasible branches,
or a parcel-wise min/max wrapper therefore does not establish a new method.

If `A(θ)=A₀+Σ_k θ_k A_k`, optimizing over `x` and continuous `θ` jointly
introduces bilinear terms `θ_k A_k x`; the joint set is generally
nonconvex. Existing uncertain-operator robust estimation is directly
relevant, but does not automatically prove an exact spatial identified-set
range for every connected-patch family. A genuinely distinct mathematical
step would have to provide a sound inner/outer enclosure or exact extremum
for this **specific nonconvex joint problem**, preserve family disjunctions,
bound numerical error, and be tighter or more useful than established robust
optimization/branchwise methods. Merely discretizing `θ` is not such a bound.

There is an additional structure caveat: a spatiotemporal smooth patch written
as `J=a sᵀ`, with both spatial amplitudes `a` and time course `s` unknown, is
rank-one and generally nonconvex even when its support and sign are fixed.
The fixed-forward convex-branch reduction applies only after a genuinely
convex parameterization is specified; it must not silently be applied to
rank-one temporal models. A product parameterization, its relaxation, or a
bilinear solver also needs its own prior-art comparison.

There is an additional structure caveat: a spatiotemporal smooth patch written
as `J=a sᵀ`, with both spatial amplitudes `a` and time course `s` unknown, is
rank-one and generally nonconvex even when its support and sign are fixed.
The fixed-forward convex-branch reduction applies only after a genuinely
convex parameterization is specified; it must not silently be applied to
rank-one temporal models. A product parameterization, its relaxation, or a
bilinear solver also has close optimization precedents and would need its own
prior-art comparison.

The quantifier matters. **Existential compatibility** uses the union over
`θ`: at least one admitted head model and source can explain the observation.
**Uniform robustness** asks for a statement to hold for every admitted `θ`.
These answer different questions and must not be exchanged in prose or code.
Existential compatibility can make ambiguity sets wider; uniform guarantees
can be conservative. A calibration threshold for residual compatibility is
not a probability that a family or source is true.

Two small exact reductions help keep the computational claims honest:

* A standard support-function/dual lower bound on the distance from `z` to
  `⋃_{θ∈U} A(θ)F` is a lower bound on distance to its convex hull. It can be
  vacuous even when every actual branch is separated. For the purely
  algebraic example `F={(1,t): |t|≤1}`, `A(θ)(1,t)=(θ,t,θt)`, `|θ|≤1`, and
  `z=(0,0,1)`, direct minimization gives
  `min_{θ,t} ||z−A(θ)(1,t)||₂ = 1`: writing `q=θt`, the squared residual is
  `θ²+t²+(1−q)² ≥ 2|q|+(1−q)² ≥ 1`. But the convex hull contains `z`, since
  it is the midpoint of `(1,1,1)` and `(-1,-1,1)`, so the hull-based lower
  bound is zero. This is an algebraic relaxation counterexample only, not
  neural data or evidence of a new method.
* The quantifier order changes the question. With scalar observation
  `y=1`, `A(θ)=θ∈[1,2]`, and `x∈[1/2,1]`, existential fitting has
  `min_θ min_x |1−θx|=0`, while requiring one `x` to fit uniformly over all
  `θ` gives `min_x max_θ |1−θx|=1/3`. A protocol must choose one semantics;
  swapping the order would silently change the estimand.

## Reduction verdict and smallest possible novelty claim

The proposed high-level object reduces to established components on a finite
grid and convex family branches. The only unresolved computational gap is a
validated, useful enclosure of spatial-functional extrema under a continuous
uncertain operator and the project's topology-constrained source-family
union. That is not yet a contribution; it is a sharply stated research
question. Before coding a solver, prove at least one of the following:

* a nontrivial certified outer bound for a spatial functional that is tighter
  than branchwise robust relaxations and remains valid over the entire
  uncertainty set; or
* an exact algorithm for the declared connected multi-patch family with a
  proven complexity reduction over direct enumeration/branch-and-bound; or
* a held-out measured researcher decision that existing set-valued,
  Bayesian, GBF, direct-fit and resolution methods do not provide.

If none is achieved, classify the output as established set-valued inverse
analysis packaged as validated software, not a novel mathematical method.

## Consequence for Observable Geometry

The candidate **continuous robust source-family certificate** is now
down-ranked as a novelty route. Its generic components are close to existing
work:

* uncertain forward operator → robust indirect-observation recovery;
* finite source-family union → union-of-convex-set recovery/testing;
* sparse/patch source structure → sparse and structured inverse methods;
* noise-compatible EEG source sets → prior feasible-set search (Srebro, 1996);
* optimal connected-support search → ESI-A* graph search (AAAI 2023);
* scalar confidence/risk → existing statistical and conformal calibration.

The only possible mathematical gap is a specific, proved step for computing
or bounding the *spatial identified set* over the project's exact
connected-patch/multi-patch family **jointly** with a continuous, physically
bounded EEG forward uncertainty set, beyond both robust branchwise recovery
and ESI-A*'s fixed-size connected-support optimum. The proposed step must
preserve the family disjunction, quantify uncertainty in the reported spatial
functional, and beat direct enumeration/branch-and-bound on a useful audited
decision. This gap is not established. The proposed families are not yet frozen,
participant geometry is not cleared, and the available WSGZP release does not
provide complete truth for later CCEP generators.

Before implementing such a method, require a formal reduction test:

1. Write the project optimization and guarantee in the notation of the
   uncertain-operator and finite-union papers.
2. Determine whether each convex source branch can be handled by a known
   robust estimator and the family union by established finite-union
   aggregation/testing.
3. If so, record that the method is not novel unless a new exact spatial-set
   guarantee or useful complexity result is proved.
4. If not, isolate the smallest missing lemma/algorithmic step and state its
   assumptions, proof obligation, computational scaling and a falsifying
   example before coding it.
5. For an empirical finding, test a preregistered interpretation or external
   decision against single-map GBF, patch and resolution baselines on valid
   held-out measured data. For a new algorithm, compare the same certified
   object to direct constrained fitting as an equivalence oracle; require a
   proved guarantee or certified computational advantage, not a different
   answer.

The empirical candidate remains an independent question: whether an
ambiguity report adds a useful decision on WSGZP. Because the closest GBF work
already uses that data route and the released epochs lack verified event
identity, independent EEG–SEEG pairing, and cleared geometry, the current
dataset cannot yet support a decisive source-truth or false-attribution
claim. An empirically interesting secondary result could still be reported
narrowly, but it would not by itself establish a new method.

## Current classification

**Continuous-uncertainty novelty:** not supported; generic robust estimation
under operator uncertainty is close prior art.\
**Source-complexity novelty:** not supported; sparse-source and finite-union
recovery are close prior art.\
**Combined identified-set method:** open only as a precise, falsifiable
mathematical gap; do not implement as a novelty claim until the reduction test
shows what existing methods fail to provide.\
**WSGZP empirical novelty:** unverified; current provenance and reference
limits prevent a true-source accuracy claim.

## Adversarial reduction and endpoint correction (28 October 2026)

Independent mathematical review identifies an important equivalence oracle:
for the same declared source-family set, uncertainty set, loss, tolerance and
spatial functional, exhaustive direct constrained fitting that computes the
minimum and maximum of that functional over every feasible branch returns the
same identified-set report as the proposed certificate by definition. A
different report against that oracle means the assumptions, approximation,
or numerical accuracy differ. Therefore a new algorithm must show a proved
complexity/tightness advantage while returning the same certified object, or
state a genuinely different guarantee. Merely changing the implementation or
the displayed decision is not a mathematical novelty result.

An independent protocol review found that `COG_PROTOCOL_AMENDMENT_20261028_v4.md`
averages the released trials within each held-out stimulation condition and
rejects event-row A/B/C splits, while §7 of `NOVELTY_PROOF_PLAN_20261028.md`
still describes fitting on one half and predicting the other. The v4
participant-grouped split prevents cross-participant tuning leakage, but it
does not create an independent second observation of each held-out condition.
That within-condition repeatability/prediction endpoint is therefore not
currently executable as written. Do not score the same run-average field
against a model fitted to it and call that held-out prediction.

The closest feasible WSGZP external outcome is sparse positive scalp–SEEG
concordance at a fixed cortical-area budget, with implant-sampling and
stimulation-distance controls. This cannot establish whole-cortex sensitivity,
specificity, true-source coverage or source recovery. The dataset paper
already proposes scalp source-localization/SEEG concordance, and the GBF study
already analyzes the cohort, so the exact endpoint delta must still be
demonstrated. If event mapping, geometry, preprocessing semantics and protocol
cannot be cleared, no measured-data novelty claim is currently testable with
this route.

**Updated novelty decision:** no algorithmic novelty candidate passes. The
only live avenue is a narrowly stated measured-data empirical finding about
source-family-dependent spatial ambiguity, evaluated against an executable
SEEG-positive concordance endpoint and strong baselines. It remains
unverified and may end as useful validated software or a pivot.

This audit is not a pivot decision for the entire software build. It is a
reason to avoid spending implementation time on a generic robust/union
reformulation before the exact mathematical gap and data-validity chain are
established.
