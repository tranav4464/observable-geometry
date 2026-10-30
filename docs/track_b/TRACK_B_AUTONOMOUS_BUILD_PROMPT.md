# Autonomous build brief: Observable Geometry, Track B

> **Superseded 23 October 2026.** This brief describes the withdrawn WBEN route. Do not use it to select the active baseline, dataset, or gate sequence. The active GBFs project is defined in `PROJECT_DEFINITION.md`, `GBF_BUILD_PLAN.md`, and `GATE_REGISTER.json`.

You are continuing the computational-neuroscience ML/software build in:

`<repository root>`

Complete Track B as a usable, reproducible software build. Do the research, implementation, real-data evaluation, debugging, documentation, and verification required by the project. Do not return only a proposal or paper draft. Do not provide or request a timeline.

Read `docs/track_b/MASTER_RESEARCH_PLAN.md` for the full design and `docs/track_b/PROJECT_DEFINITION.md` for the concise scope. The machine-readable `docs/track_b/GATE_REGISTER.json` is authoritative for gate status. Reconcile older notes with verified evidence when they conflict; preserve the history of important corrections.

## Build objective

Independently reconstruct WBEN, a published joint scalp EEG/iEEG state-space model; build an auditable workflow that evaluates it against real paired recordings; and expose what the observations can and cannot support. Include matched baselines and a researcher-facing report that separates measured signals, predictions, latent estimates, and biological interpretations.

The contribution is undecided. The generic distinction between predictability and identifiability is already described in a 2026 virtual-iEEG review, and profile likelihood for partially observed dynamical models is established prior art. Do not call either a novelty. An edge-wise WBEN transition-parameter profile is only a design candidate; determine whether it is distinct from prediction-profile likelihood, dynamic-network identifiability, robust system identification, and the closest task-specific methods. Define its mathematical object and researcher decision, then retain it only if a prior-art gap survives and matched real-data evidence meets the prespecified criterion. Otherwise deliver the strongest honest reproduction/challenge software without a novelty claim.

This is a software build, not a paper-writing task. The long-term ambition does not expand the evidence: do not claim complete brain reconstruction, arbitrary-thought decoding, unique recovery of unobserved sources, or a breakthrough before the results justify it.

## Verify current state before working

Inspect the gate register and validator, master plan, project definition, README, B0/B1 closeouts, B2 specification, method matrix, evidence ledger, decision log, source tree, tests, and existing run artifacts. Verify current contents and status rather than assuming this prompt is current.

The recorded status is B-1 PASS, B0 PASS, B1 PASS within its bounded event-relative eight-second/50 Hz feasibility scope, B2 IN_PROGRESS, and B3–B8 NOT_STARTED. Track A is sealed. Do not describe B3 or later as complete until implementation and verification evidence exist.

## Non-negotiable constraints

1. Use real recordings for every active neuroscience experiment and model evaluation. Do not generate, extend, simulate, score, or use synthetic datasets or synthetic signal fixtures. Historical synthetic artifacts are archival only and must not be run or cited as active evidence. Use real-data checks, algebraic identities, independent implementations, and code-level invariants for software verification.
2. Keep participants `sub-01` through `sub-03` as development data. Do not inspect event rows or signal outcomes for `sub-04` through `sub-15` until the B5 protocol lock and access preflight pass. If an exposure occurs, record it and reclassify the affected data as development.
3. Do not modify source recordings. Do not contact people, publish or submit, incur costs, or use restricted data without explicit authorization.
4. Never invent results, citations, licenses, cohort details, novelty, test outcomes, or completed gates. Preserve failures, negative outcomes, exclusions, and deviations.
5. Keep separate: software correctness, reproduction fidelity, prediction of measured signals, parameter identifiability, anatomical interpretation, causality, and practical utility.
6. Keep Track A sealed. Keep WBEN, GBFs, direct baselines, and candidate extensions as separate implementations with distinct estimands.
7. Use CPU float64 as the correctness reference. Use GPU only for an eligible real workload that benefits, and compare with CPU on the same computation before reporting it.
8. Review licenses for all datasets, dependencies, templates, and transforms. The candidate MNI template crosswalk uses locally stored fields from a repository declaring CC BY-NC-SA 4.0; do not redistribute those fields or dependent artifacts without resolving the license obligations.

## Execute gates in order

### B2: Freeze one defensible real-data task

Complete primary-source review for WBEN, direct scalp-to-iEEG prediction/reconstruction, virtual-iEEG methods, working-memory load analyses, scalp/iEEG information-theoretic methods, and the closest method families for the proposed identifiability/sensitivity analysis. For each close source, record publication state, cohort, task, inputs, target, split, metrics, code/data access, and claim limits. Resolve the CAST description mismatch against the official dataset record and actual event labels before treating its result as a direct comparator.

Select one primary task, not a blend. Cross-load prediction of measured iEEG and the incremental predictive contribution of scalp EEG beyond task context remain candidate evaluation tasks only. Neither is a new method merely by naming it or applying it to WBEN. B2 must define the estimand, allowed inputs, participant/session/trial unit, time relation, target contacts/regions, task context, preprocessing, artifact/missing-data rules, split, metric, uncertainty, baselines, tuning budget, leakage controls, and falsifier.

The former 374/760 Harvard–Oxford identity-coordinate lookup is withdrawn. A candidate transform between likely dataset MNI152Lin coordinates and the atlas MNI152NLin6Asym space has been numerically audited on development electrode metadata. Round-trip consistency does not establish anatomical accuracy, row identity with the source localization script, or WBEN's exact contact-assignment rule. The transformed point lookup is not a faithful WBEN observation matrix. Either establish a defensible mapping variant with explicit limits and sensitivity checks, or select a task that does not depend on unsupported atlas correspondence.

The proposed mathematical contribution must be written as an exact object before implementation: estimand, assumptions, dimensions/units, algorithm, limiting cases, failure conditions, researcher decision, nearest alternatives, and falsifying criterion. Compare directly with observability/identifiability, profile likelihood, robust system identification, Bayesian uncertainty, calibration, and selective prediction as applicable. Reject the contribution if it duplicates prior art, cannot be tested on this data, or changes no useful decision. Close B2 only when an independent reviewer can audit the task and protocol without seeing reserved outcomes.

### B3: Reconstruct WBEN independently

Map each equation and algorithm step from the paper/supplement to code: dimensions, units, observation operators, objective, inference, parameter updates, initialization, preprocessing, and stopping rules. Document unresolved choices as explicit configurations. Preserve known paper inconsistencies rather than silently resolving them in the direction of a better score.

Implement under `src/observable_geometry/track_b/`, separate from baselines and extensions. Validate the CPU reference on allowed real development recordings after B2 passes. Independently check at least one input, model output, and metric. Report convergence, failures, and deviations honestly.

### B4: Challenge and select the extension

Use permitted real development data only. Compare WBEN, matched baselines, and any surviving extension with identical inputs, split, preprocessing, tuning opportunity, and compute. Include prespecified negative controls and sensitivity analyses. Assess participant-aware uncertainty and calibration only when claimed. Retain the extension only if it meets the criterion frozen at B2; otherwise remove it or narrow the claim.

### B5: Lock confirmation before access

Hash and freeze participants, sessions, trials, preprocessing, exclusions, target, inputs, model variants, hyperparameters/tuning budget, metrics, uncertainty, stopping rules, code/config/data hashes, and run identifiers before opening reserved outcomes. Preflight participant grouping, non-overlapping windows, train-only normalization, filtering boundaries, contact selection, and access logs. If any confirmation outcome has informed a decision, report the exposure and treat the affected data as development.

### B6–B8: Evaluate, audit, and package

Run the locked real-data analysis and independently recompute primary metrics from saved predictions. Report participant-level outcomes and uncertainty, counts, exclusions, missingness, failed fits, negative controls, and protocol deviations. Do not treat trials, windows, contacts, or time points as independent participants.

Test calibration, abstention, or practical utility only if prespecified, at matched operating points, with rejected-case rates visible. Package a clean installation and reproduction path. Document commands to obtain/verify eligible data under its terms, preprocess, fit, evaluate, and render reports. Keep participant recordings and restricted derived results out of source control unless terms permit distribution.

## Researcher-facing behavior

The software and reports must label measured scalp EEG and iEEG, model predictions, latent estimates, held-out evidence, assumption-dependent results, missingness, uncertainty, and failures separately. Do not draw estimated edges as if they were directly measured anatomical connections. Do not imply that sparse iEEG reveals unrecorded brain regions.

## Keep records synchronized

When evidence or decisions change, update the gate register, method matrix, evidence ledger, decision log, relevant gate documents, README, and `docs/project-review.html` together. Give every run a unique identifier. Preserve old outputs and link each reported result to its data manifest, code, configuration, environment, command, metrics, exclusions, and limitations.

## Completion rule

Declare the software build complete only when the clean install/run path works, WBEN equations map to verified code, the chosen real-data evaluation is leakage-controlled and independently checked, every claimed gate has executed evidence, and the report accurately communicates baselines, uncertainty, failures, exclusions, and limits. If the extension fails, say so and deliver the reproducible reproduction/challenge software without a novelty claim.

Begin with the earliest incomplete gate whose prerequisites are met. Resolve ordinary implementation choices independently and continue until the build is complete or a specific data/scientific blocker prevents further valid work.
