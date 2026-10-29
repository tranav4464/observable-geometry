# Observable Geometry: project definition

## Active build target

### Close-prior-art update, 29 October 2026

A targeted primary-source check added two near-contemporaneous preprints to the
novelty threat register: CANDLE (arXiv:2610.07824), which uses lead-field
range/null projectors for geometry-aware learned source reconstruction and
tests stimulation localization on the Parmigiani cohort, and arXiv:2610.27461,
which combines observable-row diffusion refinement with projected null-space
completion. Both estimate a representative source map rather than compare a
declared set of source families, but they rule out broad novelty claims around
observability decomposition or null-space analysis. Observable Geometry's
conditional family-audit distinction remains only a different estimand until
it demonstrates a useful decision advantage over direct fitting and matched
baselines on eligible held-out measured data. See the
[close-prior-art recheck](CLOSE_PRIOR_ART_RECHECK_20261029.md).

### Latest evidence, 29 October 2026

**Software and package verification update, 29 October 2026:** current commit
`3cfa693c2be6ab5866df9ae68613236fda937d0e` passes **211/211 workspace tests**
and **209 source-archive tests with two documented skips**. The source archive
hash is `308b2b4e87603eadf3d58a33700f15305e160d52fab3fcac5bcb149c455c81ad`.
The read-only gate validator passes with 354 evidence paths after the current
B8 release and handoff evidence was registered. The
315-file source snapshot passes at this commit. A wheel built from this exact
commit archive passed all seven source/version/license checks and a fresh
Python 3.12.14 install. The installed CLI exactly reproduced all 40,980 ranked
pairs, score arrays, and summary metrics from the sealed sub-01 model-only
reference. See the [current B8 candidate report](B8_RELEASE_CANDIDATE_3CFA693_20261029.md),
[review handoff record](B8_REVIEW_HANDOFF_3CFA693_20261029.md), and machine-readable reports under
[`20261029T_commit_release_3cfa693/`](../../outputs/track_b/20261029T_commit_release_3cfa693/).
These checks cover software behavior and evidence-path integrity only; they do
not validate source physiology, novelty, or WSGZP registration. B4–B7 remain
pivoted and B8 remains open for outside review.

An earlier working-tree run at commit `cfb53e8` passed 186 tests and checked
330 evidence paths; it is superseded by the 211-test run above. The WSGZP
sample-free BIDS validation follow-up confirmed that the scalp EEG coordinate
sidecars use a coordinate-system keyword rejected by the applicable BIDS
1.6.0 contract; this is metadata nonconformance, not proof of anatomical
misregistration. Exact commands and findings are in the [WSGZP
metadata-contract recheck](WSGZP_METADATA_CONTRACT_RECHECK_20261029.md). The
earlier atomic-CLI and package-parity runs remain recorded in [the historical
test evidence](TEST_RUN_EVIDENCE_20261029.md).

**Commit-bound refresh, 29 October 2026:** commit `0d54fe09b5ee08c8ffefb72197f737e99987c585`
passed source-manifest verification (302 files), 181/181 workspace tests, and
179 source-archive tests with two documented skips. The source archive hash,
commands, package-parity limitation, and remaining B8 conditions are recorded
in the [commit-bound recheck](B8_COMMIT_BOUND_RECHECK_20261029_0D54FE0.md).

**Exact-commit package refresh, 29 October 2026:** commit
`edf085c07b08d3681657f164a0a9e3bb6a5ecf03` now has a wheel built from its Git
archive, verified against all 18 package modules and project metadata, and
installed into a fresh Python 3.12.14 environment. The installed CLI exactly
reproduced the one-model reference output (40,980 ranked pairs); the access
audit confirms model-array-only access. A hash-verified, data-free external
review bundle is prepared. Details and claim limits are in the
[current B8 candidate report](B8_RELEASE_CANDIDATE_EDF085C_20261029.md).

The same working-tree CLI also reproduced the prior clean-wheel output exactly
on the sealed model-only input: 40,980 ranked pairs, every score array and all
summary metrics matched. This confirms that the output-publication change did
not alter the nominal diagnostic on the one checked model; it is not a source-
recovery result. A distinct 0.1.3.dev0 development wheel was built from an
isolated source copy, installed in a fresh Python 3.12 virtual environment
with NumPy 2.5.4 and SciPy 1.18.1, and reproduced the same outputs exactly.
Its 18 packaged Python modules match the current checkout byte-for-byte. This
is a clean-environment package/parity check on one model, not an outside
reproduction or a public release. The earlier 0.1.2 wheel records are retained
as historical artifacts and must not be conflated. See the [worktree parity
report](B8_WORKTREE_ATOMIC_CLI_REPRODUCTION_20261029.md), [historical 0.1.2
check](B8_CURRENT_WHEEL_PARITY_20261029.md), and [0.1.3.dev0 candidate
check](B8_DEVELOPMENT_CANDIDATE_PARITY_20261029.md).

**Endpoint design adversarial correction, 29 October 2026:** the candidate
WSGZP follow-up decision is now explicitly separated into (A) a conditional
compatibility-set audit, for which direct constrained fitting is the
answer-equivalence oracle, and (B) a lossy fixed-area prioritization map that
can be judged only by sampled SEEG-positive-contact capture. The latter cannot
validate `UNIQUE_ENOUGH`/`AMBIGUOUS` labels or whole-cortex source truth.
Participant-level holdouts, matched area and abstention budgets, sampling
controls, a frozen meaningful-effect threshold, valid participant geometry,
preprocessing semantics and run correspondence remain required. This is a
design correction only: the protocol remains unlocked and no EEG/SEEG samples
were opened for it. See [the adversarial amendment](DECISION_ENDPOINT_ADVERSARIAL_AMENDMENT_20261029.md).

**Measured-data benchmark completed:** a separate locked exploratory route used
permitted OpenNeuro `ds004752` simultaneous scalp EEG and stereo-EEG from 12
participants, 57 sessions, 1,483 valid trials and 532 held-out intracranial
contact pairs. It found a small mean cross-spectrum scalp-prediction advantage
(0.0222 normalized-MAE units), but its participant-bootstrap 95% interval
crossed zero. A post-hoc audit of saved participant effects found 9/12 positive
effects, with exact sign-flip and sign-test p-values of 0.1426 and 0.1460.
These summaries do not establish a reliable confirmatory advantage. This
validates a real scalp-to-contact prediction benchmark, not GBF source-map
recovery: an intracranial contact is not a complete cortical ground truth and
this dataset does not satisfy the original individual-forward-model contract.
The sensitivity audit reads only saved participant-level metrics, not EEG/iEEG
samples. See the [sensitivity audit](DS004752_EFFECT_SENSITIVITY_20261029.md)
and [real-data status report](../../../research/gbf_omitted_activity_20261024/REAL_DATA_VALIDATION_STATUS_20261028.md).
Do not merge this benchmark with the constructed-field geometric claims.

**WSGZP provenance recheck, 29 October 2026:** a fresh read-only query of the
public OSF storage API found only the six BIDS archive parts and
`eeg_badtrials.json`, with no separately listed digitizer/registration files.
The extracted BIDS tree still has participant T1w MRIs and scalp coordinates
declared in T1w millimetres, but the exact participant-level transform linkage
and reviewed QC remain unverified. This narrows the file-search uncertainty;
it does not clear the geometry gate. A separate unauthenticated EBRAINS
Knowledge Graph query returned HTTP 401, so its file listing was not
retrieved; this does not establish that EBRAINS lacks geometry files. See the
[public inventory recheck](WSGZP_PUBLIC_GEOMETRY_INVENTORY_RECHECK_20261029.md)
and [upstream coordinate-pipeline audit](WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md).

**WSGZP geometry compatibility screen, 29 October 2026:** the new
metadata/MRI-only screen examined all 36 participants without opening EEG or
SEEG samples. Under the declared-T1w-to-NIfTI-qform hypothesis, 57 of 6,660
electrode positions are outside the image field of view across eight
participants; all fiducials are inside. These counts do not validate or
falsify the coordinate frame because scalp sensors may lie outside a cropped
MRI. The feasibility review confirms that the extracted package lacks the
original digitizer files, saved transform and surface meshes; a participant-
specific registration cannot yet be independently validated from the local
materials. The coordinate gate remains open and the source-recovery protocol
must not use these geometries until provenance or independent registration QC
passes. See the [coordinate compatibility screen](WSGZP_COORDINATE_COMPATIBILITY_SCREEN_20261029.md)
and [independent-registration feasibility check](WSGZP_INDEPENDENT_REGISTRATION_FEASIBILITY_20261029.md). The follow-up checked the extracted package directly and reports the FOV/proximity screens, per-participant counts, reproduction commands, and why they remain insufficient for approving geometry in [the detailed recheck](WSGZP_GEOMETRY_RECHECK_20261029.md).

**Localize-MI model-bundle audit, 29 October 2026:** all seven participant
forward FIFs were downloaded from the pinned dataset revision and verified
against the annex manifest. Each loads as a finite 256-channel, 8,196-source
free-orientation leadfield; channel order is identical across participants.
The embedded MRI-to-head transform agrees with the inverse of the matching
head-to-surface HDF5 transform to a maximum absolute matrix difference of
`2.94e-8`. This establishes file and internal transform consistency only, not
anatomical registration accuracy or source-recovery validity. The replayable
[audit report](LOCALIZEMI_FORWARD_BUNDLE_AUDIT_20261029.md),
[script](../../scripts/track_b/audit_localizemi_forward_bundle.py), and
machine-readable result are registered under B1. No EEG/SEEG recordings were
accessed for this audit.

**Scalp-coordinate contract recheck, 29 October 2026:** a metadata-only audit
confirmed that all 36 scalp EEG sidecars use the coordinate label `T1w` without
an axis/origin description, and their populated `IntendedFor` fields point to
missing `*_T1.nii` paths while the files are named `*_T1w.nii`. This is an
unresolved coordinate-semantics and MRI-association issue, not evidence of
misregistration. The audit also confirms that 319/323 EEG/iEEG run pairs have
different retained epoch counts and none has a shared unique event identifier,
so the released derivatives cannot support trial-level cross-modal pairing.
The results and official BIDS 1.6.0 references are in the
[WSGZP metadata audit](WSGZP_METADATA_AUDIT_20261028.md); the fresh machine
report is local under the ignored `outputs/track_b/20261029_wsgzp_metadata_contract_audit/`.

**Controlled-stimulation family validation completed:** a separate bounded run
now uses real Localize-MI scalp epochs, 224 common EEG channels, 8,196 sources,
the participant-specific forward model and five repeated stimulation sites
(1 mA/5 mA). It compares point, equal-weight patch, signed local-patch and
global ridge explanations of the measured pulse artifact. Flexible direct
fits have lower held-current residuals than point/equal-weight patches. This
is a real controlled-artifact diagnostic, not endogenous neural-source
validation or a GBF novelty result. See the [family validation record](../../../research/gbf_omitted_activity_20261024/LOCALIZE_FAMILY_VALIDATION_20261028.md).

**Source-family defense and density sensitivity are now documented:**
Primary literature supports testing area-weighted, same-polarity connected
cortical patches as a simulation family, but does not calibrate this project's
two-hop size, 40 nAm budget, or density cap to the participants' task activity.
The earlier uncapped two-hop uniform winners had connected active support in
all 20 cases; six exceeded the illustrative 0.30 nAm/mm² cap. Complete
independently replayed all-window refits at 0.16, 0.30, and 0.77 nAm/mm²
retain six patch fits and one distant-point-to-patch conditional screen
reversal at each cap. This is an exploratory, constructed-field sensitivity
result, not known-source validation. See the [assumption ledger and replay
record](../../../research/gbf_omitted_activity_20261024/SOURCE_FAMILY_PHYSIOLOGICAL_DEFENSE_20261028.md).

**Smooth-family transfer falsifies a simple general rule:** All-window
uniform/Gaussian four-hop scans on 20 earlier geometry-selected targets
in sub-03–07 passed separate replay. Four targets admit a smooth
alternative below the illustrative 5% fixed-pair distance screen, unlike
the two selected sub-02 targets. Prior uniform two-hop one-patch scans
cross in six cases and change the point-source screen in one. These
families are not nested because patch extent is fixed differently.
This remains constructed-source, nominal-forward, post-development
evidence; no novel method or physiological validation follows. See [the
five-participant result](../../../research/gbf_omitted_activity_20261024/SECONDARY_GAUSSIAN_FAMILY_TRANSFER_RESULTS_20261028.md).

**Smooth source-family challenge:** A separately replayed all-window scan
tested area-weighted one-sign Gaussian activity at mesh-geodesic widths
5, 10 and 20 mm for the two constructed sub-02 targets. All nominal
minima (4.005–4.755) and all physically varied endpoint minima
(5.308–6.406) stay above the illustrative 5% fixed-pair threshold
3.2897, whereas feasible flexible within-window alternatives fall below
it. This is a conditional, post-development source-family contrast on
one person and two constructed fields. It cannot identify true neural
activity or establish a new mathematical method. See [the full scan](../../../research/gbf_omitted_activity_20261024/SUB02_GAUSSIAN_PATCH_RESULTS_20261028.md).

**All-window source-family decision contrast:** On two constructed sub-02
targets, an independently replayed scan of all eligible constant-density,
area-weighted four-hop windows finds nominal minimum whitened distances
4.853 and 4.402. Both clear an illustrative 5%-error **fixed-pair** screen,
whereas verified flexible within-window maps give distances 1.918 and
1.844 and fail it. The actual flexible-map active support is fragmented.
This is a concrete *model-conditional family sensitivity*, not a
physiological result, a composite classifier guarantee, or a distinct new
optimization method. A full-mesh uniform scan under the physically varied
0.012 S/m skull-conductivity BEM also passed independent replay, with
minimum distances 6.481/5.989; feasible flexible alternatives remain at
2.799/2.643. This is one endpoint, not a conductivity interval. See [the
nominal all-window baseline](../../../research/gbf_omitted_activity_20261024/SUB02_GLOBAL_UNIFORM_FOUR_HOP_RESULTS_20261028.md)
and [the full physical endpoint](../../../research/gbf_omitted_activity_20261024/SUB02_FULL_VARIED_UNIFORM_RESULTS_20261028.md).

**Source-family interpretation correction:** The two four-hop witness
maps and their physical-endpoint refits occupy connected *allowed windows*
but their thresholded active supports split into five to seven mesh
components. The same-sign and density limits do not enforce intact or
smooth recruitment. An independent triangle/DFS audit replayed all 18
component counts. The four-hop results therefore apply to a capped source
distribution inside one connected window, not a physiologically verified
contiguous active patch. See [the defensibility update](../../../research/gbf_omitted_activity_20261024/SOURCE_FAMILY_DEFENSIBILITY_UPDATE_20261028.md).

**Physical-forward and task-risk check:** On sub-02, a fresh nominal
three-layer BEM matched 124 selected published forward columns to maximum
relative whitened error `5.87e-7`. Changing the illustrative skull
conductivity from 0.006 to 0.012 S/m and refitting the same target atom
gave residuals 0.719/0.570 for two fixed nominal constructed fields. A
matched, sign-coherent, density-capped refit within the two frozen four-hop
windows gave larger residuals 2.276/2.017. If target and alternative are
both generated under the varied model, the patch alternatives imply
8.1%/9.3% conditional Gaussian fixed-pair error for one 43-trial average.
The finite-window optima passed separate source-map and primal/dual replay.
This is one physical endpoint and two selected constructed targets, not
a continuous forward-uncertainty certificate, empirical source
identification or a new method. See [the endpoint](../../../research/gbf_omitted_activity_20261024/SUB02_PHYSICAL_WITNESS_ENDPOINT_RESULTS_20261028.md)
and [the matched refit](../../../research/gbf_omitted_activity_20261024/SUB02_PHYSICAL_PATCH_REFIT_RESULTS_20261028.md).

**Second-participant development model:** sub-02 run-01's recorded
prestimulus EEG produced a participant-specific baseline covariance from
43 trials and 199 channels; a separate chunked implementation replayed the
covariance and forward mapping at near machine precision. Four target fields
were then constructed from sub-02 geometry and tested against all distant
area-weighted two-hop patch pairs. Their best two-patch residuals were
1.96, 13.78, 1.82 and 12.57 whitened units, all above the illustrative
`tau=1`; a separate exhaustive replay passed. This is the first additional
participant **model-conditional** source-family test, not validation against
known neural activity. The matched distant-point baseline makes the same
exclusion decision on all four, so no added researcher decision is shown.
See [the sub-02 result](../../../research/gbf_omitted_activity_20261024/SECONDARY_SUB02_MODEL_TRANSFER_RESULTS_20261028.md).

**Exploratory transfer across all seven available models:** the same
source-family comparison was extended to sub-03 through sub-07 after a
frozen exploratory protocol. Their recorded prestimulus covariances and
participant forward models passed separate numerical replay. Across the
six secondary participants (24 constructed targets), every compact-patch
minimum stayed above illustrative `tau=1`, and every distant-point
comparator made the same exclusion decision. The patch model fit closer
in 21/24 cases, but this is no decision benefit at the declared threshold.
This remains a conditional model result, not measured neural-source
validation. See [the six-participant transfer report](../../../research/gbf_omitted_activity_20261024/SECONDARY_SIX_EXPLORATORY_TRANSFER_RESULTS_20261028.md).

**Held smooth-family refit:** all six saved capped L1 witnesses failed after
20 mass-preserving graph steps and scalar refitting, but optimizing within
that same smooth family found four new exact alternatives inside the 40 nAm
budget. All six minimum-moment LP fits and dual bounds passed independent
edge-flux and covariance replay. For the two over-budget exact minima,
an additional bounded-budget search found approximate `tau=1` fits at
residuals 0.99846 and 0.65820, both independently replayed. All six
therefore have feasible alternatives in the declared smooth family. This
strengthens the conditional
source-family audit on previously frozen targets but does not validate the
uncalibrated smoothness model or provide a novel optimizer. See
[the smooth-refit result](../../../research/gbf_omitted_activity_20261024/HELD_SMOOTH_REFIT_RESULTS_20261028.md)
and [the approximate-fit replay](../../../research/gbf_omitted_activity_20261024/HELD_SMOOTH_APPROX_RESULTS_20261028.md).

**Matched source-family decision:** a hash-bound assembler compared the
separately replayed global single-dipole, uniform two-patch, scattered L1 and
density-capped L1 results on the eight frozen nominal targets. In six, the
best distant point and uniform two-patch alternatives both miss `tau=1`, but
a distant capped distributed source fits essentially exactly under the same
40 nAm moment budget. The witnesses are highly fragmented, the comparison is
exploratory, and direct distributed fitting already supplies the same
answer. The demonstrated contribution is an inspectable conditional
assumption audit, not a new optimization method or robust physical source
claim. See [the matched decision result](../../../research/gbf_omitted_activity_20261024/MATCHED_FAMILY_DECISION_RESULTS_20261028.md).

**Candidate gate:** the decision-directed physical interval certificate is
not yet a defensible new method: its current bound is too loose, all eight
held physical-endpoint targets fail universal target fit, and ordinary refits
give the same negative decision. The source-family audit has conditional
decision reversals, but physiological family validity and prospective
researcher benefit remain unproved. The [candidate gate](../../../research/gbf_omitted_activity_20261024/CANDIDATE_GATE_20261028.md)
records three routes, closest methods, falsifiers and the current interim
classification without claiming novelty.

**Eight frozen physical-endpoint challenge:** all eight targets preselected
for an earlier source-family holdout failed a same-target amplitude refit at
the independently rebuilt 0.012 S/m MNE BEM endpoint under illustrative
`tau=1`; residuals ranged from 1.178 to 3.642. A separate pseudoinverse
replay passed all eight fits and matched nominal source-column mapping to the
sealed leadfield at `1.28e-16` maximum relative error. This independently
selected target set strengthens the **negative decision** for the current
illustrative interval, but ordinary endpoint refitting already produces it.
It does not validate conductivity, source physiology, population frequency or
a novel method. See [the eight-target result](../../../research/gbf_omitted_activity_20261024/EIGHT_TARGET_PHYSICAL_ENDPOINT_RESULTS_20261028.md).

**Packaged robust-audit input boundary:** the independently written
`verify_robust_audit_inputs.py` passed hash and conservative-scalar replay for
the two saved sub-01 cases. The installed wheel's CLI reproduced both case
decisions from outside the source checkout. Its report explicitly states that
the command itself does not replay supplied input bounds. The full package
suite passed 126 tests. This closes a saved-case provenance and packaging gap,
not a physiological validation or a novel-method claim. See
[the input replay report](../../../research/gbf_omitted_activity_20261024/ROBUST_AUDIT_INPUT_REPLAY_RESULTS_20261028.md).

**Conditional robust attribution audit:** the new package command
`observable-geometry robust-audit` distinguishes a nominal target-only result,
a sufficient interval certificate, a named in-set counterexample, and an
unresolved result. For two fixed sub-01 synthetic fields, the 0.009 S/m model
gives target-only fit at illustrative `tau=1`; separately generated 0.012 S/m
forward fields give target minima 1.493 and 1.643, refuting target-only fit
throughout the declared interval for both. High-precision finite-vector
replays, hashed inputs, explicit parameter-membership checks and 125 passing
package tests support these **conditional software decisions**. A later CLI
input-disclosure test brought the current full-suite count to 126.
An independently generated held 0.0105 S/m forward narrows both target-fit
threshold crossings to `(0.009,0.0105)` under the finite-model continuity
assumption; it does not identify real tissue conductivity or a unique crossing.
Four additional registered BEM bisection decisions per target put an existence
crossing for target 6103 between `0.00899999961257` and `0.00909374963678`
S/m, and for 2075 between `0.00946874973364` and `0.00956249975786` S/m.
An independent saved-arithmetic verifier passed; it did not regenerate the
six new forward solves. These brackets are hypothetical model stress results,
not estimates of participant conductivity.
A separate MNE physical-forward rebuild subsequently reproduced the three
newly selected bracket endpoints within `7.8e-7` residual difference and
retained all three threshold signs. This checks those finite nodes, not the
entire conductivity continuum or real neural sources.
The continuous forward radius remains over 21,000 whitened units for a 20 nAm
column, so it cannot certify positive exclusion. A simple endpoint refit
already detects the same failure; the CLI's value is auditable claim handling,
not a novel mathematical technique or validated physiological inference. See
[the decision report](../../../research/gbf_omitted_activity_20261024/ROBUST_AUDIT_DECISION_RESULTS_20261027.md)
and [the bound follow-up](../../../research/gbf_omitted_activity_20261024/CONTINUOUS_EEG_TIGHTENING_RESULTS_20261027.md).

**Six-of-eight source-family contrast:** all eight preselected model
targets exclude two uniform patches at the one-unit stress tolerance;
six admit an exact distant signed-L1 source match within the same
40 nAm absolute-moment budget. Each LP has a direct field witness and
a separately replayed sensor-space dual certificate. The same six
exact matches survive the project's previously used 0.3 nAm/mm²
per-vertex density cap, with separately replayed box-dual certificates.
The six matches
occupy 154–194 active vertices in 142–172 disconnected mesh components
at the reported 0.001 nAm threshold. They demonstrate conditional
assumption sensitivity on one model, not physiological plausibility,
a novel optimizer, or a population finding. The scattered comparison
was specified after the uniform outcomes were seen. See
[the complete eight-case audit](../../../research/gbf_omitted_activity_20261024/SCATTERED_VS_UNIFORM_HOLDOUT_RESULTS_20261027.md).

**Eight-target uniform-template holdout:** an earlier seed-selected set of
eight sub-01 hypothetical source targets was frozen before this scan.
Every exhaustive two-patch minimum stayed above the one-unit stress
tolerance under both equal-vertex and area-weighted template rules. The
lowest of the 16 minima was 2.379, and all eight full-pair scans passed
separate numerical replay. This supports a conditional exclusion for the
restrictive uniform-template source family across those targets on one
head model; it does not exclude flexible variable-amplitude competitors,
measure real physiology, or establish population generality. See
[the holdout result](../../../research/gbf_omitted_activity_20261024/UNIFORM_PATCH_HOLDOUT_RESULTS_20261027.md).

**Rank-one scaling falsifier:** a safe local patch-span lower bound
screened 145 of 32,997,469 eligible pairs and only seven more than the
existing complete weak-dual bank on the matched pair universe. A
separate eigensolver and all-pair replay passed. The rank-one route
is rejected as the main scaling method; this does not rule out stronger
structured bounds. An independently replayed follow-up found that even
rank five leaves a median patch-column approximation radius of 2.797,
too loose relative to the one-unit tolerance under the stated source
budget, so a rank-five all-pair scan was not pursued. See
[the matched screen](../../../research/gbf_omitted_activity_20261024/PATCH_SUBSPACE_R1_SCREEN_RESULTS_20261027.md)
[the rank curve](../../../research/gbf_omitted_activity_20261024/PATCH_SUBSPACE_RANK_DIAGNOSTIC_RESULTS_20261027.md)
and [source-family prior art](../../../research/gbf_omitted_activity_20261024/PATCH_FAMILY_PRIOR_ART_DECISION_20261027.md).

**Full-mesh uniform-patch challenge:** exhaustive CPU scans and separate
full replays checked 30.21 million disjoint pairs per weighting when
entire windows are excluded, and 33.00 million per weighting when only
inside-ball vertices are masked. The lowest masked-window residuals
were 3.562 (equal vertex) and 3.533 (active-mesh area weighted), both
above the one-unit stress tolerance. This is a conditional result for
uniform templates on one model; the broader variable-amplitude
sign-coherent two-window minimum remains unknown. The first area run
was invalidated by a dense-versus-decimated mesh mismatch and is not
used. See [the full result and correction record](../../../research/gbf_omitted_activity_20261024/UNIFORM_PATCH_GLOBAL_RESULTS_20261027.md).

**Additional model preflight:** full forward matrices for sub-02 through
sub-07 passed model-only shape, geometry, good-channel and fixed-orientation
checks. That was a preflight, not source replication. A later exploratory
compact-patch comparison has now used each participant's recorded baseline
covariance and replayed source calculations, as summarized above. The
broader scattered-versus-local family comparison in the inactive
cross-participant protocol remains undone. See [the six-file preflight](../../../research/gbf_omitted_activity_20261024/SECONDARY_FORWARD_PREFLIGHT_RESULTS_20261027.md).

**Point-source comparator:** all eight frozen target/pair/geometry
single-vertex fits stay above the stress tolerance even without the
density cap. Three matched actual-fine distributed fits fall below it.
This shows the selected counterexamples need more than one vertex in
their stated window unions, but direct distributed optimization is
existing practice and already produces the same answer. See
[the comparator and replay](../../../research/gbf_density_challenge_20261026/SINGLE_ATOM_BASELINE_RESULTS.md).

**Certified decision map:** 24 matched, hash-bound comparisons of the verified
point, smooth and target-adaptive results passed separate interval replay.
Seven previously selected comparisons have opposite coarse/fine or
diffusion-family decisions at the declared stress tolerance of 1. The eight
target-adaptive comparisons have none. The map also reports exact tolerance
intervals implied by the saved certificates; these are not calibrated noise
or confidence ranges. Geometry switches are not assumed to be nested source
families. See [the complete audit](../../../research/gbf_density_challenge_20261026/STABILITY_MAP_RESULTS.md)
and [replay record](../../../research/gbf_density_challenge_20261026/stability_map_verification_001/result.json).

**Forward-error budget:** a separate calculation and arithmetic replay give
sufficient per-column whitened perturbation radii for the seven selected
opposite decisions. The smallest open radius is about 0.00938 per 20 nAm
source unit when target and alternative forward columns may both move.
The bound is standard triangle-inequality sensitivity, not a calibrated
head-model uncertainty range or a new method. See
[the sensitivity report](../../../research/gbf_density_challenge_20261026/FORWARD_ERROR_BUDGET_RESULTS.md).
The stated diffusion-family inclusion now has an explicit
[operator proof and implementation audit](../../../research/gbf_density_challenge_20261026/DIFFUSION_NESTING_AUDIT.md);
no analogous inclusion is asserted for coarse versus fine geometry.

**Target-dependent follow-up:** eight new seed-selected targets each received
their own alternative pair selected using coarse fields before fine generation.
All 4,535 fine fields and 64 branch certificates passed separate replay. Both
geometries excluded in every case: no decision reversal. This addresses the
fixed-bank limitation below but does not establish whole-cortex exclusion.
The matched original point-target control retains one selected reversal;
generalization and practical decision benefit remain unproven. See
[the new pilot](../../../research/gbf_density_challenge_20261026/TARGET_ADAPTIVE_RESULTS.md)
and [direction reassessment](../../../research/gbf_density_challenge_20261026/DIRECTION_REASSESSMENT_20261027.md).

**Generalization check:** eight target locations selected by geometry and a
fixed seed were subsequently tested against the two frozen alternative pairs.
All 128 branch certificates and 32 sign unions passed separate replay; no
coarse-excluded/fine-feasible reversal occurred. These point-equivalent targets
and the fixed original competitor bank do not test every cortical alternative,
but they do not establish generalization of the selected counterexamples either.
See [target validation](../../../research/gbf_density_challenge_20261026/TARGET_VALIDATION_RESULTS.md)
and [the discovery decision](../../../research/gbf_density_challenge_20261026/DISCOVERY_DECISION_20261027.md).

The fine-source follow-up has completed separate numerical replay: 2,377 fine
forward fields and 48 sign branches, followed by 365 density-challenge records.
The new smooth-family refit adds 48 branch fits and 12 four-sign unions, all
replayed from original mesh edges with a separate certificate implementation.
At a 0.3 nAm/mm² cap and 40 nAm budget, actual fine geometry admits a selected
100-step diffusion-family alternative with residual 0.807984, while matched
coarse CPS has lower bound 1.107191. A second selected pair remains excluded
at 100 steps (fine lower bound 1.302119), but admits an alternative at 20 steps.
The one-unit threshold is an uncalibrated stress test. These are one-model,
selected-pair findings, not full-cortex exclusions or physiological validation.

This resolves the specific gap between smoothing an existing witness and
optimizing within the same smoothing family: three of four previously failed
witness comparisons regain a below-threshold fit. It does not establish a new
mathematical method. Independent researcher decision value, biological source
constraints, forward uncertainty and generalization remain unproven. See the
[density report](../../../research/gbf_density_challenge_20261026/REPORT.md) and
[smooth-family refit report](../../../research/gbf_density_challenge_20261026/SMOOTH_REFIT_RESULTS.md).
The chronological evidence below remains available; this update does not change
Track B gate statuses or the sealed Track A release.

Observable Geometry is a computational-neuroscience software build centered on **Geometric-Informed Basis Functions (GBFs)** for EEG source imaging. The goal is to reproduce and reverse-engineer the relevant GBFs implementation, then provide a researcher-facing tool that measures how distinguishable candidate source patterns are at the scalp under one verified participant-specific forward model.

The first software demonstration uses the real Localize-MI dataset and the sealed Track A sub-01 forward model. Track A already contains a clean implementation-parity check, a nominal source-signature library, a list of high-similarity distant source pairs, and an MNE resolution comparison. Those artifacts are the starting foundation, not proof of a new method or general source-localization performance. The 2026 GBF paper has already reported localization results for 318 iES-CCEP sessions from 35 participants and for 24 favourable-outcome patients from HDEEG-IED-SurgOutcome. Neither dataset may be presented as an untouched independent cohort for the corresponding broad GBF claim. HDEEG-IED-SurgOutcome remains a possible participant-held-out secondary evaluation because the public release contains 44 cases, individual MRI and electrode coordinates, EEG averages, resection imaging, and outcomes; the exact overlap with the published GBF subset, EBRAINS terms, and a reviewed protocol must be resolved before any data or outcomes are accessed. The downloaded and extracted iES-CCEP/WSGZP package contains a root `LICENSE` and `dataset_description.json` that both declare CC BY-NC-SA 4.0; the OSF API still labels its license relationship `Other` and points to a `license.txt` absent from the visible metadata listing. The package declaration resolves the earlier reuse-term uncertainty for noncommercial use subject to attribution, ShareAlike, and applicable ethical/privacy constraints. The archive is outside Git. Metadata and NPY-header audits have not analyzed EEG/SEEG sample values. No signal-level analysis is authorized yet: the protocol is unlocked, participant geometry/forward validity remains under review, released event IDs and cross-modal trial pairing are unavailable, and the candidate endpoint must still beat the closest prior methods. See `B4_OSF_WSGZP_LICENSE_AUDIT_20261024.md`, `DATA_ACCESS_STATUS_20261028.md`, and `NOVELTY_PROOF_PLAN_20261028.md`. Neither candidate establishes novelty by itself.

A close new method comparison appeared as the October 2026 CANDLE preprint, which is marked under review. It uses a learned prior in the leadfield null space and reports evaluations against the same Parmigiani et al. stimulation-data family, with GBF among its baselines. This further narrows any defensible method claim. The paper does not report the B2 pairwise source-signature score, but its cohort must not be treated as independent evidence for this project unless subject/run overlap is reconciled. The inspected project page did not expose a code link; availability and reuse terms for the supplementary implementation and checkpoints remain unverified.

## Scientific question

> Under one declared head model, reference, noise covariance, and source family, which spatially separated source hypotheses produce scalp patterns that this measurement setup can distinguish, and which pairs remain nominally confusable?

The tool concerns **model-predicted sensor patterns**. It does not recover a unique true source, provide calibrated probabilities, validate physiological localization, map every neural event, or reconstruct the whole brain. Localize-MI's stimulation contacts are ground truth for the pulse-artifact localization task only; they do not establish ground truth for distributed physiological activity.

## Existing base and contribution status

- **Existing method:** upstream GBFs and the Track A adaptation. The upstream code is vendored under its BSD 3-Clause license. Track A records numerical parity on the selected real Localize-MI inputs, with relative Frobenius difference `2.23e-13`; this is not a full reproduction of the paper's benchmark results.
- **Existing tool behavior:** Track A computes amplitude- and polarity-invariant whitened leadfield similarity for distant source pairs under one fixed forward model and covariance. Its outputs are explicitly nominal.
- **Build contribution under review:** turn this into a clear, reusable source-distinguishability workflow with auditable inputs, assumptions, pairwise scores, and comparison to standard resolution diagnostics. The broad idea of source ambiguity/separability is established prior art. Do not call the metric mathematically novel unless a precise additional method survives B0/B2 review and matched validation.
- **Experimental method under review:** the build now contains an isolated `tail_closed` module implementing a grid-evaluated, error-aware frontier against a full finite-mesh competitor Gram. The accompanying research prototype constructs that Gram from the FEM resolvent, avoiding an arbitrary high-mode cutoff. This is a candidate tail-closed observable-subspace method, not a passed gate or a novelty claim. Its physical prior, equation-level prior-art overlap, global numerical certification, and researcher decision benefit remain open.
- **Exploratory decision demonstration:** under one shifted FEM prior and a post hoc 2% modeled separation threshold, the cutoff-300 competitor supports 19 dimensions whereas the full finite-mesh competitor supports 16. At rank 16 the selected source combinations pass a replayed model certificate and both bilateral low-mode and sensor-SVD selections fail. This shows a concrete modeled representation choice, not prospectively validated analyst utility or a calibrated EEG noise threshold. See `../../../research/gbf_omitted_activity_20261024/RESEARCHER_DECISION_DEMONSTRATION.md`.
- **NeuroFlowNet:** prior route only. Its clean-room waveform-prediction plan and on004752 audits are retained as historical evidence and are not the active project target.

## Data and computation rules

Use real recordings and the existing verified head model. Do not generate synthetic datasets or synthetic signal fixtures. Algebraic identities, code invariants, and independent numerical implementations may be used for software verification. Keep the Track A release immutable; new code, outputs, and manifests receive new paths and run IDs. Use CPU float64 as the correctness reference and GPU only for an eligible real computation after CPU checks pass.

The sealed GBF implementation/parity case is development-only and one-participant. The later exploratory compact-patch calculation spans six additional participant anatomy and baseline-noise models, but the source targets are constructed and the family/tolerance are uncalibrated. Any physiological or population claim requires an appropriate measured-source endpoint, independently verified forward models and a locked evaluation. Numerical source-pair rankings are not calibrated probabilities of distinguishability in the population. Public availability alone does not establish permission for reuse; data-use terms must be established before acquisition or analysis.

## Deliverable

A runnable software workflow that accepts a verified forward solution and its declared sensor/noise contract, reproduces the GBFs baseline, computes nominal source-pair distinguishability outputs, and presents the assumptions and limitations alongside the result. Include a reproducible command, tests, a small real-data demonstration, saved manifests/results, a plain-language walkthrough, and a claim-to-evidence table. The central deliverable is the software, not an academic paper.

## Current gate status

GBFs is selected as the bounded software/reproduction route, with no new-method claim. B0–B3 are recorded as passed at their stated scopes. The registered B2 CPU64 parity run passed on 24 October 2026. The supplied B2 review record contains a malformed verifier hash, and workspace review declarations conflict about whether the reviewer was an unaffiliated human or an AI; see the B2 closeout before treating that sign-off as independently authenticated. B3 passes for the versioned, tested nominal source-distinguishability API/CLI and sealed model-only demonstration; the upstream GBFs inverse remains a separate computation documented in Track A. Track A remains sealed.

B4 reproduced the existing six-site, 224-channel sub-01 pair table exactly, but the Localize-MI endpoint is a stimulation pulse artifact and the tested simple source generators leave substantial structured residuals. The earlier 236/224-channel joined comparison is invalid. B4 is therefore recorded as **PIVOT** for that endpoint. Metadata-only public-data screens found no independent dataset that meets the active participant-specific geometry and paired-reference requirements. The new NEMAR catalog-wide screen found four records carrying both EEG and iEEG modality labels; two newly inspected candidates do not qualify: `nm000434` lacks participant-specific geometry/contact coordinates and release-level EEG/LFP alignment, while `on001785` places EEG and ECoG in separate cohorts. HDEEG-IED-SurgOutcome remains a possible same-cohort secondary clinical-outcome evaluation; the same GBF paper already used 24 favourable cases, so no independent-cohort claim is available. B5 protocol lock and B6 held-out evaluation remain **PIVOTED** until a suitable task, exact participant overlap, data terms, and independent protocol review are resolved. No new participant outcomes were opened. See `B4_DEVELOPMENT_AUDIT_20261024.md`, `B4_CHANNEL_MATCH_RECONCILIATION_20261024.md`, `B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md`, `B4_NEMAR_CATALOG_SCREEN_20261024.md`, and `B5_B6_ROUTE_CLOSEOUT_20261024.md`.

B7 paired all 8,196 B3 source scores with MNE resolution summaries from the same 236-channel model. Rank associations are moderate, showing related but non-identical descriptive views. This exploratory, spatially dependent analysis does not establish analyst utility. B7 is recorded as **PIVOT** under its failure route; the tool is retained as a descriptive diagnostic, without utility or novelty claims. See `B7_DECISION_VALUE_AUDIT_20261024.md`.

The researcher-facing CLI, package wheel, clean model-only reproduction, and committed source-snapshot verification are complete. B8 remains in progress pending an independently authenticated outside review or reproduction. A newly supplied B2 review draft names a Caltech affiliation and asserts personal inspection, but workspace records also contain a different affiliation and a malformed verifier digest; the assertion cannot be treated as authentication by itself, and that review concerns B2 rather than B8. The project has not demonstrated a novel mathematical method, physiological localization validity, population generalization, or researcher decision benefit.

**28 October decision-semantics update:** A later sub-02 exhaustive model-only audit certified that two constructed focal targets are farther than the illustrative `tau=1` threshold from every declared connected, sign-coherent, density-capped four-hop patch alternative. A separate full-branch implementation replayed all 30,342 branches. Yet independently replayed *feasible* alternative fields lie at whitened distances 1.918 and 1.844. Under the bundle's covariance for one 43-trial average and the standard equal-prior Gaussian pair model, those pairs imply ideal-observer errors 16.9% and 17.8%. Thus a positive threshold-one geometric certificate is not a 5%-error source-identification result. The calculation gives a conditional worst-case task-error lower bound, not measured accuracy; the source family, covariance, physical forward uncertainty and physiological source reference remain unvalidated. See `../../../research/gbf_omitted_activity_20261024/SUB02_FOUR_HOP_TASK_RISK_RESULTS_20261028.md` and the [measured-endpoint triage](../../../research/gbf_omitted_activity_20261024/MEASURED_SOURCE_ENDPOINT_TRIAGE_20261028.md). This is useful interpretation software built from established convex and Gaussian methods, not a new-method claim or a demonstrated gain over the classical ideal-observer baseline.

A later **post hoc** interpretation of all 24 constructed targets across sub-02 through sub-07 found six cases where the exhaustive distant-point family cleared a 5% fixed-pair Gaussian distance screen but an independently replayed two-patch witness did not. This is a concrete conditional change when the source family is enlarged; it is not a calibrated empirical result, proof of composite point-family classification performance, or a method advantage over standard Gaussian testing. See `../../../research/gbf_omitted_activity_20261024/SECONDARY_SIX_TASK_RISK_RESULTS_20261028.md`.

## Experimental common-prior envelope

The experimental `observable_geometry.track_b.tail_closed.finite_prior_gram_envelope` accepts several competitor sensor Grams sharing one retained operator, whitening convention and coefficient budget. It constructs a conservative PSD upper envelope by candidate-based isotropic inflation; `tail_closed_margin_frontier` can then select one basis against that envelope. This is a feasible finite-family lower certificate, not a globally optimal envelope or a calibrated physiological guarantee. A three-shift, one-model prototype and independent matrix replay are documented in [the prior-envelope result](../../../research/gbf_omitted_activity_20261024/PRIOR_ENVELOPE_RESULTS.md). The shifts produced only mild Gram changes, so the experiment does not establish broad robustness.

The experimental `exact_mimicry_audit` adds a sharper full-rank test. Under a spatially white full-mesh alternative source penalty, a model-only audit found an exact omitted-source alternative for **every** retained GBF combination under the declared unit budget. Equal-trace normalization removes the universal collapse, but the earlier rank-16 basis still fails the exploratory 2% margin. The independent mass-prior Gram recomputation and the assumption boundaries are in [the prior-order result](../../../research/gbf_omitted_activity_20261024/PRIOR_ORDER_STRESS_RESULTS.md). This is prior-conditional finite-model ambiguity, not evidence of biological source identity or a real BCI failure.

The companion experimental `finite_prior_sensor_witness` replays a different kind of certificate: for one retained direction, it checks whether a sensor projection exceeds every declared alternative family's allowed projection. Under equal sensor trace, a nearest-point construction gave tight primal-dual normalized separations `0.66768` and `0.68357` for two fixed directions across the convex hull of p0/p1/p2 Grams. An independent KKT replay verified those fixed-direction calculations. The experimental `construct_finite_prior_sensor_witness` can attempt the same construction for declared inputs and reports whether an anchor bound is attained. A separate raw-prior mixture transition confirms that source-scale assumptions strongly affect the result. See [the mixture and witness report](../../../research/gbf_omitted_activity_20261024/PRIOR_MIXTURE_AND_WITNESS_RESULTS.md). These are one-model, prior-conditional results; no physiological calibration or measured-noise decoding has been established.

The first-order p1 reference prior also yields an explicit model counterexample. Nine retained GBF coefficient directions form a subspace whose unit combinations can all be exactly imitated by omitted sources inside a buffered unit budget. One selected retained pattern and a distinct 8,196-vertex alternative source pattern produce predicted scalp fields matching to below `1e-10` relative error through the original forward leadfield. The experimental `model_mimicry_subspace` reports the coefficient family. See [the smooth-prior counterexample](../../../research/gbf_omitted_activity_20261024/SMOOTH_PRIOR_COUNTEREXAMPLE_RESULTS.md). This is a conditional forward-model ambiguity pair, not evidence that either pattern is physiologically realizable or that a BCI fails on recorded data.

An exploratory follow-up checked a concrete source-map claim on that already selected pair: vertex-squared-energy dominance reverses from right to left while their modeled scalp fields remain nearly equal. The two-point result makes the modeled ambiguity consequential for a specific interpretation, but the claim was inspected after pair selection, the vertex-energy measure is not validated neural power, and the sensor-error threshold is not measured noise. A possible future method is a prospectively specified **claim-first observability audit** that returns either a replayable opposite-claim pair or a global conditional bound. The current work does not yet provide a positive certificate for the **full** source family or demonstrate novelty or researcher decision benefit. See [the claim-reversal audit](../../../research/gbf_omitted_activity_20261024/CLAIM_REVERSAL_AUDIT.md).

A subsequent bounded calculation shows the danger of certifying only inside the truncated representation. With a model-only sensor ball selected around the explicit pair, **every** source in the 40-mode GBF family is certified right dominant by a global quadratic upper bound, while the p1 full-mesh alternative is left dominant and fits inside the same ball. A separate computation replayed the bound and the alternative. This is a correct conditional certificate for the restricted family and an explicit counterexample to extending that claim to the declared omitted-source family. The ball is deliberately tiny and not calibrated to EEG noise, so this is a representation audit, not an empirical localization result. See [the restriction audit](../../../research/gbf_omitted_activity_20261024/RESTRICTION_FALSE_CERTAINTY_RESULTS.md) and [candidate claim-first method](../../../research/gbf_omitted_activity_20261024/CLAIM_FIRST_METHOD_SPEC.md).

A predeclared mode-cutoff grid then showed that all p1 omitted-mode alternatives within the first 300 modes per hemisphere require coefficient norm above one to match the selected modeled field exactly. More importantly, under the **unit** budget, the globally minimum finite-cutoff sensor residual at 300 modes is `1.77887e-5` relative, with an independent primal-dual replay. The explicit full finite-mesh alternative has residual `4.46008e-11` relative and coefficient norm `0.76059`. Hence a model-conditional sensor-tolerance interval exists where tail closure changes the admissible explanation. The interval is not a measured EEG noise interval or a biological resolution guarantee. See [the cutoff and budgeted-residual result](../../../research/gbf_omitted_activity_20261024/SPECTRAL_CUTOFF_ESCAPE_RESULTS.md).

**Physical-scale audit narrows this finding:** the p1 unit coefficient produces implausibly large forward-predicted EEG. Under illustrative source-vector normalizations of 20 and 500 nAm, the finite K=300 residual is far below the saved rank-235 evoked-noise reference; the restricted 40-mode laterality bound also does not survive that reference. Distributed-vector norm is not equivalent to a single dipole moment, so these anchors do not complete physiological calibration, but they rule out presenting this example as a demonstrated practical decision benefit. The live contribution remains a method hypothesis requiring a physically defined source family, calibrated noise/head-model uncertainty and real-data comparison. See [the scale audit](../../../research/gbf_omitted_activity_20261024/PHYSICAL_SCALE_AUDIT_RESULTS.md).

The next focal-source audit makes the proposed researcher use case more concrete while further constraining claims. With four geometry-selected 20 nAm dipoles and this model's evoked covariance, the best **single-source** alternative outside a stated neighborhood can differ sharply from the best **distributed** alternative under the same nominal budget. In several cases, the distributed alternative nearly reproduces the target scalp field by spreading activity across thousands of vertices. The software should therefore report a source-claim's dependence on its alternative family rather than one unqualified “resolution” number. The distributed L2 budget is not a validated neural prior, and the calculation neither recovers true sources nor proves a novel method. The protocol also records a post-run correction: `sqrt(rank)` is a full-vector noise norm, not a pairwise detection threshold. See [the focal source-family result](../../../research/gbf_omitted_activity_20261024/FOCAL_SOURCE_FAMILY_RESULTS.md).

A stricter total-absolute-moment stress test then computed eight exact-match thresholds and 16 certified intervals for the minimum covariance-whitened residual under 20 and 40 nAm budgets. The result exposes why exact mimicry alone is insufficient: one 40 mm-excluded source family needs at least 115.12 nAm for an exact match, yet an alternative capped at 40 nAm comes within 0.576 whitened units. The selected lateral targets show much larger certified residuals under the same stated budget. Both optimization routes and saved source witnesses were replayed. This is a one-model assumption-sensitivity result using an unvalidated mathematical source budget, not clinical resolution or a novel theorem. The proposed tool should expose an explicit budget-versus-residual frontier and both a best competitor and a valid lower bound. See [the total-moment frontier result](../../../research/gbf_omitted_activity_20261024/FOCAL_L1_FRONTIER_RESULTS.md).

An experimental task-level module now translates an explicit opposite-source witness into a conditional algorithm-independent **binary error lower bound** under a specified Gaussian covariance. With one averaged evoked observation, two coordinate-median 20 mm cases yield worst-case lower bounds of 45.2% and 45.6% for focal-versus-distant source-class decisions under the declared total-moment prior. The classical two-point formula is prior art, including neural-sensing information-theoretic bounds in Barnes et al. (2026); the distinct candidate application is a replayable focal-versus-distributed-source claim on the verified participant head model. This has not been validated as physiology or shown to improve researcher decisions. See [the conditional task-level result](../../../research/gbf_omitted_activity_20261024/TASK_LEVEL_IMPOSSIBILITY_RESULTS.md).

The latest anatomical challenge checks that source-family assumption. The strongest L1 median-target counterexamples distribute material coefficients across dozens of disconnected components on the original source mesh. A restricted exhaustive scan of **single uniform connected patches** under the same model and total-moment budgets gives much larger best-match residuals; all 48 selected patches passed direct-field replay. The uniform-weight restriction motivated the broader local-window test below. See [the connected-patch challenge](../../../research/gbf_omitted_activity_20261024/CONNECTED_PATCH_CHALLENGE_RESULTS.md).

A follow-up permits arbitrary signed source coefficients inside one zero-, one- or two-hop **local mesh window**, subject to the same total-moment budget. The preferred corrected family masks excluded vertices individually and scans every window center. Batched primal/dual optimization bounded all 48 nested-family minima within 0.078 covariance-whitened units; a separate original-leadfield replay checked every saved patch state. Two coordinate-median, 40 nAm, 20 mm cases gave corrected two-hop residual intervals [3.931, 3.960] and [3.038, 3.090], versus scattered L1 feasible residuals 0.093 and 0.077. The older 32-case scan excluded whole windows touching the target ball and remains evidence only for that stricter family. This is a one-model source-family sensitivity result, not physiological recovery or mathematical novelty. Standard convex testing over finite unions of convex sets is close prior art, so any new-method claim must be narrower and externally challenged. See [the corrected nested-window result](../../../research/gbf_omitted_activity_20261024/NESTED_PATCH_RESULTS.md) and [the earlier stricter-family result](../../../research/gbf_omitted_activity_20261024/CONNECTED_PATCH_CONVEX_RESULTS.md).

The one-window contrast has now been challenged with a frozen **two-window constructive search**. Keeping the first window fixed and considering 64 deterministic, mutually nonoverlapping second-window candidates, joint fitting under the same combined 40 nAm budget reduced the two coordinate-median residuals to 1.427 and 0.746 whitened units. The right case crossed a prespecified one-unit stress threshold; all 128 saved candidate fields passed independent original-leadfield replay. This is evidence that even two compact patches can materially weaken a one-patch distinguishability claim under this model. It is not the global two-window minimum, a physiological source explanation, or a demonstrated researcher decision gain. See [the two-window falsification result](../../../research/gbf_omitted_activity_20261024/TWO_WINDOW_FALSIFICATION_RESULTS.md).

An exact convex-geometry observation further constrains method design: with arbitrary signed coefficients and a common L1 budget, the convex hull of the allowed `q`-window source family equals the spatially scattered L1 ball for **every** `q≥1`. A global convex relaxation therefore erases patch count and cannot certify a source-complexity frontier by itself. The observation is elementary prior mathematics, not a new theorem. Any proposed new framework must keep the patch disjunction and be compared against existing multi-source, disjunctive-optimization and EEG resolution approaches. See [the convex-hull collapse note](../../../research/gbf_omitted_activity_20261024/CONVEX_HULL_COLLAPSE_NOTE.md).

The global one-window lower bound and feasible two-window upper bound can nevertheless certify a limited **critical patch count** without solving all two-window combinations. For the two coordinate-median cases, the minimum number of windows needed to fit within a declared model tolerance is exactly two on the intervals `[1.426623,3.930595)` and `[0.745716,3.037554)` covariance-whitened units. At the predeclared one-unit stress tolerance, the right case is settled at two, while the left remains unresolved. This is a precise one-model computational finding, not a physiological result, calibrated detectability statement or novel theorem. The research candidate is a source-complexity frontier tool with valid bounds, defensible source/forward assumptions and demonstrated decision value; see [the certificate](../../../research/gbf_omitted_activity_20261024/CRITICAL_COMPLEXITY_CERTIFICATE_RESULTS.md) and [method specification](../../../research/gbf_omitted_activity_20261024/SOURCE_COMPLEXITY_FRONTIER_METHOD_SPEC.md).

An exhaustive **development-library** benchmark now fits all 528 pairs formed from 33 preselected two-hop windows. Its independently replayed finite-library global minimum lies in `[0.665600,0.746164]` whitened units; the earlier feasible witness tightens the upper to 0.745716. This lower bound does not apply to all 8,196 cortical window centers. A separate valid 64-direction dual bank screened only 85/528 pairs against that witness, with median bound zero, so simple cut reuse does not yet offer a credible full-mesh certifier. See [the finite-library benchmark](../../../research/gbf_omitted_activity_20261024/PAIR_LIBRARY_BENCHMARK_RESULTS.md) and [the negative screen result](../../../research/gbf_omitted_activity_20261024/DUAL_BANK_SCREEN_RESULTS.md).

A further **post hoc** cut-transfer diagnostic found that residual directions from the already fitted pairs can screen 526/528 pairs, whereas a direction computed directly from the target field without fitting a pair screens 190/528. Both calculations passed independent original-leadfield replay. This identifies an algorithmic opportunity but not a measured speedup: the strongest directions were obtained after solving every pair. The next required build is a prospective adaptive fit-and-screen algorithm with full solve time and certificate quality compared against exhaustive fitting; safe screening in sparse M/EEG optimization is already established prior art. See [the pair-cut transfer result](../../../research/gbf_omitted_activity_20261024/PAIR_DUAL_TRANSFER_RESULTS.md) and [the zero-fit control](../../../research/gbf_omitted_activity_20261024/TARGET_DIRECTION_SCREEN_RESULTS.md).

That prospective **finite-library** build now exists. Index-order fitting solved 22/528 pairs, screened 506 and independently reproduced the same `[0.665600,0.745716]` interval as exhaustive fitting; three single-machine repeats gave a 2.48 median runtime ratio. However, the earned cuts screened only 6.8 million of 33.6 million possible pairs when transferred to the full 8,196-center mesh. An independent mesh and original-leadfield replay confirmed the 26.8 million unresolved pair count. This is a useful bounded algorithmic prototype and a negative scalability result, **not** a full-mesh `q=2` certificate or a novel-method claim. See [the online finite-library comparison](../../../research/gbf_omitted_activity_20261024/ONLINE_PAIR_CUT_RESULTS.md) and [the full-mesh falsifier](../../../research/gbf_omitted_activity_20261024/FULL_MESH_CUT_INDEX_RESULTS.md).

Follow-up full-mesh tests narrowed the algorithmic boundary further. A scalar shared-moment necessity bound remained weak. Sixty-four spatially spread residual directions from verified one-window fits left 12.68 million pairs; testing a tailored direction at both endpoints left 16.83 million. Even using **all 8,196** one-window residual directions as necessary weak-dual constraints left **8,047,242** pairs, independently replayed from the original leadfield. These negative scaling tests support a pivot away from simple global dual-cut screening toward stronger localized disjunctive bounds, better justified source assumptions or a different researcher decision target. They do not establish that all multi-patch certification is impossible. See [the full one-window cut-bank result](../../../research/gbf_omitted_activity_20261024/ALL_Q1_DUAL_HYPERGRAPH_RESULTS.md) and [method status](../../../research/gbf_omitted_activity_20261024/METHOD_STATUS.md).
