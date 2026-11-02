# Researcher handoff

Observable Geometry is a local software tool for checking similarity among EEG patterns predicted by a supplied forward model. It accepts a model-only leadfield and matching covariance, ranks distant source-pattern alternatives, and records the run inputs and outputs for inspection.

## To try it

1. Install the package and optional browser requirements as described in the [demo guide](demo.md).
2. Use the public arithmetic fixture to explore the interface, or prepare your own verified model-only bundle.
3. Run a diagnostic into a new output directory.
4. Inspect the ranked CSV, summary, score arrays, run manifest and key-access log.
5. Interpret every score as conditional on the supplied model, covariance, reference, orientation and source family.

The public example is not EEG. The licensed participant model used for the recorded project result is not distributed here; reproducing it requires lawful access to the matching model-only inputs.

## What the tool can support

It can help flag pairs of modeled sources that produce similar predicted scalp patterns, giving researchers a concrete alternative to inspect before making a spatially specific interpretation.

## What it cannot establish

It does not determine which source generated an observed EEG event, provide a calibrated probability, validate endogenous neural-source recovery, or show that a researcher makes a better decision. The cosine score is established mathematics, and the current project makes no novelty claim for it.

See [the project overview](project-overview.md), [results and limits](results-and-limits.md), and [the mathematical definition](../foundation/mathematics.md).
