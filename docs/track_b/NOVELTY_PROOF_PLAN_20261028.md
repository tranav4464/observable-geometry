# Novelty proof plan: Observable Geometry

**Status:** prospective falsification plan; no novelty claim supported
**Signal access:** closed until the existing protocol and geometry gates pass
**Purpose:** define evidence that could support a distinct contribution, and
the outcomes that would reject it

**Gate-status clarification (29 October 2026):** the authoritative
`GATE_REGISTER.json` currently marks B4, B5, B6 and B7 **PIVOT**. The
evaluation below is a set of criteria for any formally reopened route; it is
not an active protocol, permission to inspect signal arrays, or evidence that
the candidate endpoint is feasible. The pinned curation-source audit in
`WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md` narrows the unresolved
geometry provenance but does not clear it. Reopening requires a reviewed
endpoint, protocol, geometry/forward-model validity, preprocessing contract
and explicit gate update before sample analysis.

## 1. What is already known

The overlap is unusually close and must be treated as a serious novelty threat.

* The 2026 GBF manuscript already analyzes the iES-CCEP high-density EEG data.
  It evaluates stimulation-site localization across 318 sessions from 35
  participants, comparing GBF with wMNE, eLORETA, sLORETA and LCMV. It also
  reconstructs and discusses N1/N2 response propagation. Its stimulation-site
  error endpoint uses the peak source estimate within ±5 ms of stimulation,
  while the propagation analysis uses later responses. Thus neither “apply
  GBFs to WSGZP” nor “compare EEG maps to the stimulation site” is a new
  contribution.
* The WSGZP data paper already reports paired hd-EEG/SEEG CCEP properties and
  explicitly identifies source-localization comparison as a use of the
  released data. EEG-to-SEEG concordance alone is therefore not a novelty
  claim.
* Spatial-fidelity metrics for point and patch estimates, multiple inverse
  methods, source-family priors, forward-model uncertainty, and set-valued or
  union-of-convex recovery all have substantial prior art. A family envelope,
  perturbation sweep, calibration wrapper, or new name is not novel by itself.

Primary sources: [Wang et al., GBF preprint, §§2.5 and 4.6](https://arxiv.org/html/2604.25592),
[Parmigiani et al. (2022), iES-CCEP dataset paper](https://doi.org/10.1016/j.brs.2022.04.007),
[Samuelsson et al. (2021), spatial-fidelity evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7793168/),
[Juditsky & Nemirovski (2019), recovery over unions of convex sets](https://arxiv.org/abs/1804.00355),
 [Bekri et al. (2025), robust recovery under operator uncertainty](https://arxiv.org/abs/2309.06563),
 [Juditsky & Nemirovski (2026), sparse linear-image recovery](https://arxiv.org/abs/2609.06182),
 [Stahlhut et al., forward-model uncertainty](https://www2.imm.dtu.dk/pubdb/pubs/6017-full.html),
and [Phee et al. (2026), MRI-informed EEG source imaging with conformal
uncertainty](https://doi.org/10.1016/j.cmpb.2026.109637).

### Equation- and endpoint-level overlap summary

| Prior work | What it already establishes | Exact remaining gap (not yet novelty) |
|---|---|---|
| GBF 2026, Eqs. 1–8 and iES §2.5 / Methods §4.6 | Represents cortical activity as `x=Aθ` using individual Laplace–Beltrami modes, then solves a Gaussian MAP inverse model `y=KAθ+ε`. On the same iES-CCEP resource, it compares focal peak-localization error against the intervention site across 318 sessions, using the peak estimate within ±5 ms of stimulation; it separately reconstructs and discusses later N1/N2 propagation. | It does not report a calibrated feasible range across competing source families and bounded forward uncertainty. This is a gap in that paper's reported analysis, not proof the combination is new or decision-useful. The ±5 ms target is stimulation-adjacent, not the proposed post-artifact late-CCEP endpoint. |
| Jiao et al. 2024, [XDL-ESI](https://doi.org/10.1016/j.neuroimage.2024.120802), Eqs. 1–13 and real-data §5.2 | Uses the same Parmigiani et al. simultaneous hd-EEG/SEEG stimulation cohort (36 patients), an FEM head model and 2,213 volumetric source cubes. It reconstructs averaged CCEPs, compares XDL-ESI with MNE, sLORETA, dSPM, LCMV, ADMM and ConvDip, and treats the stimulated contact as the localization reference. The real-data figure described in §5.2 shows Subj. 29 and the top five estimated dipoles; this is a qualitative single-participant illustration, not a cohort-level held-out metric. XDL-ESI learns spatial extents and allows test-time hyperparameter variation. | This directly threatens any claim based on source extent, flexible spatial maps, CCEP source imaging, or validation on WSGZP. Its reported endpoint is stimulation-site localization and displayed extent, not a calibrated feasible range over explicit competing families and forward uncertainty, nor a held-out comparison to sparse SEEG responses for later distributed CCEPs. This endpoint difference only motivates a controlled comparison; it does not establish novelty. Data availability is “on request”; code/data reproducibility must be checked before a matched benchmark is claimed. |
| Subramanian et al. 2025, [Scalp EEG predicts intracranial brain activity in humans](https://doi.org/10.1101/2025.04.07.647612) (bioRxiv preprint) | Uses simultaneous recordings from 20 Niguarda patients (1,918 bipolar SEEG contacts), 256-channel hd-EEG reduced to 19 local-Laplacian channels, and ridge/hierarchical regression on band-power time series. It reports leave-one-patient-out prediction in selected regions and, in 11 patients with 83 stimulated sites, correlations between resting scalp-to-SEEG regression weights and scalp CCEP maps (`r≈0.19–0.22`). This already combines scalp-to-intracranial prediction with stimulation-based spatial corroboration. | The paper predicts spectral SEEG features; its CCEP analysis correlates scalp regression-weight maps with scalp evoked maps. It does not construct a participant-specific forward-model source identified set over competing source families or certify ambiguity under bounded forward uncertainty. Therefore neither generic EEG-to-SEEG prediction nor a stimulation-response spatial-correlation check is novel. Patient-level overlap with WSGZP must be resolved before either cohort can be called independent. |
| Wen, Yang & Liu 2026, [Observability-Aligned Diffusion and Null-Space Completion for EEG Source Localization](https://arxiv.org/abs/2610.27461), posted 20 Oct 2026, Eqs. 1–19 | Explicitly decomposes cortical activity into lead-field row-space and null-space components. It refines the observable component with a diffusion prior and completes the null component using ridge plus a temporal residual network projected into the lead-field null space, preserving the predicted EEG. Its main benchmark is simulation-trained/evaluated; recorded-data demonstrations are exploratory, including one participant's 71-epoch spike average against one SEEG contact. The authors explicitly do not claim validated clinical localization or cross-subject generalization. | This is a direct, current threat to broad claims about “observability-aware EEG source reconstruction,” row/null decomposition, or making unobservable structure explicit. Its target is a prior-driven point reconstruction, not a measured-data compatible set over prespecified physiological source families and bounded operator uncertainty. That object difference is not itself novelty: any surviving claim must show a distinct mathematical guarantee or held-out decision advantage against this method where a fair comparison is possible. The preprint also states that null-space content is not verified by EEG, reinforcing the need to distinguish measurement-supported statements from prior-driven completion. |
| He et al. 2026, [Virtual iEEG from Scalp EEG: Charting the Landscape of Source Imaging, Intracranial Inference and Reconstruction](https://arxiv.org/abs/2608.26998), review posted 27 Aug 2026 | Provides a target-centred taxonomy separating source imaging from scalp-to-iEEG event inference, feature translation and waveform reconstruction, and distinguishes observability, predictability, identifiability, fidelity and utility. It calls for matched source-imaging baselines, uncertainty/abstention evaluation, independent paired data and incremental-utility tests. | This is a review rather than a source-family estimator, but it preempts presenting those distinctions or a validation checklist as our conceptual innovation. Our contribution must be a specific operational quantity/result and a demonstrated incremental decision value, not a new vocabulary for evidential limits. |
| Zauli et al. 2024, [localizing hidden interictal discharges with simultaneous hd-EEG/SEEG](https://doi.org/10.1016/j.jneumeth.2024.110193) | In eight patients, uses SEEG-marked IEDs to time-lock and average simultaneous scalp hd-EEG, then evaluates topographies and dSPM/LORETA source imaging against the intracranially observed event location; reports localization accuracy around 2 cm and releases a standardized dataset. This is direct measured-event source-localization validation. | It makes “use intracranial event labels to validate scalp source localization” an occupied task. The candidate could differ only through its explicit family-wise ambiguity/forward-uncertainty object and a demonstrated decision benefit, not through using SEEG-triggered scalp averages or another localization metric. This dataset may be a useful additional measured challenge, but it is not a substitute for the required WSGZP route and its protocol/access must be checked separately. |
| Yang et al. 2024, [spatial graph Fourier filters for source extents](https://doi.org/10.1186/s40708-024-00221-2), Eqs. 5–6 and real-data §3 | Projects classical ESI estimators into low-spatial-frequency graph subspaces to recover focal or extended source regions. Evaluates synthetic EEG cases and real visual-auditory MEG. | “Estimate source extent” or “use a spatially coherent region instead of a point” is already an established method objective. It does not supply a measured-data uncertainty set over competing source families or forward-model uncertainty, but those are remaining gaps to test rather than novelty by themselves. Include a matched GFT-based extent baseline where its assumptions and modality permit. |
| Parmigiani et al. 2022 WSGZP | Measures simultaneous hd-EEG/SEEG CCEPs in 36 patients and already quantifies cross-modal agreement: trial-to-trial reproducibility is reported for both modalities; scalp global-field-power versus percentage of SEEG-responsive contacts correlates at `r=0.592`; N1 and N2 amplitude correlations are `r=0.313` and `r=0.553`, respectively. It compares response amplitudes/latencies and stimulation factors, and explicitly proposes the release for source-localization comparisons. | Generic scalp-to-SEEG amplitude association, response detection, or condition-level concordance is already established. The paper does not establish a participant-held-out comparison of spatial reports across competing prespecified source families under bounded forward uncertainty. That gap is not proof of novelty; the proposed report must add a prospectively defined decision benefit beyond those published cross-modal measures and source-imaging baselines. |
| Srebro 1996, [An iterative approach to the solution of the inverse problem](https://doi.org/10.1016/0013-4694(95)00263-4) | Directly frames the bioelectric inverse problem as searching a noise-constrained feasible set for physiologically plausible solutions, using regularized inverses iteratively to restrict the search. It was tested in a model system using a digitized cadaver cortex in a three-shell spherical head replica. | This predates and preempts any “first feasible set of EEG source explanations under measurement noise” claim. The inspected abstract does not describe the proposed explicit union of modern source families, bounded participant-specific forward-operator uncertainty, calibrated decision rule or held-out CCEP evaluation. These differences are only candidate deltas; they require an exact full-text and equation comparison and a demonstrated decision benefit. |
| Wan et al. 2023, [Electrophysiological Brain Source Imaging via Combinatorial Search with Provable Optimality (ESI-A*)](https://ojs.aaai.org/index.php/AAAI/article/download/26471/26243), Eqs. 1–4 and search algorithm; [official code](https://github.com/ghwanlab/ESI-AStar) | Defines EEG/MEG source reconstruction as least-squares fit over a fixed-size active support, then searches connected candidate supports on the cortical mesh with an A*-style algorithm and an optimality guarantee. It reports simulated tests and real epilepsy EEG comparisons to resection/seizure-onset regions. | This preempts generic claims to optimal connected-source search or a graph-topology accelerator for one best patch. Unlike the proposed candidate, it returns a best fixed-size support and does not report a calibrated family-wise compatible set over continuous participant-specific forward uncertainty. A new robust-set algorithm would need to prove a distinct guarantee and benchmark against ESI-A* where a fair matched comparison is possible. |
| Samuelsson et al. 2021 spatial fidelity | Compares linear and nonlinear source estimators on distributed patch activations over measured resting-state noise, with spatial-fidelity metrics. | It does not use WSGZP measured late CCEP observations or the proposed participant-level ambiguity-report decision. Source-family/patch comparison and spatial-fidelity evaluation are already established concepts. |
| Juditsky & Nemirovski 2019 | Gives near-optimal recovery of linear and N-convex functionals under Gaussian indirect observations when the parameter lies in a finite union of convex sets. | Family unions and functional ranges over them are not new. Any claimed extra guarantee must be stated mathematically and shown not to be an instance of their framework or related convex testing results. |
| Skaf & Boyd 2010, exploring the suboptimal set | For convex problems, computes bounding boxes, diameter estimates and ellipsoidal approximations of the ε-suboptimal set using related convex programs; explicitly treats a large set as materially different parameter values that remain plausible in estimation. | A spatial range, spread, diameter or near-optimal ambiguity visualization is not new by itself. A possible delta must handle the declared structured nonconvex source/operator coupling with a verified advantage. |
| Bekri, Juditsky & Nemirovski 2025, robust indirect observations | Models an uncertain observation operator `A[η]=A+D[η]` and gives robust linear/polyhedral recovery-risk bounds for structured bounded operator uncertainty and convex signal sets. | A participant leadfield ensemble or structured forward perturbation alone is not new. A new result must add something beyond operator-robust recovery combined branchwise with finite-union methods. See `PRIOR_ART_OPERATOR_UNCERTAINTY_AUDIT_20261028.md`. |
| Juditsky & Nemirovski 2026 preprint, sparse linear-image recovery | Eqs. (1), (2), (7), §§4–6 and Propositions 4.2–4.3 treat sparse `Cx` under `ω=Ax+ξ`, recover linear functionals/images with `ℓ₁`/polyhedral estimates and risk bounds, and test sparse hypotheses with an undecided outcome. | Weakens generic spatial-linear-image, sparsity, risk-bound and abstention claims. It does not directly establish our topology-constrained continuous-leadfield problem; exact remaining delta needs a proof and comparator. See `PRIOR_ART_OPERATOR_UNCERTAINTY_AUDIT_20261028.md`. |
| Set-membership inverse methods and SESAMEEG 2024 | Set-inversion methods report feasible solution sets under measurement tolerances; Bayesian M/EEG methods explicitly quantify uncertainty and alternative source configurations rather than only one best map. | “Return a set of plausible sources” is not novel on its own. The proposed spatial-functional range must add an exact guarantee or a held-out decision advantage beyond these methods. See `PRIOR_ART_OPERATOR_UNCERTAINTY_AUDIT_20261028.md`. |
| Luria et al. 2024, [SESAMEEG](https://doi.org/10.3389/fnhum.2024.1359753), [official model documentation](https://pybees.github.io/sesameeg/explanation_algorithm.html) | Open-source Bayesian multi-dipole M/EEG software samples a posterior over source count, locations and strengths; it reports location probability maps, uncertainty, and multiple competing configurations when the posterior is ambiguous. The official model documentation states that multiple topographies can be fit when source count and locations remain fixed while moments vary over time; it allows free or cortical-normal orientations and assumes isotropic Gaussian noise in the documented likelihood. The paper notes that a weak dipole-strength prior can produce widespread reconstructions that mimic distributed sources, and lists explicit source extent with uncertainty and more detailed forward-error modeling as future work. | This is a close conceptual and operational comparator for a channel-by-time CCEP response. Neither multiple maps nor diffuse posterior support is novel. SESAMEEG's point-dipole posterior is not the same estimand as a deterministic feasible set over declared extended families and a bounded participant-specific operator set, but that object distinction is not itself a contribution. Any remaining delta must give a useful guarantee under those constraints, compare SESAMEEG on the same eligible observations, and show decision value; otherwise the candidate is a repackaging of uncertainty reporting plus known set-membership optimization. |
| Tong et al. 2025, [DeESI](https://doi.org/10.1109/TMI.2024.3506596), [full author-hosted paper](https://www.songxichen.com/Uploads/Files/Publication/Debiased_Estimation_and_Inference_for_SpatialTemporal_EEG_MEG_Source_Imaging.pdf), and [author code](https://github.com/tongpf/Debiased_EEGMEG_source_imaging) | The full paper reports a scaled rotated group Lasso (Eqs. 11–12), selected-support nuisance regression/debiasing (Eqs. 13–16), asymptotic covariance and chi-square-type testing under stated Gaussian/rank/sparsity conditions (Eqs. 17–18), plus PSF/CTF (Eq. 19). Its measured analysis uses seven simultaneous hdEEG/SEEG participants from **Localize-MI**, anonymous MRI, known stimulation locations, and a -2 to +2 ms post-average reconstruction window; it reports mean DLD 11.2 mm fixed orientation and 11.5 mm free orientation against 11 methods. The public repository remains an example-code simulation path, not a turnkey real-data reproduction. Detailed review: [`PRIOR_ART_DEESI_CODE_AUDIT_20261028.md`](PRIOR_ART_DEESI_CODE_AUDIT_20261028.md). | Strongly weakens generic claims to add sparse multi-source estimation, inferential uncertainty, PSF/CTF, or known-stimulation localization on Localize-MI, which this project reserves as a pulse-artifact control. DeESI did **not** analyze the separate 36-participant WSGZP/iES-CCEP resource. Our narrower candidate target is later post-artifact physiological CCEPs with sparse SEEG response evidence and explicit source-family/operator uncertainty. This is an estimand/dataset difference only; matched-baseline feasibility and added decision value remain unverified. |
| Hart, Polichtchouk & Dannhauer 2026, [robust transformer source localization](https://doi.org/10.1088/1741-2552/aeb82c) | The primary abstract states that the model is trained and evaluated on hundreds of thousands of simulated EEG measurements spanning noise, source count and electrode dropout, and compared with classical and deep-learning methods. It reports up to 12 mm lower mean localization error in a high-noise multi-source condition and says data/code will be made public. | This makes generic ML, multi-source estimation and robustness-to-missing-sensors novelty claims especially weak, while also showing why our required measured-data evidence matters: this study's reported test evidence is simulated, not held-out measured neural responses. It is not a measured WSGZP baseline, and its code/data are not yet available according to the abstract. Treat as prior art only; do not reproduce its synthetic benchmark under this project's evidence rules. If inspectable code appears, a comparison must use eligible measured data and a scientifically fair method-level endpoint. |
| Stahlhut et al. 2009/2011 forward uncertainty | Models effects of errors in conductivity, cortical surface and electrode locations; proposes a hierarchical Bayesian framework that jointly accounts for sources and forward model. | A perturbation ensemble alone is not new. A distinct robust certificate would need a new valid bound or an empirically useful decision advantage. |
| Phee et al. 2026 multimodal/conformal ESI | Official code at commit `ded88a361ad349cb5e93a07171a11772f791a0e5` predicts a single-dipole center and computes a scalar loss quantile from separately indexed simulated EEG examples. For MRI IDs held out from model fitting, it uses 200 additional examples per MRI ID and pools their losses into one cohort-level calibration threshold; the same held-out MRI IDs supply test examples. This is target-cohort-specific calibration, not zero-shot calibration for new anatomy. | The inspected repository computes and prints a threshold, but does not itself construct/export spatial regions. Its target is one dipole center, not a union of distributed source families across a forward-uncertainty set. This is a distinction in object and task, not proof of novelty. See `PRIOR_ART_PHEE_CODE_AUDIT_20261028.md`; independence of the indexed generated examples and the paper's full coverage construction still require review. The inspected primary test split is also created by `random_split` without a fixed generator. |

The only surviving empirical question is whether materially different,
physiologically defensible source families remain compatible with measured
late-CCEP scalp fields and whether that changes interpretation relative to
standard single-map or resolution outputs. This could be a new empirical
finding even if it uses established optimization. It is not automatically a
new method. For a method claim, exact direct constrained fitting over the same
families is an equivalence oracle: it should return the same identified set.
The method would need a validated guarantee or meaningful certified
complexity/tightness advantage over that oracle, not a different decision.

Participant-held-out evaluation on WSGZP would test within-cohort transfer;
it is not an independent-cohort replication because WSGZP has already been
used by the source-localization literature, including GBF and XDL-ESI. A claim
of cross-cohort generality requires an accessible, compatible external cohort
such as HDEEG-IED-SurgOutcome with its own geometry and independent source
reference. If that access is not granted, limit the finding to the measured
WSGZP derivative and do not describe it as externally replicated.

The formal reduction audit further narrows the mathematical gap. For fixed
forward instances and convex source-family branches, tolerance-compatible
sets are convex and finite branch/uncertainty unions reduce to established
constrained functional optimization followed by min/max aggregation. Only the
continuous joint source/operator case creates a nonconvex problem; a new
contribution would need a certified useful enclosure or a proven complexity
gain for that topology-constrained case, beyond robust operator estimation
and finite-union methods. A set-valued output alone is not enough. See
`PRIOR_ART_OPERATOR_UNCERTAINTY_AUDIT_20261028.md`.

## 2. The only live empirical novelty hypothesis

**Hypothesis:** for post-artifact late CCEP scalp fields, a focal GBF or other
single-map estimate can appear spatially decisive even when materially
different, prespecified source families remain compatible with the same
measured scalp field under a training-calibrated tolerance. An
uncertainty-aware family report may therefore change a predeclared reporting
decision from “report a focal location” to “report an unresolved spatial
range.” Under the current WSGZP release this is an in-observation
compatibility claim, not independent response prediction.

This is a hypothesis about **conditional observability and reporting**, not
proof of the true neural generator, complete source reconstruction, or a new
inverse-problem theorem. SEEG-responsive contacts are sparse positive
corroboration. The stimulation contact is an intervention site, and later
CCEPs are distributed responses; neither is complete source ground truth.

### Mathematical object to freeze

For participant `p`, let `Y_p` be the measured scalp response, `L_p(θ)` the
participant-specific lead field under a bounded uncertainty value
`θ ∈ U_p`, and `F_j` the `j`th prespecified source family. Let `ℓ_p` be the
fixed, noise-weighted in-observation residual and let `τ` be calibrated using
development participants only. The candidate compatible set is

```text
C_p(Y_p; τ) = union over j and θ in U_p of
               { X in F_j : ℓ_p(Y_p, L_p(θ) X) <= τ }.
```

For a prespecified spatial functional `h`, the report would show its range
over `C_p`, plus the surviving family labels and the response loss. An
“ambiguous” result means that this range is wider than a separately frozen
decision tolerance. This set-membership construction is **not claimed as
novel**; finite unions of feasible source families and functional ranges
over them have close prior art. The research must show that the exact
functional/guarantee is not already available and changes a useful measured
decision. `τ` controls compatibility with the chosen residual; it is
not a posterior probability, source-truth confidence, or guarantee of
physiological coverage. The loss, temporal covariance handling, amplitude
constraints, source-family parameterization, `h`, uncertainty set and
decision tolerance are all unresolved protocol choices and must be frozen
before signal access.

### Priority-map identifiability gate

The compatibility set is not a probability distribution and does not supply
a unique ranking of locations. Do not rank candidate locations by how often
an optimizer, mesh enumeration or random sampler returns them; those counts
depend on parameterization and sampling density. Before using SEEG contact
capture as a researcher-decision endpoint, define and freeze a deterministic
map from the full set to an at-most-fixed-area shortlist. One conservative
candidate is the pointwise guaranteed activity

```text
g_p(v) = inf { ||X(v, :)||_2 : (j, θ, X) belongs to C_p(Y_p; τ) },
```

when `C_p` is nonempty; when it is empty the report is `UNSUPPORTED` and no
priority map is formed. Here `X(v, :)` is the reconstructed source time course
at cortical vertex `v`. A shortlist could rank vertices by `g_p(v)`, include
only vertices whose certified lower bound exceeds a prespecified activity
floor, and stop at a frozen area budget using cortical area weights. If the
eligible region is empty or too small, the procedure abstains. This candidate
requires a common physical amplitude scale across families, a defensible
activity floor, continuous/numerical lower-bound error control, and an
explicit penalty or coverage rule for abstention. For a fixed forward model
and convex source-family branch, each `g_p(v)` is an ordinary constrained
convex optimization problem (an SOCP for the stated norm residual and norm
objective); taking the minimum across branches is standard finite-union
optimization. The continuous operator case adds source/operator coupling but
does not make this score novel by itself. It is **not yet selected or
validated**. If these requirements cannot be met, keep the certificate as an
unranked compatibility report and do not claim improved follow-up
prioritization. Any alternative map must meet the same prespecification and
anti-sampling-bias requirements.

Candidate point, coherent-patch, multi-patch, smooth and signed-distributed
parameterizations now have a literature-based rationale and explicit claim
limits in `SOURCE_FAMILY_PHYSIOLOGY_REVIEW_20261028.md`. That review does not
validate the families for WSGZP CCEPs. In particular, the flexible signed
family remains an adversarial model unless additional evidence justifies its
within-patch sign freedom; all alternatives remain unfrozen pending the
protocol and geometry gates.

## 3. How to try to prove it

### Gate A — exact prior-art delta

Before method implementation, make a line-by-line equation and endpoint table
for GBF, its WSGZP analysis, the WSGZP data paper, PSF/CTF and empirical
spatial-fidelity methods, patch/sparse inverse methods, robust forward-model
methods, and set-membership/conformal uncertainty methods. For each, record:

1. observed data and target;
2. source family and uncertainty assumptions;
3. optimization or inference object;
4. guarantee or calibration claim;
5. metric and researcher decision;
6. cohort and evaluation split.

**Pass condition:** identify a precise output or result absent from close work.
If the only delta is testing known methods on a known dataset, call it a
replication/extension, not a novel method.

### Gate B — predeclare a meaningful observable

Freeze a single spatial statement, such as the range of cortical parcels that
remain compatible with the measured scalp response across accepted source
families and forward-model uncertainty. Define how cortical area/volume is
matched; do not use an undefined “matched volume” for surface sources.

Define “compatible” using a tolerance calibrated only on development
participants and applied to the held-out participant's measured scalp response
as the inference input. Unless independent repetitions and a permissible
split are documented, this is an in-observation compatibility fit, not
held-out scalp-response prediction. Report fit residual and set size
separately. Do not call that tolerance a probability that a source is true.

### Gate C — held-out matched comparison

After the protocol, geometry, preprocessing and access gates pass, use
participant-grouped outer folds. Compare the proposed report with GBF,
XDL-ESI, SESAMEEG where its source model can be matched, DeESI using its full
paper methods and measured endpoint where a fair reimplementation is feasible,
ESI-A* as a best fixed-size connected-support comparator (not a same-estimand
identified-set baseline), graph-Fourier source-extent methods where applicable, direct
constrained fits for the same families, matched patch methods, MNE, dSPM,
eLORETA, LCMV, and appropriate PSF/CTF or empirical fidelity outputs.
The 2026 robust transformer is a literature-only prior-art reference here; its
synthetic benchmark must not be reproduced under this project's evidence
rules, and it cannot stand in for a measured-data comparator.
Use the same lead field, channels, reference, covariance, response window,
uncertainty scenarios, spatial budget, and tuning information wherever the
methods permit. Include prestimulus, shifted-condition and held-out
stimulation-contact controls specified before outcome access.

Measure (a) the stability of the spatial statement across frozen family and
forward scenarios, and (b) overlap with sampled positive SEEG-responsive
contacts at a predeclared matched cortical area, with implant-sampling and
stimulation-distance controls. This is sparse positive concordance, not
source truth. Add held-out scalp-response prediction only if independent
same-condition repetitions and their permissible split are authoritatively
documented before analysis; the current v4 amendment does not provide that
split. A metadata-only inventory now identifies two candidate same-condition
run-table pairs (sub-14 runs 01/02 and sub-36 runs 06/07). The public
repository does not establish which numbering helper produced the released
run-ID mapping, so chronology, session identity, and independence remain
unknown. The release also lacks run spacing, preprocessing-independence
provenance, and event matching. These two participants are insufficient for a
confirmatory repeatability endpoint. Ask the dataset custodians to resolve the
run provenance before considering an EEG-only repeatability analysis. Report
participant-level intervals and per-participant outcomes. Do not infer SEEG
specificity or true-source sensitivity from unobserved cortex.

An additional paper-to-derivative eligibility discrepancy must be resolved:
Parmigiani et al. report 30/40 trials per session and retention of 323/379
sessions after excluding 47 sessions with fewer than 25 retained trials (and
nine with evoked epileptic spikes). Released sub-36/run-06 contains only 13
EEG and 15 iEEG epoch rows. Its inclusion in the paper's retained set and the
meaning of these counts are unknown, so exclude sub-36 runs 06/07 from a
paper-matched repeat test unless an authoritative selection/trial-count
mapping resolves this. Sub-14 runs 01/02 exceed 25 rows in both modalities,
but remain an unverified candidate pair. This discrepancy is recorded in
`WSGZP_REPEAT_RUN_FEASIBILITY_20261028.md` and the custodian query; it does not
change the no-signal-access gate. The public OSF file index contains no
selection table, run map or event-index crosswalk, so this cannot be resolved
from the currently indexed public files. See
`WSGZP_PUBLIC_FILE_INDEX_AUDIT_20261029.md` and its JSON record. The
custodian query remains an unsent draft.

### Gate D — decision value and independent replay

Before evaluation, write the exact researcher action being assessed, such as
whether a focal label is withheld when a broader source family remains
compatible. For an empirical claim, compare the frozen report with GBF,
XDL-ESI, SESAMEEG, graph-Fourier extent methods where applicable, MNE-family,
patch and resolution outputs on held-out participants, and test its
predeclared external criterion at matched cortical area. Implement SESAMEEG
on the same eligible run-condition inputs if a defensible match is possible;
otherwise document the exact source-model or temporal-estimand mismatch and
do not imply it was beaten. For a new
algorithm claim, compare the same certified object against exhaustive direct
constrained fitting: agreement is expected, and the contribution must be a
proved guarantee or meaningful certified runtime/tightness advantage.
Independently replay the certificate and participant-level summaries from
frozen outputs.

**Pass condition:** an empirical finding must be replicated across held-out
participants, survive the frozen source-family and forward-model sensitivity
analysis, and not be explained by the matched single-map/resolution baselines.
A method claim additionally needs a valid theorem or certified computational
advantage over the direct-fit oracle. A visually richer map or smaller
in-sample residual is not a decision advantage.

### Conditions that make the endpoint interpretable

* For cortical-surface source families, match predicted **cortical area**.
  “Matched volume” needs an independently fixed 3-D thickness/dilation rule.
* Freeze how bipolar SEEG channel coordinates are assigned (including
  midpoint convention), which contacts are eligible, the response detector,
  multiplicity handling, minimum valid trials, time/frequency band, and the
  baseline/unit contract. Scalp and SEEG bandwidths differ, so not every SEEG
  response is necessarily observable in the scalp endpoint.
* Account for implantation sampling: prespecify shaft/region weights and
  geometry/stimulation-distance controls or spatial nulls that preserve depth
  and sampling density. Otherwise overlap can reward where electrodes were
  implanted rather than spatial validity.
* Freeze each held-out spatial report from permitted scalp/anatomy inputs
  before opening that participant's SEEG response labels. Give all comparators
  the same permitted information.
* Preserve the full compatible set if the output is called a certificate.
  Trimming it to a fixed area budget can discard compatible explanations and
  invalidate an “all plausible sources” guarantee. If only a ranked subset is
  shown, call it a prioritization report, not a certificate.
* Treat responsive bipolar SEEG locations as sparse positive concordance.
  Their coordinate is not necessarily the generator, and unresponsive or
  unsampled cortex is not a true negative.

Positive-contact capture is the candidate primary external endpoint for the
narrow researcher action of prioritizing a limited cortical area for follow-up.
It is too weak to establish whole-cortex observability, source truth, or
method novelty on its own. The WSGZP paper explicitly identifies
source-localization comparison as a follow-up use; the precise matched-area
family-audit endpoint was not found in inspected GBF/WSGZP methods, but that
difference alone is an endpoint distinction, not method novelty.

## 4. What can count as novelty

### Evidence classes must not be conflated

The available WSGZP measurements can support a participant-held-out
**conditional-ambiguity** analysis and sparse external concordance, but they
do not currently provide complete ground truth for later distributed CCEP
generators. The stimulation contact
is the intervention site, not necessarily the later response generator;
responsive SEEG contacts are sparse positives, and nonresponsive or
unsampled cortex is not a verified negative. Therefore the WSGZP endpoint
cannot, by itself, estimate a false-confident-source-attribution rate or
true-source coverage. Those claims require an independently defensible
source reference and an evaluation design that does not use that reference to
construct the report.

Use three separate labels for results:

1. **Measured compatibility:** two or more prespecified source families fit
   the held-out participant's measured scalp field within a frozen tolerance.
   Without an independent same-condition repeat, this is in-observation
   compatibility, not a prediction test. It establishes compatibility with
   the tested measurement and model, not that each family generated the
   response.
2. **Sampled-contact concordance:** a scalp-derived report, frozen before
   opening held-out SEEG response labels, overlaps
   responsive SEEG bipolar contacts under a frozen spatial budget. This is
   sparse positive corroboration, not source truth or whole-cortex accuracy.
3. **Source-recovery accuracy or false-confident attribution:** allowed only
   if a suitable independent neural source reference, with known limitations,
   exists for the evaluated events. Do not infer it from labels 1 or 2.

This distinction is a hard claim boundary, not a wording preference. If no
adequate source reference exists, remove false-attribution and true-source
coverage claims from the novelty criterion.

### New method supported

Requires both:

1. a specific mathematical or algorithmic step not present in the closest
   methods, with a correct proof or independently replayable guarantee under
   the declared source families and forward uncertainty; and
2. a proved or independently replayable advantage over the appropriate
   comparator. Against direct constrained fitting of the exact same object,
   the output should agree; require a certified runtime/tightness gain or a
   stronger guarantee. Against GBF, resolution/patch and calibrated
   uncertainty baselines, require a predeclared held-out researcher-decision
   advantage or a guarantee they do not provide.

The advantage must match the evidence class. WSGZP alone may show that a
source-family ambiguity report changes interpretation relative to single-map
outputs, or improves a separately defined sparse sampled-contact concordance
endpoint on held-out participants. It may not be described as reducing
false source attribution unless an independent source reference supports
that calculation. A theorem alone is not enough to claim practical advantage;
the result must also matter for a stated researcher decision.

If the mathematics reduces to known constrained fitting, robust feasibility,
Gaussian testing, PSF/CTF, a set-valued wrapper, or ordinary calibration, this
classification fails.

### New empirical finding, not a new method

Could be supported if the prespecified family-dependent ambiguity effect is
replicated across held-out participants, survives forward/preprocessing
sensitivity checks, changes the planned source-reporting decision, and is not
already shown by the close GBF/CCEP studies. It must be described narrowly as
a finding about the tested CCEP responses, source families and released
derivative. WSGZP alone cannot validate a whole-brain true-source map; an
independent cohort would materially strengthen the claim.

The primary evidence is a participant-held-out analysis in which the measured
scalp response is the inference input and the family ambiguity is assessed
under the frozen model; this is not independent scalp prediction. A
predeclared scalp-report to sparse-positive-SEEG concordance outcome can test
external decision value, with explicit sampling limits. Claim repeatability
only if valid independent same-condition repetitions and a permissible split
are documented. Do not call these endpoints proof that an inferred family
contains the biological generator.

### Validated software contribution or pivot

If the report agrees with direct fitting and established methods, if family
assumptions cannot be defended, if the effect vanishes under held-out
evaluation, or if available data cannot validate the decision, stop the
novelty claim. Preserve the tool and report its bounded contribution, or
pivot the scientific target. Do not keep adding metrics to manufacture a
novelty narrative.

### Calibration target audit (29 October 2026)

“Calibrated” must name the target. The WSGZP route has no complete spatial
label for the generator of a later distributed CCEP: stimulation contacts
mark the intervention and responsive SEEG contacts are sparse positives.
Those observations cannot calibrate whole-cortex source-set coverage or the
correctness of the `unique enough / ambiguous / unsupported` label. Conformal
coverage requires calibration examples carrying the target being covered and
a justified exchangeability unit; see
`CALIBRATION_IDENTIFIABILITY_AUDIT_20261029.md` and the primary task-driven
conformal inverse-problem formulation linked there.

Until a valid null distribution or independent null-calibration design is
specified for the residual after optimizing over source families, parameters
and forward uncertainty, use **prespecified fit tolerance**, not a calibrated
false-rejection rate. The possible WSGZP external endpoint is separately
**held-out sampled-positive-contact capture at fixed area**. It can test a
bounded follow-up-prioritization yield; it cannot establish source truth,
whole-cortex coverage, specificity, false-negative rate or calibrated
ambiguity. This correction neither opens signal access nor relaxes the
matched-baseline novelty criterion.

### Measured source-reference screen (29 October 2026)

The public-data check found no currently reviewed route that simultaneously
provides endogenous neural events, verified participant-specific scalp
forward geometry, and a sufficiently complete event-matched spatial source
reference. WSGZP remains the primary CCEP route but its intervention site and
sparse responsive SEEG contacts do not label the later full generator.
HDEEG-IED-SurgOutcome supplies MRI, high-density EEG and surgical outcome, but
the latter is an indirect clinical proxy, access is unresolved, and the
cohort is already listed in the 2026 GBF study. The newly accessible NEMAR
`nm000513` release has measured endogenous spike-centred scalp EEG/SEEG, but
its released SEEG contacts have no coordinates and the same seven-patient
cohort was already analyzed by Koessler et al. and Ternisien et al. It cannot
serve as an independent spatial validation cohort as released. Details and
sources are in `MEASURED_SOURCE_REFERENCE_DATASET_REVIEW_20261029.md`.

This narrows the scientifically supportable WSGZP endpoint to model-
conditional compatibility plus, separately, sampled-positive-contact
prioritization utility. Neither supplies source-truth calibration. Do not
silently replace the requested validation target with this weaker endpoint;
state the claim limit and keep seeking a valid reference if source coverage is
required.

## 5. Current blockers and immediate next work

No signal-level novelty test is authorized or complete. The WSGZP protocol is
unlocked; geometry/forward-model validity is unresolved; the released-array
baseline and SEEG scaling semantics are unresolved; the coordinate audit
flagged a participant requiring adjudication; and HDEEG access is unavailable.
The GBF article has already used WSGZP, so it is not an untouched external
cohort for a newly formulated claim. HDEEG access remains unavailable; do not
make claims about its prior use or suitability until its status is verified.

The current operational design is now aligned with proposed amendment v4:
participant-grouped evaluation of per-run-condition scalp averages followed by
sparse positive SEEG-contact concordance. The previous event-row split-half
scalp-prediction endpoint is withdrawn unless independent acquisition,
event-mapping and preprocessing provenance is provided. Repeatability is a
conditional follow-up and the sub-36 repeated-condition pair is excluded
pending reconciliation with the paper's trial-count selection rule. Complete
the exact matched-baseline decision audit and close coordinate/forward,
preprocessing-scale and endpoint gates before signal access or fitting. The
protocol remains unlocked.

## 6. Decision rule

The current classification is **PROMISING BUT UNVERIFIED** as a research
direction and **NOVELTY NOT ESTABLISHED**. The candidate proceeds only if Gates
A and B produce a precise, non-duplicative, measurable claim. The novelty
claim is falsified if Gate C shows equivalent decisions or Gate D shows no
incremental decision value. The project remains useful if it ends as a
validated software contribution, but that is a different outcome from a novel
method or scientific discovery.

## 7. Operational test for a possible empirical contribution

The current primary test is **not** split-half scalp prediction or test-retest.
Amendment v4 uses each released run-condition's available trials to form a
single scalp response estimate and keeps each participant wholly in one outer
fold. Separate two claims that could otherwise be conflated: (i) whether the
set-valued report correctly implements its declared model-conditional
compatibility and ambiguity rules, which is assessed by proof, numerical
replay, and the forward-uncertainty contract; and (ii) whether a frozen,
fixed-area spatial shortlist derived from that report captures more sparse
positive SEEG contacts than matched single-map/extent baselines. The latter
tests a bounded research-prioritization use, not correctness of the
unique/ambiguous/unsupported label or source recovery. It is conditional on
the processed derivative, not independent scalp prediction or event-level
EEG-SEEG validation.

### Primary evaluation unit and endpoint

Use participant-grouped outer folds. Train or calibrate all global thresholds
using only the outer-training participants. Calibration may set a measurement-
noise/residual compatibility tolerance, but the available data do not support
calibrating spatial coverage or the ambiguity label against the true
whole-cortex generator. Do not report a probability that the biological source
lies in the set. For each held-out participant,
form one scalp response per eligible run-condition using the frozen channel,
reference, baseline, artifact and time-window rules. Fit the predeclared
point, uniform-patch, smooth-patch, signed-distributed, multi-patch and
flexible-constrained families under the verified participant-specific model.
Serialize the spatial report and the decision (unique enough, ambiguous or
unsupported) before revealing the corresponding SEEG response summaries.
Participant-specific anatomy and outcome-blind forward construction may be
test-time inputs only under the frozen protocol.

The candidate external endpoint is positive-contact capture by a prespecified
fixed-area priority map derived from the compatibility report, with
participant-macro uncertainty and controls for implantation density, region,
and distance from the stimulation pair. Freeze how abstentions are handled and
the allowed abstention budget; retain every eligible held-out run-condition in
the denominator so a method cannot improve capture by silently dropping hard
cases. Keep the **full compatible set** intact for certificate claims; do not
clip it to the area budget. Score a separate priority map against matched-area
outputs from GBF, direct fitting, patch and resolution methods. This endpoint
can measure sampled-positive yield only; it cannot provide specificity,
false-negative rate, source truth, or calibration of the ambiguity decision.
The unit of cross-modal
comparison is the **run-condition**, not the trial: the released metadata do
not provide event IDs or prove EEG-SEEG epoch correspondence. Use only
run-condition EEG and SEEG summaries, and never pair rows by index. The
stimulation pair is an intervention location, not ground truth for the later
CCEP generator. Responsive SEEG contacts are sparse positive observations;
nonresponsive or unsampled cortex is not a verified negative. Therefore this
endpoint is concordance, not source truth, sensitivity, specificity, or a
false-attribution rate.

Compare the compatibility report and the separately derived priority map with
GBF, direct constrained fitting, XDL-ESI, SESAMEEG, applicable graph-Fourier
and patch methods, and matched PSF/CTF or empirical spatial-fidelity metrics.
SESAMEEG is an active comparator, not an optional citation: it accepts
multiple topographies under a fixed source-count/location assumption, so the
frozen channel-by-time response is a plausible matched input. Use the same
outcome-blind forward solution and sensor subspace; prewhiten data and
leadfields consistently if needed to align its documented isotropic Gaussian
noise likelihood with the frozen covariance metric. Freeze its source-count,
orientation, noise, prior, particle-count and stopping settings using only
training participants; report Monte Carlo stability. Derive an equal-area
ranking from weighted posterior source-inclusion mass across source-count
particles, rather than comparing only its MAP dipoles to a full compatibility
set. If the maintained package does not expose weighted particles, verify an
adapter against its saved posterior output before use. Treat repeated runs
over forward perturbations as an ensemble sensitivity analysis, not as a
continuous robust guarantee. If a specific preprocessing, source-grid or
temporal assumption prevents fair execution, document and justify that
mismatch before outcomes are opened. Give methods the same permitted
scalp/anatomy inputs, held-out participants, target window and priority-map
area budget. Do not describe matched area as making a complete set-valued
certificate and a ranked map equivalent objects. A possible
researcher action is to choose a limited region for follow-up validation; the
test can ask whether the certificate-derived shortlist yields more responsive
sampled contacts at the same area than the baselines. It cannot establish
whether withholding a focal claim was objectively correct. Any empirical
novelty claim requires a predeclared advantage beyond those matched baselines
and must stay within the positive-contact evidence class. If that advantage
does not appear, this route does not support novelty.

### Repeatability is conditional follow-up only

The metadata-only screen found two same-condition run-table pairs, but the
public run map, event mapping and acquisition/preprocessing independence are
not established. The public OSF file index contains only the multipart BIDS
archive and `eeg_badtrials.json`; it has no run chronology, event-index or
379-to-323 selection table. The publication's stated exclusion of sessions
with fewer than 25 retained trials also conflicts with sub-36/run-06's 13 EEG
and 15 SEEG epoch rows. Sub-36 runs 06/07 must therefore be excluded from a
paper-matched repeatability test unless the discrepancy is authoritatively
reconciled. Sub-14 runs 01/02 pass the simple count screen, but remain an
unverified candidate pair. See `WSGZP_REPEAT_RUN_FEASIBILITY_20261028.md`,
`WSGZP_PUBLIC_FILE_INDEX_AUDIT_20261029.md`, and the machine-readable paper
and OSF file-index audits.

Do not split event rows or claim held-out scalp prediction from a single
run-condition average. A repeatability or scalp prediction endpoint can be
added only after custodians establish independent acquisitions, event
membership/non-overlap and preprocessing dependencies, and the protocol
specifies a valid independent measurement split. Even then, run-average
repeatability is conditional on the released preprocessing unless the raw
pipeline can be rerun separately within each split. If that evidence is not
obtained, report repeatability as unavailable; it is not a blocker to the
separate participant-held-out sparse-contact concordance endpoint.

### Freeze and falsification

Before opening confirmatory signals or held-out SEEG outcomes, freeze:

1. Participant folds, participant exclusions, eligible run-conditions, the
   source families and the verified forward-model/uncertainty contract.
2. One response window, channel/reference/baseline rules, covariance and
   calibration method, spatial support functional, area budget and
   unique/ambiguous/unsupported thresholds.
3. Matched baseline implementations and tuning budgets, participant-macro
   metric and confidence interval, implant-sampling and stimulation-distance
   controls, and measured negative controls (including prestimulus and
   shifted-condition controls where meaningful).
4. One researcher action and its decision threshold, a minimum effect that
   would change that action, and the stopping rule if matched methods agree.

The claim fails if family constraints cannot be defended physiologically,
forward or preprocessing sensitivity explains the result, sparse-contact
concordance does not improve beyond matched methods, the confidence interval
includes no meaningful gain, or the endpoint cannot be computed independently
of report construction. A positive result supports only the declared
source-family and sampled-contact claim on the processed WSGZP derivative. It
does not establish a complete neural source map. A new-method claim additionally
requires a distinct mathematical step, proof under the declared families and
uncertainty, independent numerical replay, and advantage over direct
constrained fitting of the same object. Otherwise classify the result as a
new empirical finding, validated software contribution, or pivot, as the
evidence warrants.

## 8. Proof-feasibility decision after the WSGZP provenance audit

The downloaded archive's package license is now documented as CC BY-NC-SA 4.0
(`DATA_ACCESS_STATUS_20261028.md`). This resolves the earlier package-license
uncertainty, but does not establish that a novelty claim is testable.

The current WSGZP release does **not yet support the planned decisive test**:

* The stimulation contact is known, but it is not ground truth for the
  generator of a later distributed CCEP. GBF already reports stimulation-site
  localization on this data route, so repeating that result cannot establish
  novelty.
* Run-level SEEG-positive contacts could provide sparse corroboration for a
  scalp-derived spatial report. Because unrecorded and nonresponsive cortex
  are not verified negatives, this alone cannot estimate false-confident
  attribution, true-source coverage, or whole-cortex recovery.
* EEG and SEEG epoch counts differ in most runs and no shared event identifier
  or onset is released. A metadata-only scan found two exact same-condition
  run pairs (sub-14 runs 01/02; sub-36 runs 06/07), but cannot establish
  independent acquisition or preprocessing. These do not authorize a
  repeatability claim. The paper reports that sessions with fewer than 25
  retained trials were excluded, but sub-36/run-06 has only 13 EEG and 15
  iEEG rows. Until reconciled, that pair is ineligible for a paper-matched
  repeat analysis; sub-14 is the sole remaining row-count-eligible candidate
  and is still not proven independent. The bad-trial mask matches exported EEG epoch counts
  in 317/323 runs, but its semantics and ordering are undocumented and six
  runs disagree. This also prevents establishing a cross-modal trial match.
* The participant-level split inventory is valid metadata evidence, but
  coordinate/forward-model validity and the released-array preprocessing and
  scaling contracts remain open. The confirmatory protocol is still
  `UNLOCKED`.

Therefore, **do not fit or score the proposed certificate on WSGZP yet**. The
only empirically defensible next step is to establish whether a frozen
participant-held-out, run-condition endpoint is useful and independently
auditable. If using sparse SEEG-positive concordance, predefine spatial
coverage/volume and compare against matched GBF, direct constrained fitting,
patch and resolution baselines; label it corroboration, not source truth. If
using repeatability, first obtain authoritative event mapping, non-overlap,
and preprocessing-fit provenance. If neither endpoint can distinguish the
candidate from existing methods, stop the novelty claim.

The evidence threshold for **NOVEL METHOD SUPPORTED** remains conjunctive:

1. A precisely stated mathematical/algorithmic step is not equivalent to the
   closest prior method under the same assumptions.
2. Its guarantee is proved for the declared source families and bounded
   forward uncertainty, and independently replayed with numerical error
   accounted for.
3. A preregistered, participant-held-out measured-data comparison shows a
   predeclared decision-relevant advantage over GBF and the strongest
   applicable resolution/patch/uncertainty baseline, with uncertainty
   excluding no improvement. For the same identified set, direct constrained
   fitting is an answer-equivalence oracle; method novelty requires an
   independently replayed guarantee or certified computational advantage
   over it, not a different decision.
4. The endpoint independently supports the exact claim. Prediction,
   repeatability, sparse SEEG concordance and true-source recovery are
   separate evidence classes and cannot be substituted for one another.

Failure of item 1 rejects method novelty. Failure of item 3 rejects practical
advantage. Failure of item 4 narrows the claim or invalidates the test. A
positive result on only one item is not enough. Until this chain is met, the
current result remains **NOVELTY NOT ESTABLISHED**; the archive download and
metadata work change access feasibility, not that conclusion.

## 9. Decision-endpoint logic check (29 October 2026)

An adversarial endpoint review identified a distinction that must remain
explicit in any reopened protocol. The proposed analysis produces two
different objects, and the available WSGZP labels can evaluate only one of
them:

1. **Full compatibility report.** This is the set/range of source-family
   explanations satisfying the declared residual and forward-model
   assumptions. It must retain the full compatible set and report its
   numerical/model limits. Sparse responsive SEEG contacts cannot establish
   whether this set contains the true generator, whether its support is
   complete, or whether `unique enough / ambiguous / unsupported` is a correct
   label. Direct constrained fitting of the same mathematical object remains
   the answer-equivalence oracle.
2. **Fixed-area priority map.** A separately frozen rule may turn the report
   into a ranked cortical shortlist for follow-up investigation. At a matched
   area budget, this map can be evaluated for capture of sampled responsive
   SEEG contacts. This tests positive-contact prioritization yield only. It
   supplies neither verified negatives nor a source-truth calibration target.

Therefore, a better positive-contact capture score does **not** validate the
ambiguity label or prove lower false-confident source attribution. If this
route is reopened, the researcher action must be stated narrowly, such as
choosing a fixed-area region for follow-up sampling or abstaining under a
predeclared cost rule. Keep every eligible held-out run-condition, including
abstentions, in the denominator; fix the abstention budget; and compare
against matched-area GBF, direct-fit, patch, resolution and suitable ensemble
maps. Use nested participant-grouped tuning and participant-level paired
uncertainty, with controls for implant density, shaft, region, depth,
stimulation distance and leadfield sensitivity. Report positive-contact
capture as such; do not call it sensitivity, specificity, whole-cortex
coverage, or source recovery.

This narrower utility result could support a **measured empirical finding**
if it is independently reproducible and materially improves a predeclared
follow-up decision over the matched baselines. It does not by itself support
a **novel method**. Method novelty still requires a non-equivalent
mathematical guarantee or a certified computational advantage over direct
fitting of the same object, plus valid measured-data evidence. Equivalent
decisions, a gain explained by map combination or changed spatial spread, or
a gain removed by the sampling/preprocessing/geometry controls rejects the
novelty claim.

**Current status remains unchanged:** this is a protocol-logic correction,
not a signal result or authorization. WSGZP participant geometry, forward
model, released preprocessing contract and protocol lock remain unresolved;
do not fit or score confirmatory signals until their gates pass.

## 10. Mathematical reduction test before another solver (29 October 2026)

For a measured field `y`, a declared family union `F = ⋃_b F_b`, forward
operator `A(θ)`, uncertainty set `Θ`, loss `ℓ`, and tolerance `τ`, the proposed
compatibility object is

```text
K(y) = ⋃_{b} ⋃_{θ ∈ Θ} {x ∈ F_b : ℓ(y, A(θ)x) ≤ τ}.
```

For any declared spatial functional `h`, its exact reported range is
`[inf_{x∈K(y)} h(x), sup_{x∈K(y)} h(x)]`. Computing this same range by exact
direct constrained fitting is an answer-equivalence oracle. A new name,
branch aggregation, or different numerical answer is not a novel method; a
difference indicates changed assumptions, approximation, or error unless a
separate guarantee explains it.

The audited prior art already covers substantial components: recovery over
finite unions of convex sets, robust recovery with uncertain sensing
operators, sparse linear-image estimation, near-optimal solution-set
summaries, and connected-support optimization. No precise missing lemma or
implemented complexity gain has yet survived that reduction. The narrow
mathematical question left open is whether one can produce a useful,
independently replayable enclosure of the spatial-functional range for the
**exact declared connected multi-patch disjunction jointly with continuous
physical forward uncertainty**, while preserving the disjunction and
accounting for numerical/forward-approximation error, at certified cost or
tightness better than direct branch-and-bound. This is a candidate question,
not evidence that existing methods cannot solve it.

The quantitative literature-range audit is recorded in
[`FORWARD_UNCERTAINTY_PRIOR_ART_20261027.md`](../../../research/gbf_omitted_activity_20261024/FORWARD_UNCERTAINTY_PRIOR_ART_20261027.md).
Vorwerk et al.'s broad conductivity intervals can motivate transparent
stress scenarios, but they come from a template head and single-dipole
sensitivity study; they do not bound WSGZP participant registration,
electrode placement, or extended CCEP-source error. They cannot be presented
as calibrated WSGZP uncertainty bounds.

Before implementing a solver for that question, freeze a minimal case and
quantifiers. In particular, distinguish (a) whether there exists an admitted
`θ` and source `x` that explains an observation, (b) whether a target source
fits for every admitted `θ`, and (c) whether every alternative is excluded
for every admitted `θ`. These are different claims. Compare full ranges and
rigorous enclosures against independent direct optimization, include a
disjunctive counterexample that defeats global convexification, and count
certified work as well as wall time. Reject method novelty if the candidate
reduces to established robust branchwise optimization plus union aggregation
without a proved guarantee or cost/tightness improvement. A permitted-window
search also must not be described as connected active support unless the
active support itself is constrained to be connected.

**Execution consequence:** do not build a larger solver or introduce ML until
this reduction test identifies a specific unhandled mathematical step.
Current float64 primal/dual checks are replayable numerical evidence, not
outward-rounded rigorous bounds. The available WSGZP positive-contact
endpoint, if its gates later pass, is a separate empirical validation path
and cannot substitute for this mathematical proof.
