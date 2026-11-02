# Observable Geometry: project overview

Observable Geometry is a Python research-software project for inspecting how similar two candidate sources look to EEG under a specified forward model.

A researcher supplies a leadfield, a noise covariance built for the same sensor set and reference, source coordinates, and metadata describing the model. The software whitens and normalizes the leadfield patterns, ranks distant pairs by absolute cosine similarity, and records the inputs, outputs and accessed archive keys for each run.

## Intended use

Use the output as a **pre-interpretation model audit**. If two distant candidate sources produce similar modeled sensor patterns, that is a reason to be cautious about a spatially specific interpretation under those assumptions. The diagnostic does not say which source generated a real recording.

## Relationship to GBFs

The repository preserves a GBFs implementation/reproduction workflow. The pairwise diagnostic is separate: it compares supplied sensor-by-source patterns directly and does not run an inverse estimator or identify active sources.

## Evidence and limitations

The current software has reproducibility and regression checks, including a recorded participant-model calculation. Licensed participant inputs are excluded from this public repository. The public arithmetic example is only a software demonstration. Endogenous neural-source recovery, decision benefit over standard resolution measures and population generalization have not been established. The underlying similarity is established mathematics, so no novelty claim is made for that score.

See the [mathematical definition](../foundation/mathematics.md), [validation scope](../foundation/validation.md), and [user guide](demo.md).
