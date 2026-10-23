# B1 layered-conductor feasibility and source-generator check

**22 October 2026. Development participant sub-01 only. B1 remains open.** This is an explicit failure audit, not a source-recovery result. No sub-02 through sub-07 EEG values or pair-confusion outcomes were read.

## Geometry and numerical chain

The supplied sub-01 GIFTI meshes contain 10,242 vertices each for inner skull, outer skull and outer skin. `scripts/track_b/prepare_sub01_bem.py` checked finite vertices, face bounds, closed-manifold edges and oriented volume, converted the meshes to FreeSurfer geometry, and built an MNE three-layer BEM with **642 vertices / 1,280 triangles per shell** at ico-3. The assumed conductivities are brain **0.3**, skull **0.006**, scalp **0.3 S/m**. The candidate solution is `outputs/track_b/development/sub01_bem_feasibility/bem_ico3_solution.fif` (SHA-256 `704729E6B15752A996C7C4365F6C03060B1686057B1A56DA1FE5FFA05632C80F`). These are assumptions, not fitted participant conductivities. MNE's [head-model tutorial](https://mne.tools/stable/auto_tutorials/forward/30_forward.html) explains the three-layer EEG BEM workflow.

`scripts/track_b/check_sub01_bem_forward.py` regenerated free-orientation dipole lead fields at six preselected cortical grid points using the candidate BEM and the supplied channel/head transform. The downsampled inner-skull boundary excluded one of the six points, so it is reported rather than silently removed. At the other five points, the smallest canonical correlation between each regenerated and supplied three-dimensional lead-field subspace was **0.958**. This is a coordinate/solver plausibility check, not proof of exact conductivity, source physics or stimulation-artifact fit. The raw comparison is in `outputs/track_b/development/sub01_bem_feasibility/forward_comparison_ico3.json`.

A mesh-resolution sensitivity check built an ico-4 solution with **2,562 vertices / 5,120 triangles per shell** and repeated the same six fixed comparisons. It retained all six source points. Five had minimum canonical correlations from **0.964 to 0.984**, while source index 4000 had a minimum of **0.338** (the other two correlations there were 0.985 and 0.974). Ico-3 had excluded that point at its downsampled inner-skull boundary. In the original full-resolution inner-skull mesh, this source is only **0.90 mm from its nearest mesh vertex** (Euclidean vertex distance; not a signed point-to-triangle distance). That makes a boundary-sensitive geometry edge case plausible, but does not establish it as the cause of the orientation mismatch. The higher-resolution mesh therefore does not establish a uniformly matching head model; the outlier remains disclosed rather than hidden by reporting only the other five. The comparison report is `outputs/track_b/development/sub01_bem_feasibility/forward_comparison_ico4.json`. The GPU is visible to the machine, but MNE 1.13.2 reports CUDA disabled and neither CuPy nor PyTorch is installed in the Track A environment; these BEM solves therefore ran on CPU. GPU availability does not change the scientific interpretation.

For a source contact `a` and sink contact `b`, the candidate model integrates infinitesimal current-dipole lead fields along their connecting line. Gauss-Legendre quadrature uses three and nine nodes. `tests/test_track_b_physical.py` verifies analytically that this line integral reproduces a source-sink potential in an infinite homogeneous conductor. The MNE BEM calculation incorporates isotropic layered boundaries; it is still a point-contact approximation, not an electrode-contact FEM. The contact TSV positions are **already in metres**. A first development run divided them by 1,000 a second time and produced invalid output. That artifact is retained as `outputs/track_b/development/sub01_layered_adequacy_contiguous_INVALID_UNITS.json` and must never be cited as a scientific result. The script now rejects implausible contact gaps before solving.

## Equal-split sub-01 result

Each model uses the same training-selected pulse time, fixed good-channel intersection, average reference and training-baseline covariance whitener. Its scale is fitted on training trials; R² and residuals are scored on held-out trials within the same runs. Two splits were run: alternating trials and first-half/second-half contiguous trials.

| Candidate sensor model | Median held-out whitened R², alternating | Median R², contiguous |
|---|---:|---:|
| Fixed cortical-normal dipole | 0.162 | 0.173 |
| Infinite homogeneous bipolar point sources | 0.533 | 0.549 |
| Contact-axis equivalent dipole | 0.577 | 0.597 |
| Layered BEM source-sink line, 9 nodes | 0.568 | 0.600 |
| Fitted free-orientation dipole, 3 parameters | 0.615 | 0.651 |

The three- and nine-node layered R² values differ by at most **4.7×10⁻⁷** across the six sites in the contiguous split, so integration resolution is not the explanation for the modest fit. The layered model's median signed train/test residual cosine is **0.999** on that split. Its within-site residual is reproducible, whereas cross-site residual topographies vary (median signed cosine approximately **0.385** across the 15 dependent pairs). A realistic three-layer conductor plus ideal point source/sink **does not remove the systematic residual** in this development case. The site-level values are in `outputs/track_b/development/sub01_layered_adequacy_contiguous.json` and `sub01_layered_adequacy_alternating.json`.

## Decision and falsification boundary

The numerical chain supports a *feasible* participant-specific BEM and a well-converged line-integral implementation. It does **not** validate any current source representation for the recorded pulse artifact. Possible missing factors include tissue anisotropy, actual contact size/current distribution, imperfect conductivity, recording hardware effects and pulse-time processing. These are hypotheses, not diagnoses from this test.

Route P cannot use this generator to assert cortical-source recoverability or calibrated ambiguity at present. The next B1 decision is whether a tractable, independently defensible injection/recording model can remove the structured residual without fitting a separate arbitrary template to every known site. If not, Route P must be narrowed to sensor-level artifact discrimination or retired in favor of a separately validated physiological task. The B0 novelty audit remains independent and unresolved.
