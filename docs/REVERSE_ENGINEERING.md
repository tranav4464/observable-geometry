# Reverse-engineering record

GBFs checkout: `99fc7c6e8afbd2e3e68a700c5f1fa1483b90f49e`.
Localize-MI analysis checkout: `1bfed2384b523c8ffcc98b09faad3e94b3e0b138`.
Localize-MI metadata checkout: `d7a123d3067213281f106b343c71f28c30e4dd60`.

## Paper-to-code path

`demo_iES.py` loads epochs, builds/loads a forward solution, averages and references EEG, estimates noise covariance, builds a whitener, obtains cortical modes and calls `utils/seeg_with_eeg.py::process_evoked`. That routine builds a mode-space gain matrix and solves a penalized inverse system. `demo_simulation.py` calls the separate `utils/simulation.py::process_evoked_sim` path. The aggregate `main.py` invokes several datasets and should not be the first execution target.

## Findings to reproduce and clarify

1. **Different normalizations:** the recorded-data `process_evoked` normalizes each whitened lead-field row; `process_evoked_sim` does not. Both normalize whitened observed data by a global standard deviation. These are different transformations. Record exact behavior in parity mode; do not silently standardize one and call it the original method. Whether the difference is intended or consequential requires matched-input evaluation.
2. **Penalty sign and scale:** the routine uses `-1/log(eigenvalue)` and replaces each hemisphere's first eigenvalue with its second. This expression is positive for eigenvalues in (0,1), negative above 1 and singular at 1. Audit actual mesh units and eigenvalue range before interpreting it as a positive prior precision. Do not assume a paper-level Bayesian interpretation without checking the numerical domain.
3. **Direct inverse:** the mode solve explicitly forms a matrix inverse. A solve or factorization can improve numerical practice, but must be validated against unchanged upstream behavior and labeled an implementation change.
4. **External inputs:** simulation preparation loads `/data/benchmark/noise/cov-cov.fif`; the demo expects FreeSurfer anatomy and benchmark maps. A plain clone is not a ready-to-run benchmark.
5. **Path and execution assumptions:** `main.py` sets an empty path prefix and comments on a NeuroVault connection issue. Each demo needs its own verified paths and inputs.
6. **Basis restriction:** cortical eigenmodes are computed from a surface and may be restricted to a decimated source space. Preserve vertex IDs, hemisphere order and the induced metric; do not treat a restricted basis as automatically Euclidean-orthonormal.
7. **Epoch averaging:** recorded-data routines multiply whitened evoked data by sqrt(nave). Track covariance convention and output scaling when comparing amplitudes.

These are code observations, not claims of author error or invalid scientific results.

## REA work package

REA is optional for a concrete opaque component: a packaged source-imaging program, native solver extension, model artifact or executable whose behavior affects reproducibility. No such indispensable target has yet been identified in GBFs. Open Python paths are better inspected directly.

If a target is identified: pin its version and hash; write a specific question; inspect metadata/static code with REA; trace evidence to the observed transformation; independently verify it with input/output probes; record REA version, commands, output and interpretation limits. Do not infer biological meaning from binary structure. A software trace does not establish what a learned representation encodes.

REA installation is not yet performed. We will not configure a global MCP server or acquire a decompiler solely to create the appearance of reverse engineering. The source audit above already supplies a legitimate reverse-engineering deliverable.

## Parity plan

First evaluate upstream numerical routines on small, explicitly labeled algebraic fixtures. Then compare unchanged upstream and adapted routines on the same recorded data and geometry. Preserve original output normalization alongside any physically consistent alternative. Pin tolerated numerical differences, record the reason for any patch, and never substitute modified results into a reproduction table without a separate label.
