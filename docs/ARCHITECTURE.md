# Observable Geometry software architecture

**Current status:** B0–B3 pass at bounded scopes; B4–B7 are pivoted at their stated scopes; B8 is in progress. See `track_b/GATE_REGISTER.json` for the authoritative state.

## Active components

| Component | Path | Purpose |
|---|---|---|
| Nominal source-signature API | `src/observable_geometry/track_b/distinguishability.py` | Validate a leadfield/covariance/coordinate contract, compute whitened amplitude- and polarity-invariant pair similarities, and summarize their conditional interpretation. |
| Researcher CLI | `src/observable_geometry/cli.py` | Read allowlisted model arrays, enforce provenance metadata, refuse overwrites, and write ranked pairs, scores, summary, hashes, and access log. |
| Sealed-model reproduction command | `scripts/track_b/run_b3_distinguishability.py` | Verify the sealed Track A release, recompute the score in CPU float64, compare with the recorded reference, and write a versioned run. |
| Matched-output reproduction check | `scripts/track_b/verify_b4_matched_224_reproduction.py` | Compare saved derived outputs only; it does not open recordings. |
| Upstream GBFs implementation | `vendor/GBFs/` | Pinned upstream code and license, kept separate from project adaptations. |
| Track A foundation | `scripts/complete_track_a.py`, `outputs/tracka_release_20261022_v2/` | Sealed one-participant GBFs integration, parity evidence, nominal signatures, and MNE diagnostics. Do not modify the sealed release. |
| Historical prototype | `src/observable_geometry/core.py` | Earlier conditional linear-Gaussian computation; it is not the active GBFs diagnostic or an established BCI estimator. |

## Input contract

The active CLI accepts a NumPy NPZ model bundle containing:

- `leadfield`: sensors × sources, in the declared channel order.
- `noise_covariance`: sensors × sensors, in the same reference/order.
- `coordinates_m`: sources × 3, in metres and one declared coordinate frame.
- Optional `source_ids`: one integer/string identifier per source column.

The CLI rejects extra arrays before loading them; in particular, it does not accept an EEG `data` member. It also requires JSON metadata declaring dataset, participant, forward model, reference, coordinate frame, source orientation, covariance description, and unique sensor names. The software can validate shape and numerical properties but cannot verify the scientific truth of the supplied provenance text.

## Computation

The API eigendecomposes the symmetric noise covariance, retains its supported eigenspace using a fixed relative threshold, and rejects forward columns with material energy outside that support. It whitens the leadfield in that space, normalizes valid columns, excludes candidates closer than the declared Euclidean distance, and ranks absolute pairwise cosines with deterministic tie-breaking. A unit-whitened-SNR profiled residual is reported alongside the cosine.

This is a nominal geometry diagnostic under one forward model, covariance, reference, and source family. It is not a calibrated probability, unique inverse, empirical source-recovery score, or whole-brain reconstruction. Pairwise similarity is not automatically transitive and does not define ambiguity clusters.

## Output and reproducibility

Each CLI invocation writes to a new directory and records source/implementation identity, input hashes, output hashes, parameters, supplied provenance, and which NPZ members were read. CPU float64 is the reference implementation. The current sealed B3 example uses a fixed one-participant model; it is not portable without obtaining and preparing appropriate model inputs under the data license.

The package performs no model training. The active route does not create synthetic neural datasets or signals. Algebraic software fixtures verify invariants and interface behavior only. Track A and all earlier failed or mismatched outputs remain preserved.

## Known release limits

- This repository's source is licensed under BSD-3-Clause, as stated in `LICENSE`, `pyproject.toml`, and the wheel metadata. That license does not extend to the separately vendored GBFs checkout or to any dataset; follow each item's own license and data-use terms.
- Localize-MI data and derivatives are not bundled for redistribution.
- B4's artifact endpoint did not validate endogenous neural source identifiability; the prior 236/224-channel joined comparison is invalid.
- B7's paired model-only comparison found related but non-identical views from forward-signature similarity and MNE point-spread summaries; it did not test researcher decisions.
- No held-out multi-participant evaluation or researcher decision-value study is complete.
- Outside technical and clean-environment reproduction review remain outstanding.
