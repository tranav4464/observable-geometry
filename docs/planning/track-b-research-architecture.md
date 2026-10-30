# Track B research architecture and execution system

> **Historical plan, superseded 22 October 2026.** The authoritative current plan is [`docs/track_b/MASTER_RESEARCH_PLAN.md`](../track_b/MASTER_RESEARCH_PLAN.md), with the required session procedure in [`docs/track_b/RESEARCH_OPERATING_SYSTEM.md`](../track_b/RESEARCH_OPERATING_SYSTEM.md) and machine-checked stage contracts in [`docs/track_b/GATE_REGISTER.json`](../track_b/GATE_REGISTER.json). This document records earlier RSG planning and must not be used to infer the current primary route or gate state. Track B's provisional WBEN reproduction/challenge route is not yet locked.

**Planning version 1.1, 22 October 2026. Status: B-1 passed, B0/B1 in progress; no Track B method validated.** Owner: Tranav Tyagi. Track A release: `outputs/tracka_release_20261022_v2`. This plan governs the research; it does not certify a new method or authorize a scientific claim. Current gate status is in `docs/track_b/GATE_REGISTER.json`.

## 1. The result we are trying to earn

The proposed result is a **task-specific, empirically tested map of which source alternatives a given EEG measurement can distinguish**. A candidate method, Recoverable Source Geometry (RSG), would use a declared family of physical forward models, measured noise, an explicit nuisance model, and a specified decision error. It would report source-centered ambiguity sets first. A spatial hierarchy or restricted GBFs reconstruction is a secondary output only if the ambiguity prediction works.

There are three separate claims, and each needs its own evidence:

1. **Mathematical contribution:** an exact decision object differs from the closest published methods. A different name, a GBF basis, or a whitened cosine does not qualify.
2. **Empirical contribution:** the object predicts confusion between *held-out* stimulation conditions better than matched nominal and prior-art comparators. The unit of generalization is a participant, not a trial or pair.
3. **Downstream utility:** restricting the detail of a source report improves a prespecified decision or its calibration without unacceptable loss of useful localization. A smoother picture is not evidence.

If claim 1 fails, publish a rigorous comparison or failure analysis instead of an invention claim. If claim 2 fails, do not use the word *certified* or claim that RSG measures recoverability. Claim 3 is not attempted until claim 2 has credible support. The larger goal of thought or imagination decoding is motivation, not an output of this dataset.

## 2. What is known at the start, and why the order matters

Track A produced a working, one-participant engineering benchmark: the pinned GBFs implementation, same-input algebraic parity, an MNE comparator, a full nominal signature search, and a recorded pulse-artifact analysis. The [independent follow-up audit](../../outputs/independent_review_20261022/REVIEW.md) found five release and validation gaps. Those were repaired in the new `tracka_release_20261022_v2` release: 27 unit tests and the sealed-run validator passed; resealing was rejected. It is development infrastructure, not evidence of Track B physical or scientific validity.

The Localize-MI repository describes **61 sessions from seven people**, with contact locations, EEG positions, surfaces, and prepared forwards. Numerical payloads for sub-01 through sub-07 are now local. A checksum/header contract passed for 50 runs and 2,004 trials across sub-02 through sub-07, and a metadata/forward geometry audit passed for all seven participants. These are **integrity and coordinate checks**, not seven validated analysis cases. The measured target is an intracranial *bipolar stimulation pulse artifact*. A fixed cortical-normal dipole is not automatically its physical generator. A development-only sub-01 test found that a contact-axis equivalent dipole fits the held-out pulse topography better than the fixed-normal proxy on median, but physical generator adequacy is still open. [Dataset description](https://www.nature.com/articles/s41597-020-0467-x); [B1 audit](../track_b/B1_LOCAL_DATA_AUDIT.md).

Prior art already includes direct two-source EEG separability under realistic forward simulations ([Kalogianni et al. 2018](https://pubmed.ncbi.nlm.nih.gov/29496570/)), [resolution matrices and point-spread/cross-talk functions](https://api.repository.cam.ac.uk/server/api/core/bitstreams/901c710a-6b48-4d1b-8271-41ec057451b2/content), [adaptive parcellation based on cross-talk](https://pmc.ncbi.nlm.nih.gov/articles/PMC5864515/), [lead-field clustering for parcellation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11845507/), [probabilistic source alternatives](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2024.1359753/pdf), [forward-model uncertainty in Bayesian estimation](https://discovery.ucl.ac.uk/id/eprint/10072222/), and a 2026 [target-centred framework for scalp-to-intracranial inference](https://arxiv.org/abs/2608.26998) that distinguishes target types and validation claims. Recent preprints also directly study scalp-to-iEEG waveform reconstruction with conditional flows and cross-attention models ([NeuroFlowNet](https://arxiv.org/abs/2603.03354), [CAST](https://arxiv.org/abs/2605.18897)). These make a broad “finest distinguishable pattern,” “recoverability framework,” generic uncertainty-aware inverse, or EEG-to-iEEG predictor insufficient as a novelty claim. Any RSG distinction must survive equation-level and task-level scrutiny, not a keyword comparison.

An additional direct collision is Yang and Liu's NeurIPS 2025 [joint scalp+iEEG state-space framework for whole-brain electrophysiological networks](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html). It uses a latent VAR, scalp lead field, iEEG region-selection matrix and EM/FIS inference, validates synthetic connectivity, and analyzes the same on004752 working-memory cohort. We will not claim generic multimodal network inference as our innovation. The equation audit records important reproduction questions, including opposite L1 penalty signs in two displayed objectives, a metric called accuracy that is algebraically precision, and noise/geometry assumptions. See [the full WBEN audit](../track_b/B0_WBEN_NEURIPS_2025_AUDIT.md).

## 3. Dependency architecture

```text
Evidence inventory and Track A repair ───────┐
Closest-method equation audit ────────────────┼─> task/estimand decision ─> frozen protocol
Physical dataset and target audit ────────────┘                         │
                                                     ┌───────────────────┘
                                                     v
                                  mathematical object + physical model family
                                                     │
                                                     v
                                   synthetic adversarial and numerical checks
                                                     │
                                                     v
                                  development calibration and matched baselines
                                                     │
                                                     v
                                  locked participant test and failure analysis
                                                     │
                                                     v
                               conditional reconstruction, report, reproduction
```

The earlier gates are **kill gates**, not paperwork. A plausible implementation cannot repair a physically invalid target, and a good held-out number cannot make an already published equation novel. Parallel work is limited to independent evidence gathering: Track A repair, prior-art reading, and metadata-only feasibility. No test-participant outcomes are inspected while choosing the method.

## 4. Two possible tasks; decide before writing the new score

**Route P: pulse-evoked response / stimulation-artifact distinguishability.** The declared source hypotheses are stimulation contact pairs. The outcome is the ability to tell which pair was stimulated from the distributed, processed scalp response under matched current, preprocessing, reference, and available channels. The Localize-MI BIDS arrays span about -250 to +10 ms around each intracranial pulse after high-pass filtering, baseline correction and peak realignment; the window includes the stimulation artifact. Therefore any Route P result is narrow evidence about discrimination under this stimulation and recording chain, not spontaneous cortical activity or general EEG source recoverability. Two candidate forward representations can be compared: an unrestricted equivalent-current dipole fitted or positioned near the contact-pair midpoint, and an explicit bipolar current-injection model. The first is an approximation with published empirical precedent, not proof that stimulation creates a neural dipole. Its goodness of fit, orientation freedom, conductivity sensitivity, residual structure, and the preprocessing transform must be checked against the more physical model where feasible. A fixed cortical-normal column remains a *proxy baseline*, not the scientific model. If neither candidate adequately predicts the artifact, Route P can only remain a method-sensitivity study. [Intracranial stimulation validation](https://pubmed.ncbi.nlm.nih.gov/36824389/); [bipolar artifact model](https://pmc.ncbi.nlm.nih.gov/articles/PMC9596776/); [B1 signal-chain audit](../track_b/B1_LOCAL_DATA_AUDIT.md).

**Route N: physiological cortical-source distinguishability.** Choose a dataset or experiment with defensible source conditions and independent validation. Required fields are EEG/MEG recordings, usable anatomy/forward models, source-condition labels or paired invasive evidence, enough independent participants, and lawful reproducible access. NEMAR nm000513 is event-centered, lacks contact coordinates, and has an existing extraction study. nm000456 has only two SEEG participants and no public coordinates. Zauli OSF 89ndr has simultaneous HD-EEG/SEEG and eight individual MRIs, but its completed metadata audit found exactly one iEEG contact per participant, so it cannot test within-participant spatial contact pairs. The 2024 source-imaging study and 2026 same-cohort preprint also create close task overlap; event-label semantics and EEG-to-MRI `IntendedFor` filenames remain unresolved. on004752 offers fifteen participants, low-density scalp EEG, multiple depth contacts, MNI coordinates and working-memory trials, but earlier work already analyzes working-memory load and scalp-source/hippocampal coupling on the same task. It is a candidate only for a distinct bounded estimand, not whole-cortex source truth or individualized forward-model validation. Localize-MI's later evoked responses likewise do not become complete cortical ground truth just because stimulation location is known. Details and kill criteria are in [the B1 physiological screen](../track_b/B1_PHYSIOLOGICAL_DATASET_SCREEN.md). If no dataset satisfies the exact spatial claim, postpone it or select a narrower task with its own explicit contribution and validation design.

Gate B1 records an explicit **P, N, or no-go** decision with a target diagram. The method can use GBFs in either route as a compact reconstruction representation, but its evaluation claim must match the physical generator actually tested.

## 5. Candidate mathematics to freeze, not yet a claimed discovery

Let `h` be a declared source hypothesis, `m` a physically specified head model, and `theta` the allowed nuisance variables (amplitude, polarity, latency, orientation, and baseline as appropriate). Let `mu(h,m,theta)` be its sensor prediction after the same reference and channel selection as the data. Let `C` be noise covariance estimated on the specified trial or average scale. A nominal comparison uses the supported covariance subspace:

`d_m(h1,h2)^2 = min_theta1,theta2 || C_m^(-1/2) [mu(h1,m,theta1)-mu(h2,m,theta2)] ||^2`.

This equation is a *candidate operationalization*, not a novel mathematical result. For fixed predictions and shared Gaussian covariance it reduces to classical squared Mahalanobis/ideal-observer discriminability, with the standard equal-prior Bayes error `Phi(-d/2)`. Profiling nuisance parameters creates a composite-hypothesis problem, and worst-case behavior over distributions/model families has a long robust-testing literature. EEG/MEG literature also explicitly defines source ambiguity as distinct source configurations producing the same measurement. B0 must test whether the controlled, empirical future-confusion estimand adds a distinct and useful decision beyond these established objects. If not, the project must be presented as a benchmark or replication, or pivot, rather than claiming a new mathematical framework.

The minimization is only meaningful after constraining nuisance variables. Allowing zero amplitude for both hypotheses makes every pair indistinguishable; independently normalizing topographies answers a different, shape-only question. Route P should predefine whether amplitude is known, bounded, estimated from a non-test calibration run, or deliberately profiled out. The same decision applies to timing and sign. Whitening must handle the average-reference rank deficiency and must not silently discard lead-field components outside covariance support.

For head-model uncertainty, compare three objects on development data only:

- `min_m d_m`: the same unknown head model applies to both hypotheses. This is the first robust candidate.
- distance between the two model-prediction sets: allows different model settings for each hypothesis and is more conservative; use only if the decision problem warrants it.
- risk averaged over model weights: use only when weights have defensible provenance; hand-picked weights are not posterior probabilities.

The primary object should be **source-centered ambiguity sets** at an empirically chosen operating point, with an abstention state when evidence is unsupported. Pairwise indistinguishability is generally non-transitive; connected components can chain together distant, distinguishable endpoints. A hierarchy is a later derived view and must state its clustering loss and stability. The ideal equal-covariance Gaussian error formula is an algebraic check, not automatic calibration for recorded EEG.

The candidate innovation, if one remains, is a *specific tested decision rule* combining a physically valid task, ambiguity under model uncertainty, and *out-of-participant* error calibration. Forward-model averaging and uncertainty calibration already have precedents, so their combination cannot be asserted as novel merely from its ingredients. Gate B0 must establish an exact mathematical and empirical difference from the nearest published work. If it does not, choose a narrower failure mode or conduct a careful replication and comparison.

## 6. Evaluation design before outcomes

**Independent units.** Participant is the outer unit. Runs, repeated sites, currents, trials, and all pairs sharing a site stay inside their participant. Sub-01 is development data because its outcomes have already shaped this project. A held-out participant's anatomy and electrode coordinates may be used to compute predeclared predictions; their EEG outcomes may not tune models or thresholds. If fewer than four eligible, independent held-out participants remain, treat the result as a feasibility report rather than a generalization claim. Seven total participants cannot support a high-capacity neural network or a precise population guarantee.

**Eligibility audit, before outcomes.** For each participant, record available payloads, forward model, coordinate transforms, electrode quality, number of unique sites at matched current, trial counts, timing, stimulation artifacts, and whether a physically compatible candidate can be generated. Inspect metadata and existence first. Hash payloads on retrieval. Record all exclusions with reasons before computing pairwise outcomes. Preselect a minimum viable count of independent within-participant site pairs and trials from metadata; abort a confirmatory test if it is not met.

A first **metadata-only** count from the checked-out epoch TSVs found the following largest same-current site groups. The pair counts are combinatorial possibilities, not independent observations or verified usable pairs. Numerical payload integrity and headers for sub-02 through sub-07 have since passed audit; held-out EEG sample values and pair-confusion outcomes remain uninspected.

| Participant | Largest same-current group | Sites | Candidate pairs | Fewest metadata trials at a site |
|---|---:|---:|---:|---:|
| sub-01 | 1 mA | 6 | 15 | 27 |
| sub-02 | 0.5 / 1 mA (tie) | 3 at each current | 3 at each current | 42 / 43, respectively |
| sub-03 | 0.5 mA | 5 | 10 | 29 |
| sub-04 | 0.1 mA | 7 | 21 | 38 |
| sub-05 | 0.1 mA | 8 | 28 | 21 |
| sub-06 | 0.1 mA | 4 | 6 | 42 |
| sub-07 | 0.3 mA | 4 | 6 | 38 |

Different participants' best-matched currents differ. B1 must decide whether current enters the nuisance/calibration model, whether a common-current subset exists, and whether trial-level signal quality supports the endpoint. Metadata alone cannot answer those questions.

The reproducible metadata-only screen `outputs/track_b/data_acquisition/eligibility_sub-02_03_04_05_06_07.json` reconciles the table against event/channel TSVs and reports every current group. The across-run good-channel intersections are 190, 195, 212, 156, 169 and 140 for sub-02 through sub-07. All six have at least one group with ≥3 sites and ≥20 trials/site, but only four meet ≥4 sites and ≥30 trials/site. These thresholds are sensitivity descriptors, not a locked eligibility rule. Site pairs are dependent and one acquisition run represents each condition, so this does not establish statistical power or justify a learned calibration function.

**Observed discrimination.** Within each eligible participant, use a frozen trial-level binary site classifier or a predeclared likelihood-ratio statistic for each matched-current site pair. Train it on training trials and evaluate on held-out trials separated by acquisition block where possible. Match trial count and channels, avoid shared-trial preprocessing leakage, and report uncertainty in pair-level error. The classifier is a measurement instrument, not the proposed invention. A random-label and trial-block negative control must approach chance. Flag pairs with near-zero signal or unstable preprocessing; do not remove them after seeing a method's ranking.

**Predicted discrimination.** Compute nominal and robust source-hypothesis separation using only the participant's non-outcome geometry, the frozen forward family, and permissible noise calibration. Do not select a favorable reference, time sample, source orientation, or model range from held-out outcomes. Store the full prediction vector and validity flags, including abstentions.

**Primary endpoint.** Freeze one participant-weighted measure of how well predicted pair confusion agrees with held-out empirical confusion. Recommended after feasibility: participant-level mean absolute calibration error of predicted confusion probability, with unweighted participants and a fixed development-fitted monotone link. Compare its paired participant-level difference against a nominal lead-field baseline and the strongest compatible prior-art score. Report every participant, the raw pair table, paired differences, and an uncertainty interval; do not treat the many dependent pairs as the sample size. A rank-discrimination metric (for example within-participant Spearman) is secondary. If finite sample noise makes pairwise error estimates too unstable for calibration, freeze a rank endpoint before inspecting test outcomes or mark the study exploratory. The exact operating tolerance, split, and minimum effect must be signed in B1/B4, not chosen after test results.

**Secondary tests.** Compare coverage/abstention, threshold calibration, false confident distinctions, stability across plausible model settings, GBFs localization and retained spatial detail. Spatial utility is measured at matched region count/detail against adaptive parcellation. Keep pulse-artifact and physiological interpretations separate. No single favorable site or attractive map can outweigh the primary endpoint.

**Confirmation rule.** A seven-person single dataset can provide an important feasibility signal but weak evidence for a broad breakthrough. A strong method claim requires an independent dataset, a prospective new participant, or a collaborator-run replication after the method freezes. If unavailable by the deadline, label the result a candidate framework with its actual scope.

## 7. Matched comparator set and ablations

All comparators use the same eligible participants, site pairs, channels, reference, noise convention, train/test partition, and permitted tuning budget.

| Comparison | What it tests | Minimum implementation/evidence |
|---|---|---|
| Simple distance and chance | Whether geometry matters at all | Euclidean site distance and random/permuted labels |
| Track A nominal signature | Whether robustness adds value | Whitened topographic cosine or declared equivalent on the same physical source family |
| Nominal statistical separation | Whether the new output beats a standard discriminability score | Mahalanobis/ideal Gaussian score with identical nuisance assumptions |
| Resolution matrix / cross-talk | Whether inverse leakage already explains confusion | `K L`, PSF/CTF summaries for a frozen MNE operator; equations from Hauk et al. |
| Adaptive parcellation and lead-field clustering | Whether source sets merely rename existing partitions | Matched number of regions, geometry and spatial constraints; implementations justified by full paper audit |
| Forward-error/Bayesian comparator | Whether ensemble robustness already exists in usable form | Closest feasible model-error method under matched physical perturbations; document if direct implementation is infeasible |
| GBFs and MNE output | Whether restricted reporting helps reconstruction | Frozen upstream GBFs and conventional inverse with identical data/target |

Required ablations: nominal versus physically perturbed family; model range width; amplitude/polarity handling; noise covariance and reference; source-family change; calibration link versus fixed Gaussian mapping; hierarchy versus set-valued output if a hierarchy is attempted. Each ablation has a predicted direction written before test inspection. A baseline that cannot be fairly implemented is reported as missing, not silently omitted from the novelty claim.

## 8. Gates, required proof, and failure routing

| Gate | Deliverable and verification | If it fails |
|---|---|---|
| B-1: foundation integrity | New Track A release includes tests in snapshot, prohibits resealing, fixes chart label and metric/CSV checks; fresh run and mutation tests pass. Old run remains immutable. | Continue only literature and metadata work; do not use its validator as proof of Track B numerical correctness. |
| B0: closest prior art | Full-text equation matrix for at least resolution/CTF, Farahibozorg adaptive parcels, 2025 lead-field clustering, Bayesian forward error, robust inverse and SESAMEEG; exact difference, benefit, falsifier and implementation status per method. | Narrow the claim, choose a different obstacle, or report a replication/comparison. |
| B1: physical task and dataset | Participant eligibility table, source-generator diagram, transforms/units/reference/time/noise audit, P/N choice, data license, split and measurable endpoint. At least two eligible sites per test participant under a matched condition. | Find a compatible dataset or restrict to a descriptive artifact study. |
| B2: formal specification | Independent derivation of nuisance and model-family score, source correspondence, abstention, non-transitivity, limiting cases and complexity. Two reviewers can implement without guessing. | Revise the definition before writing production code. |
| B3: forward family | Each variant regenerated from a named physical parameter with provenance; mesh/coordinate correspondence, numerical convergence and sensitivity checked. The nominal model is one member. | Remove unsupported dimensions or perform a nominal-only study. |
| B4: numerical and statistical development | Analytical fixtures, independent reference implementation, property/adversarial tests, leakage controls, frozen calibration model, matched baseline outputs. No held-out outcomes opened. | Repair or change the method using development data; version the revision. |
| B5: protocol lock | Immutable code/config/data inventory, participant assignment, primary endpoint, effect threshold, exclusions, tuning budget, seed and permitted sensitivity analyses. Independent preflight checks all paths and hashes. | No confirmatory test; document the reason and relock. |
| B6: held-out evaluation | Once-only participant-level run; all eligible cases, raw predictions/outcomes, paired comparator differences, uncertainty and negative controls. | Report the null/negative result. A post-hoc revision needs a new independent confirmation set. |
| B7: conditional spatial reporting | Only after B6 support: source-centered alternatives and optional detail-limited GBFs report compared at matched complexity against adaptive parcels. | Keep the calibrated ambiguity output, omit reconstruction improvement claim. |
| B8: release and outside check | Clean-machine reproduction of main table/figure, test suite and manifest, license audit, methods report, explicit claim ledger, second researcher review if available. | Release as prototype only; list unreproduced components. |

Gate status is one of `NOT_STARTED`, `IN_PROGRESS`, `PASS`, `FAIL`, `PIVOT`. `PASS` requires a dated evidence artifact and a named falsification check, not a persuasive paragraph. A `FAIL` records the smallest scientific claim still supported. A stage may be revisited, but if held-out results drove the change its old test set becomes development data.

## 9. Software and evidence architecture

Keep the pinned GBFs checkout read-only. Put Track B research modules under `src/observable_geometry/track_b/`: `contracts.py` (physical metadata and unit checks), `hypotheses.py` (source and nuisance definitions), `forward_family.py` (physical scenarios and source correspondence), `separation.py` (nominal/robust measures and ambiguity sets), `calibration.py` (small fixed statistical link), `comparators.py` (matched baseline interfaces), and `evaluation.py` (grouped analysis). `scripts/track_b/` holds one deterministic command per gate. Tests should target independent mathematical properties, input corruption and leakage traps rather than merely restating implementation lines.

**Compute environment, checked 2026-10-22.** The host exposes an NVIDIA GeForce RTX 4050 and driver-reported CUDA 13.1. The pinned `.venv_tracka_clean` is a Python 3.12/MNE 1.13.2 CPU environment; PyTorch and CuPy are absent, so it cannot run project tensor work on CUDA. This does not block current metadata, derivation or small-matrix tests. When a gate introduces a measured GPU workload, create a separate, version-pinned Track B CUDA environment and run a CPU/GPU parity fixture before relying on it. Keep the sealed Track A environment unchanged; record package versions, driver, GPU model, seeds and numerical tolerances in each run manifest. A visible GPU alone is not evidence that an analysis used it.

Each run writes to a new `outputs/track_b/<run_id>/` directory. Its manifest stores code and input hashes, participant/session IDs, reference, ordered channels, units, source family, forward scenario parameters, covariance scale, split role, calibration version, exclusions, warnings, predictions and all failures. The release builder refuses an existing manifest and inventories *all* required source, tests, scripts, protocol and result files before hashing. The audit script independently recomputes key metrics and verifies that CSV, JSON and report figures derive from the same rows.

The public result should have three layers: (1) a one-page question/claim/outcome report; (2) a methods record with equations, baselines, participant-level tables and failures; (3) a viewer only for claims the data support. The viewer distinguishes predicted signatures, measured artifacts, uncertainty due to noise, sensitivity to forward models and any empirical calibration. A 3D map is a communication layer, not evidence by itself.

## 10. Operating system for research without wasted work

Maintain four live records in `docs/track_b/`: `DECISION_LOG.md`, `EVIDENCE_LEDGER.md`, `METHOD_MATRIX.md`, and `PROTOCOL_LOCK.md`. A decision records its date, alternatives, evidence, impact on claims and test-data exposure. The ledger marks each claim `ESTABLISHED`, `SUPPORTED_WITH_LIMITS`, `UNTESTED`, or `FALSIFIED`, with a file/figure/command that proves it. The matrix compares equations, nuisance and uncertainty assumptions, outputs and code availability. The protocol lock is written before any confirmatory outcome inspection.

The gate register is enforced by `scripts/track_b/validate_gate_register.py`. Run it before work and after editing a gate status. It fails on missing evidence, unknown or cyclic dependencies, or any started/passed/failed gate whose prerequisites are not passed. On the current Windows setup, run `.venv_tracka_clean\\Scripts\\python.exe scripts\\track_b\\validate_gate_register.py`; the current register must pass before B2 implementation or any B6 outcome access. This validator checks workflow consistency, not scientific truth; gate-specific falsification checks remain mandatory.

Every work session begins by reading the gate register, works on the highest-risk unresolved dependency, and ends with one evidence update or a concrete failure record. Stop rules prevent spending time on viewer polish before task validity, deep learning before sample-size evidence, a full 8,196-by-8,196 matrix when blocked computation suffices, and adding forward variants without physical provenance. Use small fixtures to test an equation before running seven subject models. Preserve failing runs; never silently rerun with altered settings under the same ID.

Review after each gate: **What was demonstrated? What is still assumed? What result would falsify the next step? Are we still studying the same task?** A second person can challenge the physical source model and closest-prior-art row before B5. Outreach to a lab is useful after B0/B1 have concrete diagrams and questions; no external message is sent without Tranav's authorization.

## 11. Critical path and deadline decisions

| Window | Required output | Decision |
|---|---|---|
| 22–31 October | Finish B0 exact-method audit and B1 task decision; repair Track A release in parallel | Pick a physically valid P/N route or pivot before algorithm work. The nm000513 metadata/leakage screen is complete; its missing contact coordinates rule it out for spatial validation. |
| November weeks 1–2 | B2/B3 frozen math, physical model prototype, synthetic/adversarial checks | Keep only a formulation that survives known failure cases |
| November weeks 3–4 | B4 development analysis and matched baseline comparison | Decide if a confirmatory participant test is justified |
| Early December | B5 lock and B6 once-only held-out test | Accept result, including null result; do not retune on test participants |
| Remaining December | Conditional B7/B8 report, reproducibility, lab-facing pitch | Describe only claims that survived their gates |

These are decision windows rather than promises. The earliest expensive risk is **task validity**, followed by **prior-art overlap** and **participant eligibility**. If any fails, switch route or narrow the claim immediately. A convincing candidate framework may emerge by December; a demonstrated scientific breakthrough requires a positive independent replication and cannot be scheduled by effort alone.

## 12. Immediate next actions and current status

1. B0: finish full-method and comparator audit. Direct collisions include two-source separability, lead-field clustering, adaptive parcellation, Bayesian forward uncertainty, plausible-source maps, calibration tooling, information-theoretic bounds and scalp-to-iEEG “where versus what” methods. Reproduce Kalogianni et al.'s separability baseline before testing any forward-ensemble extension. Novelty is **unresolved**.
2. B1: integrity, channel/header and coordinate audits are complete for seven Localize-MI participants. Physical generator adequacy remains unresolved. NEMAR nm000513 supports no contact-level spatial validation. Zauli OSF 89ndr metadata are now payload- and checksum-audited: 256 scalp EEG channels have XYZ entries, but each of eight participants has exactly one iEEG contact, ruling it out for within-subject spatial-pair validation. The event-label summary and EEG-to-MRI filename mismatch remain unresolved; no signal or MRI payload was read. on004752 is the next metadata-screen candidate for a narrower task-conditioned scalp-to-contact question, but it lacks established individual-MRI forward models and cannot ground a full source map. No route has passed B1.
3. B-1: the repaired Track A release passed and is sealed. Continue verifying it from the sealed snapshot; do not treat it as Track B scientific proof.
4. Freeze the P/N source task, independent unit, empirical outcome and primary comparator before B2. Sub-01 development diagnostics exist, but no held-out Track B result or new-framework claim exists yet.

**References used for this planning screen:** [GBFs paper](https://arxiv.org/abs/2401.17939); [Localize-MI descriptor](https://www.nature.com/articles/s41597-020-0467-x); [resolution analysis](https://api.repository.cam.ac.uk/server/api/core/bitstreams/901c710a-6b48-4d1b-8271-41ec057451b2/content); [adaptive CTF parcellation](https://pmc.ncbi.nlm.nih.gov/articles/PMC5864515/); [lead-field clustering](https://pmc.ncbi.nlm.nih.gov/articles/PMC11845507/); [SESAMEEG](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2024.1359753/pdf); [Bayesian forward uncertainty](https://discovery.ucl.ac.uk/id/eprint/10072222/); [robust eLORETA](https://arxiv.org/abs/2405.05790). This is a targeted screen. B0 requires full-method comparison before any novelty verdict.
