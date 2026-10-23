# Track B confirmatory protocol lock

**Status: UNLOCKED.** This is a template, not a preregistration or permission to inspect reserved outcomes. Track B active experiments use real recordings only; do not generate or score synthetic datasets or signal fixtures. Do not inspect confirmatory participant outcomes until B0–B4 pass, the route and real-data endpoint are approved, every applicable field is complete, and the B5 preflight passes. If no valid real-data endpoint survives, document that limit and narrow the software claim rather than substituting a synthetic study.

| Required field | Frozen value |
|---|---|
| Selected route and version | Pending B0 decision |
| Primary scientific question and estimand | Pending B2 |
| Target entity and observation type | Pending B1/B2 |
| Dataset, license, version/commit and signal hashes | Pending B1 |
| Eligible participant IDs and exclusion rules | Pending B1 |
| Development / confirmation split unit and IDs | Pending B1; all linked sessions/trials for one participant stay in one outer split |
| Event semantics, time window and epoch definition | Pending B1 |
| Sampling, anti-aliasing, resampling and time-grid policy | Pending B1 |
| Filter, reference, channel order, units and missing-channel policy | Pending B1 |
| Artifact handling and preprocessing provenance | Pending B1 |
| Model equations, dimensions, assumptions and identifiability limits | Pending B2 |
| Forward/observation-model family and parameter provenance | Pending B3 |
| Primary real-data endpoint and target semantics | Pending B2/B4; do not call prediction a ground-truth connectome |
| Baselines, matched tuning budget and implementation provenance | Pending B0/B4 |
| Primary metric, independent unit and uncertainty method | Pending B2/B4 |
| Minimum sample and meaningful effect / decision threshold | Pending B1/B4 |
| Negative controls, stress tests and sensitivity analyses | Pending B4 |
| Missing-data, exclusions, stopping and deviation rules | Pending B4 |
| Code commit, configuration hash, environment and run ID | Pending B5 |
| Test-outcome access audit and lock timestamp (UTC) | Pending B5 |
| Independent reviewer and sign-off | Pending B5 |

Any test-informed change to the model, threshold, time window, exclusions, or wording demotes the exposed test data to development. A new confirmation then requires an untouched independent sample. If a field cannot be specified before outcomes are opened, report the work as exploratory or pivot the study. All scientific evaluations use eligible real recordings; software checks may use algebraic identities, code invariants, independent implementations, and real-data pipeline checks, but no fabricated neural signals.
