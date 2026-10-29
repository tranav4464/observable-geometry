# B8 working-tree model-only reproduction after atomic CLI change

**Date:** 29 October 2026\
**Status:** PASS for the listed software parity checks on the modified working tree; not a release or scientific-validation pass.

## Reproduction

The current CLI was run on the sealed Track A sub-01 forward-model bundle
using the existing model-only exporter. The exporter read only `leadfield`,
`noise_cov`, `source_coordinates`, and `vertex_ids`; its manifest states that
the recorded EEG `data` key was not accessed. The CLI's separate key-access
log records exactly `leadfield`, `noise_covariance`, `coordinates_m`, and
`source_ids`.

The fresh working-tree run reproduced the prior verified version 0.1.2
clean-wheel result exactly:

- Ranked-pair CSV: byte-identical, SHA-256
  `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`.
- All saved `scores.npz` arrays: exact, including IDs, indices, validity,
  norms, scores and residuals.
- Summary metrics: exact; 8,196 valid signatures, covariance rank 235,
  median best distant absolute cosine 0.915556984605132, and 6.04% of best
  distant similarities at or above 0.95.
- Current input and output hashes: match their run manifests.
- Reference chain: the prior output is linked to the recorded clean-install
  parity check, which reports PASS for the installed 0.1.2 wheel.

The machine-readable result is
[`reproduction_check.json`](../../outputs/track_b/20261029T_atomic_cli_real_model_reproduction/source_cli/reproduction_check.json).
Rerun with:

```powershell
python scripts/track_b/verify_b8_atomic_cli_reproduction.py
```

## Claim boundary

This verifies that the output-directory safety change preserved the previous
nominal diagnostic on one sealed participant-specific model. It does not
independently verify the scientific algorithm, validate endogenous neural
source recovery, establish decision utility or novelty, or demonstrate
population generalization. The rerun used model arrays only, not EEG samples.
The working-tree changes are uncommitted and have not been rebuilt as a new
clean-install wheel; this check does not close B8 or its outside-review gate.
