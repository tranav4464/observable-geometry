# Automation and verification scripts

The scripts at this directory's top level reproduce and verify the sealed Track A foundation. They remain together because they share `tracka_paths.py` and the geometry-cache utilities.

- `bootstrap_foundation.ps1` creates the pinned Track A environment.
- `run_foundation.ps1` runs the complete foundation workflow.
- `verify_foundation.py` validates and optionally seals a Track A run.
- `render_review.py` writes a run-local `foundation_review.html` beside the Track A outputs. It never overwrites the curated project review.
- `build_tks_submission.py` creates the portable TKS handoff bundle.

[`track_b/`](track_b/) contains the later model audits, registered recomputations, gate checks, dataset inspections, and independent verifiers. Many filenames in that directory are evidence identifiers cited by the gate register, so they are intentionally retained.

Run commands from the repository root unless a script explicitly states otherwise. Never overwrite the sealed Track A outputs.
