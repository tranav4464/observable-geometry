# Track B research operating system

This is the required workflow for every Track B research session. It exists to prevent unverified assumptions, wasted compute, test leakage, and claims that exceed evidence. The master scientific design is `MASTER_RESEARCH_PLAN.md`; the machine gate state is `GATE_REGISTER.json`; the claim state is `EVIDENCE_LEDGER.md`.

Before substantive work, copy `RESEARCH_SESSION_TEMPLATE.md` into the unique run directory and fill the decision question, smallest decisive check, stop condition, input role, and falsification condition. If the work cannot change a decision or create a reusable validation artifact, do not start it.

## Start of a work session

1. Read the current gate register, the relevant plan stage, and the latest decision-log row. Confirm the current dataset/code commit and check for new user instructions.
2. Choose the earliest unresolved gate on the critical path. Do not work around a failed prerequisite by moving to a later stage.
3. Write a one-line session question: **What decision will this work change?** Record expected evidence and the smallest decisive check.
4. Identify whether any input contains held-out outcome values. If yes, confirm B5 lock and the approved access log before opening them.
5. Check whether an equivalent artifact already exists; extend it only with a new run ID and explicit reason. Do not repeat searches or tests whose authoritative outputs already exist without new evidence.
6. Run only the smallest check that could change the decision. Expand to a full sweep only after the check passes and record why the sweep is now necessary.

## Research-source protocol

For each literature claim, record the primary source, publication/version date, exact equation or experimental task, cohort, metrics, split unit, code/data availability, limitations, and the exact Track B implication. Use primary papers, official proceedings, official repositories, dataset records, and original supplementary methods before reviews or secondary summaries. A search result is a lead, not evidence. Search for errata, later versions, and post-publication code. Keep unresolved interpretations visible in the method matrix.

For each dataset claim, identify its pinned commit/version and license. Separate repository metadata from actual signals, images, derived outputs, and author preprocessing code. Hash fetched files, log allowlists, and state exactly what bytes were inspected. Never infer source truth from a filename, channel label, coordinate value, or paired event count alone.

## Gate-specific work rule

Before coding, write the equation, input/output shapes, units, assumptions, and one hand-computable case. Implement the CPU reference before acceleration. Compare against an independent solution. Add a negative control before any performance claim. Use tests that detect a realistic scientific error: sign mistakes, rank deficiency, coordinate mismatch, leakage, time-grid drift, overfit threshold, wrong metric, or unsupported inference.

Before signal processing, freeze event semantics, sampling, filter/reference, anti-alias/resampling, epoch/time-zero definition, channel order, missing-channel handling, artifact policy, and data split. Keep all sessions, trials, sites, and pairs from one participant in the same outer split for population-level claims. Contact-held-out checks are allowed only for the prediction endpoint they actually test.

Before a GPU run, retain a CPU result on the same inputs, record the full environment, warm up, synchronize CUDA around timing, include transfer cost, report peak memory, and compare numerical error. CUDA availability, utilization, or lower runtime on a toy matrix is not a scientific result.

## Run and evidence discipline

- Each run gets a unique UTC-stamped ID and a new output directory. Never overwrite a manifest or silently replace a failed run.
- Inputs, code revision/hash, parameters, data split, random seeds, environment lock, GPU/CPU, logs, warnings, exclusions and outputs belong in that run folder.
- Preserve failed runs and negative outcomes. A rerun after a code/config change is a new run with a new ID.
- Recompute primary metrics from saved raw predictions using an independent function/script. Generated tables/figures must be traceable to the same participant-level rows.
- Update `DECISION_LOG.md` when a choice changes; update `EVIDENCE_LEDGER.md` when a claim's status changes; update `METHOD_MATRIX.md` when prior art changes; update `PROTOCOL_LOCK.md` before confirmatory work.
- A test participant's outcomes may never be used to choose a model, threshold, time window, exclusion, hyperparameter, or wording. If they are inspected, demote that participant to development and find new independent confirmation.
- At session end, mark the result pass/fail/inconclusive/exploratory; record the exact artifact and next earliest gate. Do not quietly leave a failed or incomplete run as if it passed.

## End of a work session

Record (a) the question answered; (b) evidence artifact and verification command; (c) what is established, assumed, and unresolved; (d) the decision changed or why it did not change; (e) the next smallest decisive action; and (f) whether data were accessed. If no evidence or decision changed, do not report the session as scientific progress. Run the gate validator after gate/evidence edits and the relevant tests after code edits.

## Required commands

From the repository root in PowerShell:

```powershell
.venv_tracka_clean\Scripts\python.exe scripts\track_b\validate_gate_register.py
$env:PYTHONPATH = 'src'
.venv\Scripts\python.exe -m pytest -q
.venv_trackb_gpu\Scripts\python.exe scripts\track_b\check_gpu_runtime.py
```

The first command checks dependency ordering and existence of registered evidence; it does not verify scientific truth. The test suite verifies software properties represented by its tests; it does not validate the source model. The CUDA smoke check verifies device access and one linear-algebra parity fixture; it does not establish speedup or a scientific result.

## Wasted-work filter

Do not proceed with a task that has no plausible result-to-decision map. Before spending compute or reading held-out signals, answer:

1. What uncertainty or claim does this resolve?
2. What exact result would make us stop, pivot, or continue?
3. Is there a cheaper metadata, equation, or toy-fixture test that could answer it first?
4. Could the work contaminate an independent test set?
5. What reusable evidence artifact will remain even if the result is null?

If the answers are missing, write the missing prerequisite into the gate register and do not start the expensive work.
