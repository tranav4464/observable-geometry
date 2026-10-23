# Synthetic feasibility harness

> **Archived historical artifact.** The active Track B objective now excludes synthetic datasets and simulated performance. This harness, its tests, and its outputs are retained as project history only; do not run it for current evidence or cite its results as support for the real-data build.

## Purpose

This is the first executable data-path check for Track B. It verifies that the project can represent a directed regional network with known truth, produce simultaneous abstract scalp and sparse intracranial observations, enforce stable dynamics, and set each modality to a named finite-sample signal-to-noise ratio. It is development feasibility evidence only. It is not an estimator benchmark, a reproduction of the paper's exact generator, or evidence about real brains.

## Explicit generator

For `N` regions, the simulator selects `A` active regions, then assigns exactly `d` incoming directed edges to each active target from the other active regions. Inactive regions have no incoming or outgoing edges and receive no process innovations. Nonzero weights are standard normal draws. The coefficient matrix is rescaled to the configured spectral radius `r`, with `0 < r < 1`. Latent states follow

`x[t] = A x[t-1] + epsilon[t]`,

where the innovation components for active regions are independent standard normal draws. The convention is `A[target, source]`, matching matrix multiplication `A @ x[t-1]`.

The scalp operator is a deterministic, seeded dense random matrix with entries distributed as `N(0, 1/N)`. It is an abstract linear mixing operator, not a head-model lead field. The iEEG operator selects `m` distinct regional states from all `N` regions, independently of whether a selected region is active. Each observation channel receives independent Gaussian noise; for each modality, the noise is scaled to the requested finite-sample RMS SNR. This exact finite-sample scaling makes the configured ratio auditable but slightly conditions the random noise realization on the generated signal.

## Feasibility run

Command:

```powershell
.venv\Scripts\python.exe scripts\track_b\run_synthetic_feasibility.py --out-dir outputs\track_b\synthetic_feasibility_20261022_v3 --seed 20261022
```

The saved report records configuration, dimensions, active regions, graph edge count, transition spectral radius, realized SNRs, participant-data status, and the compressed array hash. The default fixture has 69 modeled regions, 10 active regions, 2 incoming edges per active target, 128 scalp channels, 21 selected iEEG regions (30.4% coverage), 512 samples, scalp SNR `-5 dB`, and iEEG SNR `30 dB`. These settings echo several paper-described values, but the random lead field and simplified generator mean this is still not a physical WBEN reproduction.

## Interpretation and current boundary

This run verifies dimensions, deterministic generation, known graph support, stable latent dynamics, and SNR bookkeeping. It does not test source inference, edge-recovery accuracy, or a contribution. Because the lead field is abstract, it does not reproduce WBEN's realistic BEM-based scalp observation. The paper's Appendix A.3 says its simulated experiment uses `K=1`; higher-order VAR remains an optional generalization, not a requirement for matching that experiment. If a defensible physical lead field cannot be built from available project resources, the final software must label the simulator as abstract and limit its conclusions accordingly.

Tests: `tests/test_track_b_synthetic.py` checks deterministic output, dimensions and selection semantics, graph activity/in-degree, zero-edge behavior, transition stability, exact SNR accounting, and invalid-configuration failures.
