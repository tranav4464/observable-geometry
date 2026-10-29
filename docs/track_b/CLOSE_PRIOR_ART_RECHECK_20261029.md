# Close prior-art recheck: source observability and null-space methods

**Checked:** 29 October 2026
**Scope:** Primary arXiv records and the authors' CANDLE project page; targeted recheck for work close to Observable Geometry's observability and source-family claims.

## Finding

Two 2026 preprints make explicit observable/null-space decomposition a crowded and rapidly moving area. They do not implement the same estimand as Observable Geometry, but they substantially narrow any defensible claim about source observability, null-space analysis, or a general new EEG source-imaging framework.

## CANDLE (arXiv:2610.07824)

CANDLE defines the lead-field source-space projectors

```text
L_r = L† L
L_n = I - L† L
```

and reconstructs a source map as a pseudoinverse-derived row/range component plus a learned, projected null-space component. Its stated contribution is a subject-geometry-aware learned ESI model and a whole-brain simulator, not a set-valued distinguishability certificate. The paper reports simulation results over 1,113 geometries and 26,273 statistical brain maps, then evaluates intracranial stimulation localization on 32 patients / 291 runs and epileptogenic-zone estimates on 22 patients. It reports no significant difference from GBF on two SPES comparisons, although it reports advantages over several other baselines and condition-specific depth results. Its empirical stimulation dataset is Parmigiani et al. (2022), which is also a central dataset in the GBF/WSGZP line; it is therefore not an independent cohort relative to that prior work.

**Overlap with Observable Geometry:** both use participant-specific lead-field geometry to reason about what scalp data constrain. This preprint makes clear that row/null decomposition, geometry-aware handling of unobservable components, and empirical stimulation localization cannot be claimed as new by themselves.

**Difference:** CANDLE returns a single plausible source reconstruction using learned priors. Observable Geometry's declared object is instead a conditional comparison of multiple declared source families under a fixed forward/noise model, with explicit ambiguity and replayable bounds. That distinction is real at the estimand level, but it does not establish a new method or usefulness. Current direct constrained fitting produces equivalent family decisions, and the held-out WSGZP decision test is not eligible; therefore no advantage over CANDLE or other source-imaging baselines has been shown.

**Audit consequence:** include CANDLE in any claim-level comparison and, if data/protocol gates are eventually cleared, compare the same participant/run outputs against it only where a fair implementation and shared endpoint are possible. Do not imply independent validation by reusing the same stimulation cohort. The authors' project page lists paper and code, but the inspected page did not expose a repository link or downloadable code; code-level comparison remains pending access to the paper's supplementary artifacts.

## Observability-aligned diffusion / null-space completion (arXiv:2610.27461)

The arXiv API record identifies the paper as “Observability-Aligned Diffusion and Null-Space Completion for EEG Source Localization” (v1, 20 October 2026). The arXiv HTML full-text currently displays a different title, “Observable and Null-Space Electrophysiological Source Imaging with Diffusion Priors,” for the same identifier and authors. This is a metadata/title inconsistency; this audit identifies the work by arXiv ID and version rather than treating the title mismatch as two papers.

The paper explicitly decomposes source activity into lead-field row and null components, refines the row component with singular-coordinate Posterior-DDIM, then adds ridge and temporal-network completions constrained to the null space. It states that the null completion leaves the row estimate and predicted EEG unchanged. The paper distinguishes prior-driven completion from measurement-supported information and acknowledges that the null component is not identifiable from EEG. The principal benchmark is simulated TVB activity; the recorded-data demonstrations are exploratory and use cross-modal or single-contact references, including one participant for its coreg-spikes evaluation.

**Overlap:** an explicit observability decomposition, null-space reasoning, and a warning that EEG-invisible source structure is prior-driven are already present in this close work. These cannot be framed as new contributions of Observable Geometry.

**Difference:** this work estimates a representative source waveform; Observable Geometry asks which competing source hypotheses are distinguishable under a specified operator and family. Again, this is a difference in question, not evidence of novelty. General finite-union testing and inverse-resolution methods remain close prior art, while no held-out measured-data result currently demonstrates that our family audit changes a decision beyond direct fitting or established methods.

## Updated claim boundary

The strongest defensible distinction is currently a **software/workflow distinction**: a reproducible, model-conditional report that exposes how a source-family choice changes the residual/compatibility conclusion, rather than silently returning one regularized source map. The present evidence supports describing this as a potential researcher-facing audit capability, not a validated decision aid. The existing method does not yet earn a novel-method claim because:

1. the `q*(tau)` sandwich is a basic implication of nested feasible sets;
2. full-mesh multi-patch certification and a useful computational advantage are unresolved;
3. direct constrained fitting presently gives the same decisions;
4. measured neural-source recovery and a protocol-locked, held-out researcher-decision benefit are not established; and
5. the closest 2026 work now directly occupies source-space observability decomposition and null-space completion.

Do not pivot to a learned reconstruction model merely to look more novel. A viable future distinction would have to show that a predeclared family-ambiguity report or certificate changes a concrete decision correctly on held-out measured data, at matched coverage/error, beyond direct fitting, GBF, CANDLE, relevant resolution/patch methods, and a fair set-valued or Gaussian testing baseline. If it does not, retain the reproducible software contribution and state that no novel method is supported.

## Primary sources inspected

- Suzuki, Wada & Sugiura, **CANDLE: Cortical Null-Space Decomposition for Noninvasive Brain Source Imaging**, arXiv:2610.07824v1: <https://arxiv.org/abs/2610.07824> and full text <https://arxiv.org/html/2610.07824v1>.
- Authors' CANDLE project page: <https://candle-esi.pages.dev/>.
- Wen, Yang & Liu, arXiv:2610.27461v1. API title: **Observability-Aligned Diffusion and Null-Space Completion for EEG Source Localization**; HTML title currently differs. Record: <https://arxiv.org/abs/2610.27461>, full text: <https://arxiv.org/html/2610.27461v1>.

This is a targeted close-prior-art screen, not an exhaustive systematic review. The conclusions above are based on the arXiv v1 texts and the CANDLE project page inspected on the date stated; later revisions or supplementary code may change implementation-level details.
