# Tail-closed observability candidate: novelty falsification and evidence

**Date:** 29 October 2026\
**Status:** candidate remains mathematically interesting; novelty is **not supported**.\
**Scope:** model-only operator artifacts. No EEG/SEEG recordings, event labels, or outcome arrays were accessed.

## Question tested

Can the current tail-closed GBF selector be presented as a novel mathematical/computational contribution, or does it combine established detectability, robust subspace, and convex-separation ideas without a demonstrated advantage?

The candidate receives a whitened retained operator `B` and an omitted-source factor `D`. It seeks the largest retained coefficient subspace `V` such that every nonzero retained pattern `c` remains separated from every omitted-source explanation `z` satisfying `||z|| <= eta ||c||`:

```text
||B V c - D z|| > delta ||B V c||.
```

For a fixed `V`, a strict positive margin can be expressed with an S-lemma multiplier `t > 0`. The reduced matrix is

```text
F(t) = t B' (D D' + t I)^(-1) B - delta^2 B' B - t eta^2 I,
```

and `V' F(t) V` must be positive definite. The proposed frontier chooses the multiplier and reports the positive inertia of `F(t)` as an attainable subspace dimension. For the finite-mesh FEM tail, `D D'` is formed from the full prior-weighted sensor Gram minus the retained Gram.

This is not an observation-level hypothesis test, a probability of correct localization, or a source-recovery guarantee. It is a deterministic separation property under a particular forward operator, covariance whitening, source prior, norm budget, and finite mesh.

## Prior-art challenge

| Closest work | Actual overlap | What appears different here | Novelty consequence |
|---|---|---|---|
| Rezaei et al. (2020), RAMUS | Explicitly defines noise-thresholded detectable and undetectable source configurations, discusses a maximum detectable dimension, and uses coarse-to-fine source spaces to improve E/MEG reconstruction. | It focuses on detectability of configurations and reconstruction over randomized resolutions; the current selector asks for a retained subspace uniformly separated from a bounded competing source family. | The broad “maximum observable/detectable source dimension” framing is already present in EEG/MEG. A narrower adversarial-family distinction may remain, but must be shown to matter. |
| Kalogianni et al. (2018) | Defines EEG spatial resolution through source separability after whitening, with realistic noise and inverse-method comparisons. | Their experiment studies two dipoles and reconstruction accuracy; this selector imposes a universal coefficient-space guarantee against a bounded omitted family. | Distinguishability as a source-resolution concept is not new. |
| Gubner & Scharf (2004) | Constrained-subspace signal detection with additive infinite-dimensional interference/noise and an optional signal-energy constraint; derives a generalized likelihood-ratio receiver. | Here the selected object is a source-coordinate subspace and the output is a worst-case geometric margin/rank frontier, not a GLRT decision for a received sample. | Very close constrained-interference precedent. Full equation-level comparison remains unresolved because the full paper was not available in the inspected sources. No “first” claim is defensible. |
| Goldenshluger, Juditsky & Nemirovski (2015); Juditsky & Nemirovski (2019/2022) | Convex composite Gaussian testing and finite unions of convex signal sets; distance/separation between sets is central. | The current prototype reports a deterministic rank/margin design and does not implement their risk-controlled observation-level test. | The union/convex separation ingredients and any testing interpretation are prior art. |
| Foucart & Liao (2021/2022) | Deterministic optimal recovery from bounded inaccurate data under approximation assumptions; uses worst-case geometry and semidefinite methods. | Their target is an optimal recovery map/error, not this exact source-family rank selection. | Bounded-error recovery and S-procedure machinery are not new. Exact objective overlap requires continued scrutiny. |
| M/EEG resolution/fidelity work, including Hauk et al. (2021) | Resolution matrices, point-spread/cross-talk, localization error and spatial dispersion quantify how source maps are blurred or confused. | The candidate compares whole coefficient subspaces against a budgeted omitted-family adversary before choosing a reconstruction. | EEG-specific ambiguity and resolution are mature topics; superiority over matched metrics is not demonstrated. |
| GBF (2026), XDL-ESI (2024) | Existing source-imaging frameworks, with GBF already evaluated on relevant CCEP data and XDL-ESI addressing source extent. | The current code is a separate pre-inversion, operator-level audit. | An alternative output on the same data/model does not establish novelty. |

### 29 October update: Gubner–Scharf constrained-subspace precedent

A targeted follow-up search located an indexed copy of the full 2004 article, but the PDF host returned HTTP 403/429 to direct inspection. The accessible abstract and opening text establish the observation model `y(t)=a(t)+b(t)+n(t)`: a desired signal, an interference term known to lie in an infinite-dimensional subspace, and additive white Gaussian noise. The paper derives a generalized likelihood-ratio receiver for detecting a constrained desired signal and gives average error probabilities; an energy constraint may be imposed on the desired signal. The indexed copy confirms the title, venue, pages (2873–2879), and DOI.

This is close prior art for **constrained-subspace separation in the presence of interference**, so it blocks any broad claim that the S-lemma or an energy-bounded subspace/interference comparison is itself new. The currently available text does not establish that Gubner–Scharf optimizes the dimension of a retained source-coordinate subspace, constructs a uniform worst-case source-family separation frontier, or closes an omitted finite-mesh source tail. Those are possible differences in the *object being designed*, not proof of priority or usefulness. Because the article's equations and full derivation could not be inspected, the equation-level equivalence question remains **unresolved**; the candidate does not pass the prior-art distinctness gate.

Sources checked: [Gubner & Scharf (2004), DOI record](https://doi.org/10.1109/TIT.2004.836674); [indexed full-text PDF record](https://citeseerx.ist.psu.edu/document?doi=4820cabcea847c391b5f1745e1a660c6a5e065b5&repid=rep1&type=pdf). The indexed page was searchable, while opening/downloading the PDF was blocked by the host (403/429) during this review.

### Primary references inspected

- Rezaei et al., [Randomized Multiresolution Scanning in Focal and Fast E/MEG Sensing of Brain Activity with a Variable Depth](https://link.springer.com/article/10.1007/s10548-020-00755-8), especially the observation/detectability and coarse-to-fine sections.
- Kalogianni et al., [Spatial resolution for EEG source reconstruction](https://doi.org/10.1016/j.jneumeth.2018.02.016).
- Gubner & Scharf, [Detection of Constrained Subspace Signals in Additive Infinite-Dimensional Interference and Noise](https://doi.org/10.1109/TIT.2004.836674), DOI 10.1109/TIT.2004.836674. Available abstract/metadata confirms the constrained signal subspace, infinite-dimensional interference, and energy constraint; exact equation comparison remains open.
- Goldenshluger, Juditsky & Nemirovski, [Hypothesis Testing by Convex Optimization](https://doi.org/10.1214/15-EJS1054).
- Juditsky & Nemirovski, [Near-optimal estimation of linear functionals over unions of convex sets](https://doi.org/10.1093/imaiai/iaz011).
- Foucart & Liao, [Optimal Recovery from Inaccurate Data in Hilbert Spaces](https://arxiv.org/abs/2111.02601).
- Hauk et al., [Spatial fidelity of MEG/EEG source estimates](https://pmc.ncbi.nlm.nih.gov/articles/PMC7793168/).
- GBF, [Nature Biomedical Engineering (2026)](https://www.nature.com/articles/s41551-026-01664-0); XDL-ESI, [NeuroImage (2024)](https://doi.org/10.1016/j.neuroimage.2024.120802).

## What fresh verification established

I reran the existing independent checkers on the preserved model-only artifacts, writing new run folders rather than overwriting previous evidence:

1. **Full-tail frontier replay:** `research/gbf_omitted_activity_20261024/tail_closed_verification_004/result.json` reports `PASS_INDEPENDENT_TAIL_CLOSED_REPLAY`. It independently checked the finite-tail Gram factors, all 1,429 interval upper bounds for each of the nominal and error-inflated cases, and all positive-margin saved bases (28 nominal ranks and 25 robust ranks).
2. **Fixed-subspace decision replay:** `research/gbf_omitted_activity_20261024/decision_verification_003/result.json` reports `PASS_FIXED_SUBSPACE_DECISION_REPLAY`. It rechecked 12 matched cases at ranks 16 and 11. At rank 16 and a post-hoc 2% margin, the selected tail-closed subspace passes while sensor-SVD and bilateral low-mode baselines fail under this one declared model/prior. At rank 11 and a post-hoc 5% margin, the selected basis passes; sensor-SVD also passes, so the advantage is not universal.
3. **Full rank/margin sweep:** `research/gbf_omitted_activity_20261024/tail_closed_rank_margin_verification_002/result.json` reports `PASS_INDEPENDENT_RANK_MARGIN_REPLAY` for all 75 cases (three subspace families at each rank 1–25). The alternative verifier reconstructs a sensor-space factor from the competitor Gram and independently replays the scalar profile. Its first version rejected a valid but looser tangent upper bound by demanding the two upper bounds be numerically identical; verifier `_002` corrected that checker mistake and required interval overlap and lower-bound agreement. No underlying artifacts were changed.

The reproduced rank-16 result is a **retrospective model-representation choice**, not evidence of improved neural localization, a prospective researcher decision, or generalization. The selected ranks and thresholds were chosen after examining the frontier. The competitor uses the shifted FEM prior with `eta=1`; the Gram-error inflation is conditional and does not account for every numerical, basis, or anatomical uncertainty. Float64 matrix checks are not outward-rounded formal interval proofs.

The full sweep's largest ranks passing descriptive normalized-margin cuts were:

| Descriptive margin cut | Tail-closed selected | Bilateral low modes | Sensor-SVD |
|---:|---:|---:|---:|
| 1% | 18 | 0 | 16 |
| 2% | 16 | 0 | 14 |
| 5% | 11 | 0 | 11 |
| 10% | 8 | 0 | 8 |

These cuts are retrospective summaries, not calibrated detectability thresholds. The selected family optimizes this very margin, so its advantage over fixed low-mode and sensor-energy baselines is expected. The sweep makes the comparison less dependent on the earlier two selected rank/threshold pairs, but it does not fix the post-hoc design or turn the result into an independent decision test.

### Matched-comparator evidence and what it does not establish

The wider build already contains a separate matched baseline audit (`research/gbf_omitted_activity_20261024/BASELINE_RESULTS.md`) using the same model, retained/excluded families, coefficient budgets, dimensions, and thresholds for candidate, low-frequency, sensor-SVD, and zero-noise-cost selections. Its independent verifier reports `PASS` for 24 numerical cases (`baseline_verification_001/result.json`); failures of the fixed baselines have feasible replayed counterexamples, while ties are retained. The candidate is designed to maximize the very margin being compared, so this establishes that the criterion selects different subspaces on this operator, not a fair superiority result over a baseline optimized for the same objective.

The broader source-family audits likewise show a conditional assumption effect: direct single-point, uniform-patch, and flexible constrained fits can return different compatibility decisions on the same constructed fields (`MATCHED_FAMILY_DECISION_RESULTS_20261028.md`). These direct fits produce the same decisions as the family-audit interpretation. They demonstrate researcher-facing transparency about what the chosen family excludes; they do **not** show that the tail-closed subspace method improves on direct fitting or established resolution analysis. Neither comparison supplies prospective outcome validation, calibrated source priors, or an independent direct robust-subspace/convex-testing implementation with matched runtime and guarantee. Thus the smallest existing matched comparisons have been independently replayed, but the stronger novelty comparison has not been passed.

### Artifact hashes

```text
operator_grams.npz              D87D192D6DCA0ED731F81B41839C806D51F49285A85A5D13BEFCE78F4875A3A5
tail_closed_002/result.json     1316D3E033ABE599AEA19DD89169BE15B8E1112CC8D406D3FE9423C326877E22
frontier_evidence.npz           2487DBDABC86688E675CA86FB26959E1D1C7FA272E1654C0522EA3C34157AE51
verification_004/result.json   22ACCD4AADE177C8C551A23ABAC80ABFFE61CBD51E2085D9BA5A7CFAF260F395
decision_replay_003/result.json D5957BB43F26CF57F374234B6B832112AB8D416CEBB9147B2588C2033486883E
rank_sweep_001/result.json     50F7CF36BF41C196B575383CE6AB900CA01BC86BC4BCBCB3EC6FB976003B49B6
rank_sweep_001/evidence.npz    DDDFC78F35FACE94DE2421582EDB73B301BBE0A2C32146BDCEC15F423DD479FB
rank_sweep_verification_002/result.json AB5FE34A702E93CB00B404D192BB7A28CBC66B4ABCC8EE9B69533666D3F56507
rank_sweep_protocol.md         0E01A44227D16964A5D72C4C1A997A2F1DC95E2F747344E7A9D0BB5E53FB9482
rank_sweep_script.py           F82AFACAE0458BA4D9A11C41B600E10F01FFEA73521964AB5F7E0AB63CA1B001
rank_sweep_verifier.py         582A26D46760AEE161B3D786651349365E02C6B89E4FBE06568D374E80782586
```

## Falsification result and status

The current evidence does **not** establish a novel mathematical method:

- The S-lemma, Schur complement, inertia, Woodbury/resolvent identity, and matrix perturbation steps are established tools.
- The broad objective of measuring distinguishability/detectability and maximum observable dimension already has EEG/MEG precedent.
- The exact budgeted adversarial subspace objective may be a useful specialization, but no equation-level proof of priority or non-equivalence to robust constrained-subspace design has been completed.
- The only concrete baseline difference is post hoc and model-conditional; ordinary choice of threshold/rank could manufacture the displayed pass/fail split.
- No measured endogenous neural source event, prospective decision, or held-out researcher-use benefit supports the claim.
- Over the full rank range, the 5% and 10% passing-rank cut is tied with sensor-SVD; this weakens any broad practical-advantage narrative.

**Classification:** promising, technically reproducible operator-level software; **novel method unsupported**. No physiological source-recovery or frontier-advancement claim should be made from this result.

## Falsifiable claim and gate

**Candidate claim to test:** Given a declared finite-mesh EEG operator, retained GBF family, positive-semidefinite omitted-family Gram, coefficient budget `eta`, and relative discrepancy `delta`, the tail-closed selector returns the largest retained-subspace dimension for which every retained coefficient direction is separated from every allowed omitted-family explanation. It includes the entire declared finite-mesh tail rather than a user-chosen spectral cutoff.

This claim has a mathematical correctness component and a distinctness/usefulness component. The latter is not implied by the former.

| Gate | Pass criterion | Fail / pivot criterion | Current status |
|---|---|---|---|
| Correctness | Independent solver/replay matches direct constrained optimization on adversarial, degenerate, and real operator-Gram cases; all reported certificates include numerical-error control. | Any feasible counterexample violates a reported certificate, or crucial positive/negative decisions remain unresolved. | Partial: saved and fresh float64 replays pass; no outward-rounded proof, and this new sweep has a replayed numerical profile only. |
| Equation-level distinctness | Exact objective and guarantee cannot be reduced to an existing robust constrained-subspace detector, finite-union test, optimal-recovery result, EEG detectability criterion, or generalized-eigenvalue design after mapping assumptions and variables. | A prior method yields the same rank/margin frontier or the method is a reparameterization of established machinery without a new guarantee. | Not passed: Rezaei et al. already discuss detectable source sets and maximum detectable dimension; Gubner–Scharf full equation comparison remains unresolved; S-lemma and resolvent steps are standard. |
| Matched computational advantage | At the same answer, family, tolerance, and precision, an independent baseline cannot achieve the same certificate with comparable or lower cost; advantage must be measured on the existing operators and reproduced. | Direct fitting or a known robust-subspace/SDP solver yields the same frontier at comparable cost, or the current approach has no verified cost/tightness advantage. | Not tested against a generic direct SDP/robust-design implementation. |
| Decision value | A rank/representation decision is fixed before evaluation and changes in a justified way versus matched baselines; it must not depend on post-hoc thresholds. | The advantage appears only for a chosen rank/cut, or optimized baseline comparison is tautological and no separate decision follows. | Not passed: the full curve is retrospective; candidate is optimized for that curve; it ties sensor-SVD at 5% and 10% descriptive cuts. |
| Scientific interpretation | The source prior, coefficient budget, covariance, and forward-error set have a defensible interpretation for the intended EEG use. | The result is sensitive to arbitrary or uncalibrated prior choices and cannot be translated to a researcher action. | Not passed: full-tail prior is conditional, shifted-FEM parameterization and budget are not physiologically calibrated. |

**Overall pass rule:** a novel-method claim requires all five gates to pass. A software contribution may still be delivered if correctness passes while distinctness or decision-value gates fail, but it must not be labeled novel. Current outcome: **no novelty claim**; retain the tool as a conditional operator-level diagnostic pending a more decisive prior-art and computational comparison.

## Smallest decisive next step that needs no new dataset

Do not expand the method or add an ML model yet. Use the existing retained/tail operators to run a frozen, threshold-swept matched comparison against (i) the exact finite-dimensional constrained-subspace formulation in Gubner–Scharf if its full text can be obtained, (ii) generalized-eigenvalue/robust-subspace formulations, and (iii) direct constrained fitting as an answer-equivalence oracle. Predefine ranks and normalized margins before recomputation. Record whether the selector produces a nontrivial guarantee or computational cost/tightness advantage that those methods cannot reproduce. If the same rank/margin frontier follows from a known formulation, classify the result as a software contribution and stop the novelty claim. This can falsify a method claim without new recordings; it cannot establish biological validity.

If that method-level test finds no gap, the remaining route to a discovery without new data is a clearly bounded mathematical result about these already verified operators, with independent proof and a researcher decision that changes under a prospectively frozen rule. Existing one-model retrospective results do not yet meet that standard. If neither route survives, preserve the valuable build and report the negative novelty result honestly.

## Reproduction commands used

Commands were run from the research directory with the repository Python 3.12 environment. The verifier scripts consume only the approved operator Gram, saved scalar frontier, selected subspace evidence, and comparison report; they do not load EEG/SEEG sample arrays.

```powershell
python verify_tail_closed_certificate.py `
  --input implicit_tail_001/operator_grams.npz `
  --run tail_closed_002 `
  --output tail_closed_verification_004

python verify_decision_comparison.py `
  --grams implicit_tail_001/operator_grams.npz `
  --selection tail_closed_002/frontier_evidence.npz `
  --comparison decision_comparison_003/result.json `
  --out decision_verification_003

python run_tail_closed_rank_margin_sweep.py `
  --grams implicit_tail_001/operator_grams.npz `
  --selection tail_closed_002/frontier_evidence.npz `
  --out tail_closed_rank_margin_sweep_001

python verify_tail_closed_rank_margin_sweep.py `
  --grams implicit_tail_001/operator_grams.npz `
  --selection tail_closed_002/frontier_evidence.npz `
  --run tail_closed_rank_margin_sweep_001 `
  --out tail_closed_rank_margin_verification_002
```
