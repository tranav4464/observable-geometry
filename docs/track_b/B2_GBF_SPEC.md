# B2 specification: nominal GBFs source-pattern distinguishability

**Status: frozen v10 specification; the registered v11 CPU64 numerical parity check passed on 24 October 2026.** This is the active GBFs route and replaces the superseded NeuroFlowNet/WBEN specifications as the B2 contract. The supplied review record reports approval for the registered parity computation, but the workspace contains a conflicting AI-authored declaration under the same reviewer name. The human identity and affiliation have not been independently authenticated; see `B2_GATE_CLOSEOUT_20261024.md`. No model fitting, new signal analysis, synthetic neural data, or confirmatory outcome access is authorized by this document.

**Review version:** `B2-GBF-2026-10-23-v10`. This version adds two directly relevant prior-art sources to the comparison boundary; the v9 numerical tolerance correction is retained.

## Decision and scope

The software answers a narrow, pre-data question for one declared participant-specific forward model: **which spatially separated, single-source hypotheses predict similar scalp voltage patterns after applying the same sensor reference and noise weighting?** The output is a ranked list of model-predicted alternatives for each cortical source location. It helps an analyst see when a location has distant alternatives with similar predicted scalp patterns before describing an inverse estimate as spatially unique.

This is not a classifier of actual brain sources. It does not estimate a probability that the brain used a location, an empirical localization error, the number of active sources, or the spatial resolution of EEG for all tasks. The Localize-MI contact pair is a reference for the measured stimulation-pulse artifact only. It is not ground truth for a distributed physiological response.

The active deliverable is a reproducible GBFs implementation and an inspectable real-data workflow. The pairwise cosine and source-separability question have substantial prior art. No novelty claim is retained. The implementation may be useful as software without being a new mathematical method.

The GBFs inverse and this diagnostic are separate computations. The GBFs estimate uses its geometric-mode basis to represent source activity. The pairwise score below instead compares columns of the vertex-level fixed-orientation forward matrix `G` directly; it does not apply the GBFs basis or inverse operator. It shares the same participant anatomy, source mesh, and sensor model, but the score is not an output or equation of the GBFs estimator.

## Frozen development case and information boundary

- Dataset: Localize-MI, local snapshot `d7a123d3067213281f106b343c71f28c30e4dd60`, CC-BY-NC-SA 4.0.
- Participant and event: `sub-01`, `run-01`, K13–K14, 1 mA single-pulse stimulation; 38 recorded epochs, 8 kHz, epoch −250 ms to +10 ms.
- Sensors: 236 good EEG channels in the forward-solution order; recorded unit V. The same average-reference projection is applied to data, leadfield, and covariance.
- Noise contract: pooled pre-event interval −200 ms to −50 ms and 10% diagonal shrinkage, followed in Track A by division by 38 for the evoked average as documented in the frozen protocol. For the primary normalized pairwise score, this global division by 38 has no effect: replacing `C` by `C/38` scales every whitened signature by `√38`, which cancels when each signature is normalized. The score still depends on the covariance's shape. Cross-trial covariance was not measured, so the single-trial covariance shape may not fully represent noise in the evoked average; the saved absolute whitened norms also depend on the scale convention. Do not interpret the trial-count scaling as changing the primary similarity ranking.
- Source family: the supplied participant-specific FIF is originally free-orientation: 256 sensors by 24,588 dipole components for 8,196 cortical vertices. Track A first picks the 236 good EEG channels in the frozen order, then calls `mne.convert_forward_solution(..., surf_ori=True, force_fixed=True, use_cps=True)` using MNE 1.13.2. This derives a surface-orientation, fixed cortical-normal leadfield with one column per vertex (236 × 8,196). `use_cps=True` uses cortical patch statistics to define surface-normal orientations. Each candidate is a single focal source at one vertex in that derived leadfield; all other source coefficients are zero. The actual transformation and dimensions are recorded in the [B2 orientation audit](../../outputs/track_b/20261023T_b2_gbf_orientation_audit/orientation_audit.json). This family does not include arbitrary distributed source configurations or unknown orientations.
- Geometry: source coordinates are in metres in the supplied surface frame. For candidate pairs, Euclidean distance in those coordinates is converted to millimetres. The reported “distant” set uses distance **at least 20 mm**. This is a Euclidean cutoff, not cortical geodesic distance; conclusions depend on the cutoff.
- The case is development-only. It was used in the sealed Track A foundation and cannot be described as held-out or confirmatory. The B1 audit records that the target contact midpoint is valid only for pulse-artifact localization.

Authoritative case and release evidence: [`B1 audit`](../../outputs/track_b/20261023T_b1_gbf_case_audit/case_audit.json), [`case validation`](../../outputs/b1_gbf_case_validation_20261023/case_validation.json), and [`sealed Track A manifest`](../../outputs/tracka_release_20261022_v2/run_manifest.json).

## Mathematical contract

Let `G ∈ R^(m×n)` be the **derived** surface-normal fixed-orientation leadfield for `m = 236` retained scalp channels and `n = 8,196` cortical vertices. The raw FIF is free-orientation; `G` is produced by the MNE conversion above after channel selection. Column `g_i` is the predicted sensor voltage pattern per source coefficient in the converted forward file's fixed-dipole units at vertex `i`; the local artifact describes these as “forward-defined fixed dipole units,” and the absolute source coefficient scale is removed by normalization. EEG data are in V, so `C ∈ R^(m×m)` is in V² after the frozen reference and evoked-noise scaling. Source coordinates are in metres; distances in the report are in millimetres. `C` is the positive-semidefinite covariance of evoked sensor noise under the frozen protocol.

Use the eigendecomposition `C = U Λ Uᵀ`. Retain eigenvalues `λ_k > 10⁻¹⁰ λ_max`; call the retained eigenvectors `U_r` and eigenvalues `Λ_r`. Before whitening, reject a leadfield column if its component in the discarded covariance nullspace exceeds `10⁻⁷` times its Euclidean norm. This prevents silently deleting deterministic modelled signal directions. For accepted columns:

```text
z_i = Λ_r^(-1/2) U_rᵀ g_i
s_i = ||z_i||₂
u_i = z_i / s_i, when s_i > 10⁻¹⁰ max_j(s_j)
```

For two valid source hypotheses `i,j`, define the nominal similarity

```text
ρᵢⱼ = |u_iᵀ u_j|,       0 ≤ ρᵢⱼ ≤ 1.
```

This is the absolute cosine between noise-whitened, unit-norm sensor signatures. Unit normalization removes source-amplitude scale; the absolute value treats polarity as a nuisance. Equivalently, it is the best-fit residual for explaining one normalized signature by an unrestricted scalar multiple of the other:

```text
min_a ||u_i − a u_j||₂ = sqrt(1 − ρᵢⱼ²),       a ∈ R.
```

The complement is an algebraic residual at **unit whitened signature norm**. It is not a probability, Bayes error, calibrated localization uncertainty, or an error in millimetres. The whitening depends on the stated covariance; the signatures depend on the selected head model, source orientations, reference, and channel set.

The score is invariant to a positive global covariance rescaling. If `C' = C/N`, then `z'_i = √N z_i`, so `u'_i = u_i`, `ρ'ᵢⱼ = ρᵢⱼ`, and the profiled residual is unchanged. This invariance applies only to a scalar rescaling; changing covariance structure or its supported subspace can change the score.

### Hand-worked geometry and limiting cases

This two-dimensional example illustrates only the algebra; it is not a neural recording or a simulated EEG result. Let the two normalized whitened signatures be `u₁ = (1, 0)` and `u₂ = (cos θ, sin θ)`. Then `ρ₁₂ = |cos θ|` and the profiled residual is `|sin θ|`. If `θ = 0` or `π`, the patterns are identical up to polarity and amplitude (`ρ = 1`, residual `0`). If `θ = π/2`, they are orthogonal in the supported whitened sensor space (`ρ = 0`, residual `1`). These are exact geometrical endpoints, not claims about real EEG performance. Even for these endpoints, a physical source pair is included in the report only if its coordinate separation meets the 20 mm rule.

If the full covariance is multiplied by any positive scalar `a`, then each whitened vector is multiplied by `1/√a`; after unit normalization, every `u_i` and `ρ_ij` is unchanged. Thus dividing the covariance by the number of averaged trials does not itself alter this cosine score. Changing covariance shape, such as through diagonal shrinkage or a different noise estimate, can change the directions after whitening and therefore can change the score. The covariance scaling remains recorded for reproducibility and comparator matching.

### Pair eligibility and output

For every valid query vertex `i`, consider valid `j` only when `j ≠ i` and Euclidean coordinate distance `d_ij ≥ 20 mm`. Sort by descending `ρᵢⱼ`, breaking ties by source index. Return the top five alternatives, with source IDs, coordinates, distance, score, and validity/provenance. A query without enough eligible alternatives returns the available entries and explicit `-1`/`NaN` sentinels; a dataset with no valid query having any eligible alternative is an error. The current API also supports an optional complete per-query set for a caller-specified `ρ` cutoff, stored in CSR form.

The fixed Track A report convention is to display the fractions of vertices whose best eligible match is at least `0.95` or `0.99`, along with median and 90th percentile best-match similarity. These are descriptive visualization thresholds inherited from the existing foundation. They are **not** empirically calibrated decision thresholds and must not be described as probability cutoffs. The primary output remains the continuous score and ranked alternatives; there is no binary “EEG can/cannot distinguish” classification in this specification. The current sealed signature library stores pair scores as float32; a new Track B API must preserve float64 scores (or document any downcast explicitly), and comparison to the sealed float32 library must account for that quantization.

### Researcher-facing interpretation

For a location with a high-scoring alternative at least 20 mm away, the report should say: “Under this head model, reference, source family, and covariance, these two focal-source hypotheses produce similar normalized scalp patterns.” It may prompt the analyst to report the alternative or avoid claiming unique localization from that model alone. It must not say the two sources are biologically equivalent or that actual recordings cannot distinguish them at every signal amplitude, time course, or experimental condition.

The software does not yet prove this output improves a research decision. B7 remains responsible for testing that practical value. A clearer map alone is insufficient evidence of utility.

## Comparators and prior-art relationship

1. **GBFs reproduction.** The pinned upstream revision is `99fc7c6e8afbd2e3e68a700c5f1fa1483b90f49e` under BSD 3-Clause. Track A reports relative Frobenius parity `2.2314636763005833e-13` on the selected Localize-MI inputs. This is same-input implementation parity, not full reproduction of the paper's benchmarks. The original GBFs inverse and the project diagnostic must remain visibly separate.
2. **MNE minimum-norm resolution diagnostic.** The existing comparison uses fixed orientation, `lambda2=1/9`, no depth weighting, the same reference, channel set, and covariance. The resolution matrix `R = K G` yields point-spread columns and cross-talk rows. Compare the spatial behavior and top-location alternatives under matched source space and sensor contract. Do not compare `ρ` numerically as though it were the same estimand as PSF/CTF spread or localization error. The existing report is nominal and not measured accuracy.
3. **Published prior art.** Pascual-Marqui and Biscay-Lirio (1993, [DOI](https://doi.org/10.3109/00207459308994264)) introduced information functionals for EEG/MEG source resolution, including one based on the angle between measurement patterns from different sources. This is direct conceptual prior art for angular sensor-pattern distinguishability, although it is not the same exact noise-whitened, polarity-invariant normalized cosine or participant-specific software output used here. Two-source EEG separability under noise and source spacing is established by Kalogianni et al. (2018, [DOI](https://doi.org/10.1016/j.jneumeth.2018.02.016)). Resolution matrices, point-spread and cross-talk functions are established by Hauk et al. (2022, [DOI](https://doi.org/10.1016/j.neuroimage.2022.119177)). Scherg et al. (2022, [Relative Source Power](https://doi.org/10.1016/j.clinph.2021.10.005)) explicitly normalize leadfield vectors and use their cross-correlation matrix in an inverse localization method, a close mathematical overlap with normalized column comparisons. Forward-model uncertainty is established by Stenroos and colleagues ([2009 paper record](https://www2.imm.dtu.dk/pubdb/pubs/6017-full.html); [2010 DOI](https://doi.org/10.1007/s11265-010-0527-0)). More recent conductivity sensitivity work uses generalized polynomial chaos and 1,000 conductivity sets to map forward-topography and source-localization changes (Vorwerk et al. 2024, [DOI](https://doi.org/10.3389/fnhum.2024.1335212)). This rules out an ensemble or sensitivity map by itself as a new method. The broader ambiguity of EEG/MEG inverse inference is longstanding (Wan et al. 2008, [open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6871235/), DOI [10.1002/hbm.20424](https://doi.org/10.1002/hbm.20424)).

The exact cosine calculation is a standard leadfield-similarity/separability diagnostic. The MNE resolution output and cosine answer related but non-identical questions: the former describes an inverse operator's response to sources; the latter compares forward sensor signatures before inversion. Their comparison is a transparent software report, not evidence that either is ground truth.

## Assumptions, edge cases, and failure handling

- **Fixed orientation:** each source uses the MNE-derived surface-normal orientation with cortical patch statistics, as specified above. The raw supplied FIF is free-orientation; the fixed-orientation column is a deterministic derived representation, not its original state. This choice excludes unknown-orientation hypotheses and must be reported as a modeling assumption.
- **Common covariance:** both hypotheses are whitened with the same `C`. The covariance must be finite, symmetric within the existing numerical tolerance, positive semidefinite, and have nonzero supported rank.
- **Rank deficiency:** only the supported covariance subspace is whitened. A leadfield component outside it beyond tolerance is an explicit error, not projected away.
- **Degenerate source columns:** a column with zero or relatively negligible whitened norm is invalid and cannot be reported as a distinguishable source.
- **Spatial cutoff:** 20 mm is a reporting choice; Euclidean surface-coordinate distance can differ from geodesic cortical distance. Report it in every result and avoid calling it a minimum resolvable distance.
- **Non-transitivity:** high similarity is pairwise. If A resembles B and B resembles C, this does not imply A resembles C. Do not turn pairwise edges into equivalence classes without a separately defined and validated clustering rule.
- **Amplitude/SNR:** normalization deliberately removes absolute signal scale. The tool cannot predict actual discrimination at an arbitrary physical amplitude or trial count.
- **Forward uncertainty:** none is integrated or averaged. All statements are conditional on the one verified forward model. An ensemble is not part of B2 and cannot be added as a novelty claim by itself.
- **Pulse artifact:** known contacts support only the dataset's artifact-localization reference task; they do not validate endogenous cortical source recovery.
- **Numerical precision:** CPU float64 is the correctness reference. GPU execution is optional and cannot replace CPU checks or alter the scientific interpretation.

## Verification plan and falsification

This specification is checked against `src/observable_geometry/nominal.py`, the frozen [`FOUNDATION_PROTOCOL.md`](../FOUNDATION_PROTOCOL.md), the existing [`test_nominal.py`](../../tests/test_nominal.py), the [metadata-only orientation audit](../../outputs/track_b/20261023T_b2_gbf_orientation_audit/orientation_audit.json), and the sealed real-data outputs. MNE documents that `force_fixed=True` selects fixed source orientations, implies a surface-based source coordinate system, and that `use_cps` uses cortical patch statistics to define surface normals ([MNE 1.13.2 API](https://mne.tools/stable/generated/mne.convert_forward_solution.html)). Those unit tests use small algebraic matrices solely to check code invariants; they are not neural simulations or evidence of scientific performance. The B2 data audit must remain limited to already permitted real Track A artifacts and the B1 case record.

Before B2 can pass, an independent technical reviewer must inspect the estimand, equations, unit/reference/covariance contract, implementation-to-equation mapping, comparator interpretation, and claim boundary. After that review and resolution of findings, recompute the continuous score from the saved permitted real forward-model artifacts in CPU float64 and compare it with an independently written implementation. Record the run and hashes without modifying the sealed Track A release. No new signal outcomes or additional participant data are needed for this arithmetic/parity check.

The comparison tolerances are fixed before that run: the validity mask, eligible-candidate counts, and top-five source indices must match exactly; float64 cosine values must differ from the sealed float32 scores by at most `1e-7` absolute; whitened norms must match the sealed float64 values at `rtol=1e-8`, `atol=1e-15`. A ranking mismatch is reported as a failure even if its scores fall within the numeric value tolerance, because it changes the selected alternative.

The profiled residual is `r = sqrt(max(0, 1−ρ²))`. Because the square root is ill-conditioned as `ρ` approaches 1, do not apply the cosine's `1e-7` tolerance directly to residuals stored in float32. The new float64 result must calculate the residual from the unrounded float64 cosine. To verify the sealed Track A residual implementation, separately cast the independently computed cosine to float32, replay the legacy float32 residual expression, and require its maximum absolute difference from the sealed float32 residual array to be at most `1e-7`. Report the difference between the unrounded float64 residual and sealed float32 residual descriptively, without using it as a pass/fail criterion. Investigate rather than silently waive any failure. Retain float64 in the new output.

The specification is falsified or must be revised if any of the following holds:

1. Source orientation, channel order, reference, covariance scale/support, or coordinate units in the saved inputs do not match the contract.
2. The independent implementation disagrees beyond a preregistered float64 tolerance or any declared invariant fails.
3. The output is presented as calibrated source recovery, empirical localization error, or a probability without a separately validated observation model.
4. The claimed decision value is only a relabeling of standard pairwise similarity or MNE resolution outputs. In that case retain the faithful GBFs reproduction and inspectable report; drop any distinct-method or utility claim.

## B2 closeout reference

The registered v11 CPU64 calculation passed the frozen comparisons recorded in `B2_GATE_CLOSEOUT_20261024.md`. The project gate register records B2 **PASS** for that bounded specification and numerical-reproducibility scope. The conflicting reviewer-identity records and malformed digest remain disclosed; readers must not interpret the supplied approval as independently authenticated. This closeout does not establish physiological recovery, empirical localization accuracy, a calibrated uncertainty estimate, or generalization. No confirmatory analysis is defined in this specification; any broader real-data evaluation requires a separate feasibility decision and locked protocol.
