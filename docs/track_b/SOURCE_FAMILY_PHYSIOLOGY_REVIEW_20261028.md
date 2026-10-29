# Source-family physiology review for the WSGZP observability test

**Status:** candidate-model justification; not a frozen protocol and not a
claim that any family is the true CCEP generator.\
**Signal access:** none. This review uses primary literature and existing
source-model documentation only.

## Why source-family assumptions matter

An unrestricted signed current at every cortical vertex can fit many sensor
patterns, but that flexibility does not make every fit a physiologically
equally plausible explanation. Conversely, a single focal dipole or one
uniform patch can be too restrictive for a distributed evoked response. The
candidate set should span interpretable assumptions and label them honestly:
some are structured source models, while the fully signed model is best
treated as an adversarial flexibility bound unless further physiological
evidence justifies it.

The relevant EEG/MEG forward relation is linear, `y(t) = A j(t) + e(t)`, but
the map `A` depends on participant anatomy, sensor placement, reference and
conductivity. The spatial normal of the cortical surface gives a fixed local
orientation for each source element; it does not imply that every vertex's
current amplitude or temporal phase must be identical.

## What the literature supports

* Ahlfors et al. model extended and distributed cortical sources on
  anatomically reconstructed surfaces and show that simultaneously active
  sources can cancel in scalp EEG/MEG, including within patches spanning
  opposing sulcal/gyral orientations. Their forward relation is linear
  (`v = A q`); the cancellation depends on source arrangement and cortical
  geometry. This supports testing geometry-aware patch families and
  cancellation, not assuming a single source map is observable.
  [Ahlfors et al., *Human Brain Mapping* (2010), DOI 10.1002/hbm.20851](https://doi.org/10.1002/hbm.20851).
* Irimia et al. quantify cancellation and orientation disparity for
  contiguous patches across cortical locations and patch radii. They model
  source elements with cortical-surface orientation and equal strength for
  their forward sensitivity analysis. The result makes patch size and local
  folding material to EEG observability. Their enhancement index is
  `I_E = ||Σ_j δ_j a_j|| / Σ_j δ_j ||a_j||`; their orientation-disparity
  index is `I_O = 1 − ||Σ_j δ_j n_j|| / Σ_j δ_j`, where `a_j` is the sensor
  field from element `j`, `n_j` its cortical normal, and `δ_j` its patch-area
  weight. This is close prior art for geometry-dependent patch cancellation;
  computing a similar index is not a novel contribution.
  [Irimia et al., *NeuroImage* (2012), DOI 10.1016/j.neuroimage.2011.08.104](https://doi.org/10.1016/j.neuroimage.2011.08.104).
* Lütkenhöner et al. evaluate the cortical patch method, which constrains
  source extent with anatomical and physiological information rather than
  relying only on a generic mathematical penalty. This establishes that
  structured patch estimation is prior art; it does not validate our exact
  constraints or CCEP application.
  [Lütkenhöner et al., PubMed record](https://pubmed.ncbi.nlm.nih.gov/10619413/).
* Modern patch source models include spatial smoothness and temporal
  low-rank/coherence assumptions because patch extent and activity are
  underdetermined by sensor count. These are model assumptions to test, not
  independent evidence that the resulting patch is the biological source.
  [Giri et al., PATCH-AP, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12700762/).
* MRI-informed source-model work supports local cortical-normal orientations
  as a useful approximation, while emphasizing that EEG may arise from
  compact, regional or broadly distributed sources and that extent is usually
  unknown. A focal source assumption can be appropriate for some short-latency
  sensory responses or epileptic discharges, but is not a universal EEG
  physiology rule. [Srinivasan, *Technol Cancer Res Treat* (2006)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1995010/).
* Pyramidal-cell modeling shows that net dipole magnitude and direction depend
  on synaptic input location along dendrites; modeled input across the soma
  reversal point can reverse dipole direction, and inhibitory input may
  suppress or enhance the dipole depending on synapse placement. This is
  cell-level evidence, not direct evidence for sign changes over a millimetre-
  scale CCEP patch, but it cautions against treating equal patch amplitude or
  polarity as established. [Ahlfors & Wreh (2015)](https://doi.org/10.1007/s11517-015-1296-5).

Together, this literature supports a *family of explicit structural
alternatives*: focal sources, contiguous patches tied to cortical geometry,
several local patches, and more flexible distributed currents. It does not
establish which family should explain a particular WSGZP late response.

The evidence supports cortical orientation and possible spatial extent more
strongly than the coefficient restrictions used below. Uniform local-normal
polarity has precedent in forward simulations of patch cancellation, but this
does not demonstrate that a late CCEP response follows that pattern. A
coherent patch is a structured comparator, not a default truth. Smooth
variation and multiple patches with separate time courses should remain
available. Within-patch sign freedom remains an adversarial flexibility case
until its physiology is justified. All families must use vertex-area weights
so mesh density cannot silently change their effective source mass.

## Candidate operational definitions

These definitions are proposed for preregistration review. They must be
implemented on each participant's cortical mesh with fixed local source
orientations and vertex-area weighting. Do not call them physiology-validated
until the measured-data and prior-art gates pass.

| Family | Candidate parameterization | Interpretation and caution |
|---|---|---|
| **Point** | One fixed-orientation cortical dipole, `j(v,t)=a s(t)` at one vertex/parcel. | Established focal baseline; a convenient equivalent-source model, not a literal single-neuron claim. |
| **Uniform contiguous patch** | Connected support `P`; source density `J(v,t)=c s(t)` for `v∈P`, zero outside, with `c≥0` and free time course `s(t)`. Discretize as vertex moment `j_v(t)=A_v c s(t)` using vertex area `A_v`. | Tests one coherent density patch. The time course may change sign; at a given time, all local-normal coefficients share polarity. This is a structured comparator with cancellation precedent, not an established late-CCEP pattern. Patch area must be preregistered or swept by a frozen rule. |
| **Smooth contiguous patch** | Connected support `P`; source density `J(v,t)=a(v)s(t)`, `a(v)≥0`, with a frozen area-weighted mesh-Laplacian or bounded-gradient constraint; discretize with `A_v`. | Allows smooth spatial variation while retaining one coherent temporal waveform. Smoothness and nonnegative spatial amplitude are priors; test their sensitivity under a frozen rule. |
| **Multi-patch** | `J(v,t)=Σ_r a_r(v)s_r(t)`, with each `a_r≥0` supported on a connected patch and area-weighted discretization; each patch has its own time course. | Allows separate regions and relative phase/polarity between patches. Patch count, minimum area/separation, overlap, area weights and temporal rank must be fixed. |
| **Signed distributed** | Vertex-wise signed amplitudes, with only a fixed norm/energy constraint. | Flexible stress-test family. It may include within-patch sign reversals that are not justified by a coherent-patch model; treat as an adversarial envelope, not automatically as a likely physiological explanation. |
| **Flexible constrained** | A frozen union or regularized combination of connected support, surface smoothness, area/moment budget and temporal-rank constraints. | Candidate superset for the audit. Every added degree of freedom needs an explicit rationale; otherwise it can trivially absorb noise and destroy useful discrimination. |

For distributed families, `J_v(t)` denotes current density and the integrated
vertex moment is `j_v(t)=A_v J_v(t)`. A total absolute-moment budget is
therefore `Σ_v ||j_v|| = Σ_v A_v ||J_v||`; a density-energy penalty is
`Σ_v A_v ||J_v||²`. Smoothness penalties likewise need surface-area-aware
mesh weights. If a constraint is written directly on integrated moments
`j_v`, do not multiply by `A_v` a second time. This convention prevents a
denser mesh region from receiving extra weight merely because it has more
vertices.

For fixed cortical-normal orientations, a common scalar polarity over a local
patch means current is aligned with or against each vertex's *local* normal.
Because local normals turn across sulci, those currents can still point in
opposite global directions and partially cancel. A second patch may have a
different time course or polarity. Therefore “one sign per patch” is not the
same as “all dipoles point in the same 3-D direction.”

This sign rule remains a scale-dependent modeling choice. The dendritic-input
study shows that synaptic placement can reverse a cell's net dipole, but it
does not show arbitrary independent sign changes among vertices of a
millimetre-scale patch. Conversely, cortical-normal orientation does not prove
that every source within such a patch has a common coefficient sign. Compare
patch-size and within-patch sign/smoothness constraints and report which
inferences survive; do not select the constraint that gives the preferred
result.

## What the existing sign-coherence result does and does not show

The prior two-window calculations found that a selected unrestricted signed
two-patch fit could mimic a modeled focal field more closely than the tested
one-sign-per-patch fits on a frozen candidate set. This is a useful warning
that the inverse conclusion depends on within-patch sign freedom. It is not
measured neural evidence, does not establish the correct CCEP family, and is
not a global exclusion over the full cortex. Preserve it as a model-level
stress test only; do not cite it as proof of physiological source
observability.

The new measured-data test should compare these definitions only after fixing
the following prospectively: cortical mesh and normals, area weights, patch
connectedness, patch-size/area range, coefficient/time-course rank,
orientation convention, temporal response window, covariance and bounded
forward scenarios. Under the current v4 WSGZP amendment, each held-out
participant's released scalp field is the inference input; residuals on that
same field are compatibility fits, not independent predictions. Score held-out
predictions only if an independent same-condition repetition and permissible
split are authoritatively documented. Keep fit flexibility and external
SEEG-positive concordance separate. The proposed fixed-area priority-map
capture test may be the primary external decision-value endpoint, but SEEG
must not select supports, define whole-cortex truth, or validate the
unique/ambiguous/unsupported label. It measures sampled-positive concordance
only.

## Falsification and novelty consequences

1. If an independent held-out coherent-patch prediction test becomes
   possible and fails against zero-response/prestimulus controls, it is not a
   useful predictive CCEP family in that task. An in-observation fit alone
   cannot establish prediction quality.
2. If only the unrestricted signed family predicts well, the result is that
   this flexible representation is needed for predictive fit; it does not
   prove its within-patch sign changes are physiological.
3. If direct constrained fitting, established patch estimators and the
   proposed report give the same held-out compatibility report, this is not a
   new-method advantage unless a separate certified computational gain is
   demonstrated. SEEG-positive capture evaluates only the separately frozen
   priority map, not correctness of the ambiguity label.
4. If source-family conclusions change with reasonable patch size,
   temporal-rank, polarity or forward-error choices, report that sensitivity
   rather than choosing the family that produces a desired novelty result.
5. A novel method still requires a new mathematical step/guarantee absent
   from patch-source, cancellation, robust-inverse and set-valued-recovery
   literature plus a held-out measured-data decision benefit.

## References

* Ahlfors SP, Han J, Belliveau JW, Hämäläinen MS. Cancellation of EEG and MEG
  signals generated by extended and distributed sources. *Human Brain
  Mapping*. 2010;31(1):140–149. [DOI 10.1002/hbm.20851](https://doi.org/10.1002/hbm.20851).
* Irimia A, Van Horn JD, Halgren E. Source Cancellation Profiles of
  Electroencephalography and Magnetoencephalography. *NeuroImage*.
  2012;59(3):2464–2474. [DOI 10.1016/j.neuroimage.2011.08.104](https://doi.org/10.1016/j.neuroimage.2011.08.104).
* Lütkenhöner B, Lammertmann C, Hoke M. Modeling extended sources of
  event-related potentials using anatomical and physiological constraints.
  [PubMed](https://pubmed.ncbi.nlm.nih.gov/10619413/).
* Giri A, et al. Localization of Realistic Spatial Patches of Complex Source
  Activity in MEG and EEG. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12700762/).
* Srinivasan R. Anatomical constraints on source models for high-resolution
  EEG and MEG derived from MRI. *Technol Cancer Res Treat*. 2006;5(4):389–399.
  [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC1995010/).
* Ahlfors SP, Wreh C. Modeling the effect of dendritic input location on MEG
  and EEG source dipoles. *Med Biol Eng Comput*. 2015;53(9):879–887.
  [DOI](https://doi.org/10.1007/s11517-015-1296-5).
