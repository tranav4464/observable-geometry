# Observable Geometry: TKS build submission

**Creator:** Tranav Tyagi  
**Field:** computational neuroscience / EEG source imaging  
**Accepted software:** 0.1.3.dev0, commit `58570b8738080efd6c94b7e44eb5d89f83343be9`  
**Status:** ready for TKS submission as a bounded research-software build. B8 passed under owner-accepted AI reproducibility; human external review is deferred.

## What I built

I built a tool for inspecting ambiguity in EEG source models. Given a forward model, noise covariance, source coordinates and provenance, it finds distant candidate brain locations whose predicted scalp patterns look similar. A researcher can inspect those alternatives before treating an estimated location as spatially specific.

The project started with a GBFs reproduction and reverse-engineering workflow. The delivered pairwise diagnostic is separate from that inverse estimator: it compares forward-model columns directly. My contribution is the implementation, strict input contracts, ranked alternatives, traceable outputs and reproducible checks. The similarity formula itself is established mathematics.

## Input, processing and output

- Input: a sensor-by-source leadfield, matching covariance, coordinates in metres, optional source IDs, and metadata describing reference and model provenance. Recorded EEG samples are not required by the diagnostic.
- Processing: whiten the predicted patterns using the supported covariance subspace, normalize their magnitudes, compare absolute cosine similarity, exclude source pairs closer than the chosen distance, and rank remaining alternatives.
- Output: `ranked_pairs.csv`, `scores.npz`, `summary.json`, `run_manifest.json` and `npz_key_access.jsonl`. A high score means similar predicted sensor patterns under this model. It is not a localization probability.

## What was demonstrated

The sealed sub-01 model has 236 sensors and 8,196 candidate sources, with covariance rank 235. At 20 mm minimum separation and five alternatives per source, the CLI produces 40,980 directed ranked rows. These are five alternatives per source, not 40,980 unique unordered pairs. Median best distant similarity is 0.91556. About 6.04% of sources have a best distant similarity of at least 0.95. That threshold is descriptive, not a validated cutoff for making a clinical or anatomical decision.

A fresh installed wheel reproduced all ranked rows, nine score arrays and the summary exactly. The full archive suite passed 209 tests with two documented local-evidence skips; those two tests passed separately in the workspace. A separate calculation reproduced every ranking with maximum cosine difference approximately 2.1e-15. [Audit and acceptance](track_b/B8_PASS_20261030.md).

## Why someone might use it

A researcher studying two regions can inspect whether the declared model gives them similar scalp signatures, examine the specific distant alternatives, and export an audit trail. The result can prompt closer inspection of spatial claims. Improved research decisions compared with existing leadfield correlation and resolution reports have not yet been demonstrated.

## Run or review

Use the [demo guide](TKS_DEMO.md). The submission ZIP contains the tested wheel, exact source archive, current submission documentation, resolved audit environment and data-free audit records. The licensed model inputs are excluded. On this project's local machine the verified inputs are available for a live demo; another user needs lawful matching inputs or their own verified forward model.

## Honest completion boundary

The TKS software snapshot is complete within its declared scope. B4–B7 remain recorded pivots, not completed scientific validations. This build does not establish neural-source recovery, a novel mathematical method, clinical utility or population generalization. WSGZP registration and measured-source validation are future extensions. No stable PyPI release or journal acceptance is implied. The [next-build review plan](NEXT_BUILD_REVIEW_ACTIONS.md) preserves the outreach feedback.
