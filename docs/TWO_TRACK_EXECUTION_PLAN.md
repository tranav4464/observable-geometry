# Two-track execution plan

> **Historical execution plan, superseded 24 October 2026.** The gate status and active GBFs route are maintained in [`track_b/GATE_REGISTER.json`](track_b/GATE_REGISTER.json), [`track_b/PROJECT_DEFINITION.md`](track_b/PROJECT_DEFINITION.md), and [`track_b/GBF_BUILD_PLAN.md`](track_b/GBF_BUILD_PLAN.md). Track A remains sealed. Do not use this earlier RSG planning record to infer current Track B gates.

> **Verification closeout, 22 October 2026:** Track A acceptance is recorded in `TRACK_A_COMPLETION_REPORT.md` and the sealed run manifest. This is readiness for Track B's research and prior-art work, not acceptance of RSG novelty or physiological localization claims.

**Updated 22 October 2026 | Track A Foundation Build executed; Track B remains unstarted**

## Execution status

The authorized Track A run is complete for its selected development case. The protocol, verified data adapters, upstream GBFs execution, independent parity check, MNE comparator/resolution check, all-vertex nominal signature library, complete threshold sets, sensitivity checks, offline report, unique run manifests and adversarial artifact validator are implemented. The independent algebraic check matches upstream on identical saved inputs to relative Frobenius error `2.23e-13`.

This closes the **engineering Foundation Build** for one participant. It does not reproduce the GBFs paper's published benchmark and does not establish population performance, biological source accuracy, calibrated source uncertainty, or RSG novelty. Track B remains separate and must perform those scientific tests before stronger claims.

The frozen methods and quantitative results are recorded in [`FOUNDATION_PROTOCOL.md`](FOUNDATION_PROTOCOL.md); the accepted cold run and its hashed release are under `outputs/tracka_verified_20261022_final/`.

## 1. Strategy

The project is divided into two complete pieces:

1. **Foundation Build:** reproduce, understand and package nominal GBFs source reconstruction and source distinguishability under one verified head model.
2. **Research Build:** develop and validate Recoverable Source Geometry across noise and plausible forward-model uncertainty.

The Foundation Build is not a disposable prototype. It must be scientifically honest, reproducible and independently demonstrable. The Research Build uses frozen Foundation outputs and adds only the parts needed to test the new framework.

## 2. Shared claim boundary

The Foundation may state that two candidate sources have similar or different predicted scalp signatures under a specified nominal model. It may not claim robust recoverability, calibrated spatial certainty or validity across anatomy/model error.

The Research Build may use “recoverable” only after the score is calibrated and tested on untouched participants. Neither track may claim complete brain reconstruction, access to thoughts or universal EEG resolution.

# Track A: Foundation Build

## A0. Foundation design freeze

### Tasks

- Select one physically compatible source family: focal cortical candidates, cortical parcels or restricted GBF combinations.
- Define the first signal task: stimulation artifact or post-stimulus response. Do not combine their interpretations.
- Define nuisance treatment for amplitude, polarity, orientation, latency and baseline.
- Choose one conventional inverse comparator and one resolution-analysis comparator.
- Record the first development case and the eligibility rules for later participants.

### Deliverables

- `FOUNDATION_PROTOCOL.md`
- source-family diagram and data-flow diagram
- frozen definitions of target, observation window, preprocessing and metrics
- decision record explaining excluded alternatives

### Exit criteria

- The stimulation target can be represented in the selected source space.
- Every required quantity is available from Localize-MI or clearly derivable.
- No metric requires hidden test labels during fitting.

### Stop condition

If the physical target cannot be represented fairly, change the task before writing more code.

## A1. Environment and provenance

### Tasks

- Pin Python, operating-system details, GBFs commit and dependency versions.
- Preserve the untouched upstream GBFs clone.
- Define a separate adaptation layer rather than modifying upstream files silently.
- Verify Localize-MI license, file hashes, participant metadata and retrieval instructions.
- Create deterministic run manifests and unique output directories.

### Deliverables

- environment lock or reproducible environment specification
- dataset manifest with checksums and license notes
- one-command environment verification
- provenance schema for every output

### Exit criteria

- A clean environment imports all required dependencies.
- Missing files or version mismatches fail with actionable messages.
- No restricted dataset file is accidentally packaged for redistribution.

## A2. Physical data adapter

### Tasks

- Load epochs, channel metadata, bad-channel marks and time coordinates.
- Match EEG channels to the forward model by name rather than array position.
- Verify voltage units, reference convention and noise-covariance convention.
- Resolve fixed versus free source orientation.
- Verify head, MRI, surface and electrode coordinate transforms.
- Define the bipolar stimulation target: endpoints, midpoint or explicit bipolar forward representation.
- Keep stimulation artifact and physiological response windows separate.

### Deliverables

- annotated case manifest
- channel-alignment report
- transform-chain report
- diagnostic plots/tables using recorded metadata and geometry
- validated internal data bundle

### Exit criteria

- Round-trip coordinate checks pass at defined tolerance.
- Data and forward channels match exactly after documented exclusions.
- Reference and covariance ranks are consistent.
- The target definition is approved for the selected task.

### Stop condition

Any unexplained unit, reference, channel or transform mismatch stops scientific processing.

## A3. GBFs reproduction and reverse engineering

### Tasks

- Map paper equations to the upstream code path.
- Reproduce upstream numerical operations on identical controlled inputs.
- Document recorded-versus-simulation normalization differences.
- Audit the eigenvalue penalty domain, basis restriction, mesh units and hemisphere ordering.
- Replace no upstream operation in parity mode.
- Create a separately labelled numerically safer mode only after parity is demonstrated.

### Deliverables

- paper-to-code map
- parity report with numerical tolerances
- known-departures report
- recorded-data GBFs adaptation report

### Exit criteria

- Upstream and parity outputs agree within frozen tolerances on identical inputs.
- Every adaptation is named and justified.
- A source map can be traced to exact inputs and settings.

### Stop condition

If parity cannot be achieved, diagnose it before evaluating any extension.

## A4. Nominal source-signature library

### Tasks

- Generate sensor predictions for every allowed source candidate under the verified nominal forward model.
- Apply reference and noise whitening consistently.
- Profile or normalize frozen nuisance parameters.
- Store candidate IDs, cortical coordinates and construction settings.
- Test identical, polarity-reversed, scaled and null-space cases.

### Deliverables

- versioned source-signature artifact
- mathematical fixture suite
- source-candidate catalogue
- memory/runtime benchmark

### Exit criteria

- Repeated generation is deterministic.
- Nuisance handling behaves exactly as documented.
- Null-space or unsupported directions are identified rather than assigned false certainty.

## A5. Nominal distinguishability and ambiguity

### Tasks

- Implement nominal noise-scaled signature separation.
- Compare with raw lead-field correlation, principal-angle/subspace distance where relevant, and resolution-matrix metrics.
- Produce source-centered ambiguity sets at multiple descriptive thresholds.
- Avoid calling these sets calibrated or robust.
- Quantify sensitivity to covariance rank, reference and preprocessing choices.

### Deliverables

- nominal distinguishability matrix or structured equivalent
- ambiguity-set report
- resolution-matrix comparison
- sensitivity report

### Exit criteria

- Limiting cases pass.
- Results are stable enough to interpret or instability is clearly reported.
- Computational cost fits the local machine or has a documented batching strategy.

## A6. Standalone interface and reproducibility

### Tasks

- Build one command that validates a case, runs GBFs, calculates nominal ambiguity and exports a report.
- Display the nominal head-model assumption prominently.
- Include source map, similar alternatives, sensor signatures, reference, units and provenance.
- Add a clean-run reproduction script and user documentation.

### Deliverables

- command-line workflow
- offline report/3D viewer
- example instructions
- technical note and short demonstration

### Foundation completion criteria

- A new user can reproduce the example from documented inputs.
- Every output states that it is conditional on one nominal model.
- GBFs parity, data validity and nominal ambiguity tests pass.
- No RSG novelty claim is made.

## A7. Foundation evaluation and freeze

### Tasks

- Run the frozen nominal analysis on development data.
- Compare predicted nominal similarity with observed condition similarity descriptively.
- Catalogue failure cases and unresolved assumptions.
- Freeze the Foundation API, artifacts and version tag used by Track B.

### Deliverables

- Foundation evaluation report
- failure catalogue
- versioned interface/data contracts
- Track B handoff manifest

### Exit criteria for starting Track B

- Foundation Build is independently complete.
- Source task and data contract remain defensible.
- Nominal signatures contain enough variation to support a recoverability study.
- Gate 0 literature review identifies a plausible mathematical gap.

**Track A handoff (22 October 2026):** The cold engineering foundation and its audit remediation are closed against the sealed run manifest. The plausible, unresolved Track B gap is whether a calibrated, task-level source-equivalence object can predict held-out empirical confusion while accounting for physically defensible forward-model variation and nuisance effects. This may collide with resolution-matrix, adaptive-parcellation and robust inverse work. The observed six-site association is descriptive only. Track B should begin with prior-art equations, task validity and data feasibility; no novelty claim is accepted at this gate.

**Prior-art rationale for A7 plausibility:** Existing resolution matrices describe point-spread and cross-talk under a specified inverse; adaptive EEG/MEG parcellations already seek distinguishable parcels from cross-talk functions; robust inverse work already addresses forward-model error. A plausible, still-unverified gap is the *empirical calibration and predictive utility* of pairwise measurement-level equivalence across a physically justified family of forward models for a defined task. See the primary-source comparison in `RESEARCH_AUDIT.md`, including [adaptive cortical parcellations](https://pmc.ncbi.nlm.nih.gov/articles/PMC5864515/) and [spatial-fidelity evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7793168/). This is a research hypothesis, not proof that no prior method already does it.

# Track B: Research Build

## B0. Novelty and hypothesis freeze

### Tasks

- Complete equation-level comparison with resolution matrices, adaptive parcellation, SESAMEEG, robust eLORETA and Bayesian model-error methods.
- State the exact RSG object, difference, benefit and falsifier.
- Select hierarchy versus source-centered ambiguity-set output.
- Preregister the development/test separation and the first primary endpoint internally before test outcomes.

### Deliverables

- closest-method matrix
- formal contribution statement
- frozen research protocol
- claim/falsifier table

### Exit criteria

- The proposed object is mathematically distinguishable from closest work.
- The dataset can test the claimed difference.

### Pivot rule

If novelty fails, continue as a rigorous replication/comparison study or choose a narrower unresolved failure. Do not rename existing machinery.

## B1. Physically justified forward-model family

### Tasks

- Identify which uncertainty sources can actually be regenerated: electrode locations, tissue conductivities, geometry or limited combinations.
- Source parameter ranges from metadata or primary literature.
- Generate models with common source correspondence.
- Verify physical plausibility and numerical convergence.
- Separate aleatoric recording noise from model uncertainty.

### Deliverables

- forward-family specification
- parameter provenance table
- model-generation pipeline
- sensitivity and convergence report

### Exit criteria

- Every perturbation maps to a physical parameter.
- Source candidates remain comparable across models.
- Expanding a worst-case family does not incorrectly improve worst-case separation.

## B2. RSG mathematical core

### Tasks

- Implement the frozen nuisance-aware separation.
- Compare same-model worst case, set-to-set separation and probability-weighted risk on development data.
- Handle covariance support and reference rank explicitly.
- Build the hierarchy or ambiguity-set construction.
- Resolve non-transitivity without connected-component chaining.
- Define abstention when evidence is insufficient.

### Deliverables

- implementation-independent derivation
- tested numerical implementation
- complexity analysis
- limiting-case and adversarial tests

### Exit criteria

- Another researcher could reproduce the rule without guessing.
- All edge cases have expected behavior.
- The selected robust formulation is justified rather than chosen by test performance.

## B3. Statistical calibration

### Tasks

- Define an empirical discrimination task using development participants.
- Fit the simplest mapping from RSG separation to observed confusion.
- Compare with a fixed theoretical mapping and nominal-model calibration.
- Evaluate calibration curves, uncertainty and abstention behavior.
- Avoid high-capacity ML unless data volume and grouping support it.

### Deliverables

- calibration model and model card
- development-only diagnostics
- frozen threshold/error tolerance
- pre-test audit confirming no test-outcome access

### Exit criteria

- Calibration improves over or meaningfully complements the fixed mapping.
- Parameters are stable under grouped resampling.
- Claims remain appropriately limited with seven participants.

## B4. Recoverability-limited reconstruction

### Tasks

- Aggregate or report GBFs estimates according to the frozen recoverability output.
- Keep the original GBFs estimate available for comparison.
- Compare with existing adaptive parcellation at matched resolution/complexity.
- Measure localization utility, retained detail and stability.

### Deliverables

- RSG-constrained source output
- matched comparison report
- ablations for model uncertainty, calibration and nuisance handling

### Exit criteria

- Any reduction in detail has a measured benefit, such as improved calibration or stable localization.
- Visual smoothness alone is never counted as improvement.

## B5. Held-out evaluation

### Tasks

- Lock code and configuration before test evaluation.
- Evaluate participant-level calibration of predicted distinguishability.
- Evaluate secondary localization and spatial-detail metrics.
- Report all eligible participants, exclusions and failures.
- Run sensitivity analyses without retuning on test outcomes.

### Deliverables

- immutable test manifest
- participant-level result tables
- uncertainty intervals and sensitivity report
- null/negative-result interpretation if applicable

### Research success criteria

- RSG demonstrates a prespecified held-out advantage over nominal and closest compatible baselines.
- The advantage is not caused by unequal tuning, target leakage or arbitrary perturbation ranges.
- Failure regions and limitations are explicit.

## B6. Research interface and release

### Tasks

- Add hierarchy/ambiguity layers, calibration information and model-sensitivity views to the Foundation interface.
- Export machine-readable results and a compact human report.
- Package clean reproduction commands, licenses, citations and provenance.
- Prepare technical paper, poster/pitch and lab-facing documentation based only on actual results.

### Deliverables

- versioned RSG research package
- reproducibility bundle
- technical report
- demonstration and outreach materials

### Exit criteria

- An external user can reproduce the main table and figure.
- Every displayed claim maps to an evaluated result.
- The project clearly separates established components from the contribution.

## B7. Optional ambiguity-targeted sensor design

Begin only if B5 supports the recoverability measure. Select one unresolved distinction, rank feasible added sensors, account for reference/correlated noise, and test retrospectively using already-recorded electrodes against equal-budget random, standard and nominal designs.

### Deliverables

- frozen sensor-design objective and feasible candidate set
- retrospective equal-budget comparison
- reference/noise sensitivity analysis
- decision on whether prospective hardware validation is justified

### Exit criteria

- Recommended sensors improve the prespecified empirical outcome on untouched data.
- The gain survives comparison with random, standard-layout and nominal-model choices.
- No hidden source label is used to choose the sensor in the simulated deployment workflow.

# 3. Schedule and effort

| Milestone | Cumulative focused effort | Practical result |
|---|---:|---|
| A0-A2 | 20-40 hours | frozen task and valid case bundle |
| A3-A5 | 45-80 hours | reproduced GBFs plus nominal ambiguity engine |
| A6-A7 | 70-110 hours | complete standalone Foundation release |
| B0-B2 | 110-180 hours | formal RSG development prototype |
| B3-B5 | 180-290 hours | calibrated held-out research study |
| B6 | 220-340 hours | reproducible research release |
| B7 optional | 280-430 hours | sensor-design extension |

At 25 focused hours per week, the Foundation Build is approximately 3-5 weeks and the core Research Build approximately 9-14 weeks cumulative. At 15 hours per week, Foundation is approximately 5-8 weeks and the core research release approximately 15-23 weeks. Research pivots can extend these ranges.

# 4. Work tracking

Each work package uses four states: `not started`, `in progress`, `blocked`, `passed`. A package can pass only when its listed evidence exists. Progress percentage based only on code volume is prohibited.

Every result records:

- input and code hashes;
- environment and dataset version;
- participant/session/source IDs;
- preprocessing, reference and covariance convention;
- model parameters and calibration version;
- whether data were development or test;
- warnings, exclusions and failures.

# 5. Dependency and risk register

| Risk | Earliest detection | Prevention or response |
|---|---|---|
| Localize-MI target is incompatible with cortical source space | A0-A2 | change source task or dataset before RSG work |
| Coordinate/reference/unit error | A2 | hard validation failures and annotated transform report |
| GBFs behavior cannot be reproduced | A3 | preserve parity path and diagnose before extension |
| Nominal signatures are dominated by arbitrary amplitude | A0/A4 | freeze nuisance profiling and limiting-case tests |
| “Recoverability” duplicates adaptive parcellation | B0 | equation-level novelty kill gate |
| Forward ensemble is physically unjustified | B1 | remove unsupported parameters and narrow claim |
| Seven participants cannot support learned calibration | B3 | fixed mapping, grouped resampling and modest claim |
| Repeated pulses create false sample size | A0/B5 | aggregate by session and participant |
| Stimulation artifact is mistaken for neural decoding | A0/A2/B5 | separate windows and claim boundaries |
| Test data influence design | B0-B5 | immutable manifests and development-only revision |
| Attractive maps hide failed calibration | B4-B6 | primary calibration result shown before visualization |
| Runtime exceeds local 16 GB machine | A4/B2 | mode limits, batching, cached geometry and measured budgets |

# 6. Review cadence

At the end of every work package, update the decision log with evidence, failures, scope changes and whether the gate passed. Weekly reviews should answer four questions: what was demonstrated, what remains an assumption, what failed, and whether the next package is still justified. Test outcomes are reviewed only after code and configuration are frozen.

# 7. Final decision rule

Finish and present Track A even if Track B is delayed or falsified. Present Track B as an invention only if its exact distinction and held-out evidence survive the gates. Otherwise present the strongest truthful outcome: reproduction, benchmark, failure analysis and the narrower research question revealed by the work.
