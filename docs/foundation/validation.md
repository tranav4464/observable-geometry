# Validation scope

Observable Geometry has software checks for input contracts, numerical calculations, reproducible outputs and local interface behavior. The repository also preserves a model-only participant result and an independent numerical comparison. These checks establish software behavior and agreement under the declared inputs.

They do **not** establish that the diagnostic recovers endogenous neural sources from measured scalp EEG. The participant result is derived from a real participant-specific forward model, but the candidate fields are hypotheses evaluated by that model; they are not measurements of known, active cortical sources. Licensed participant inputs are not distributed in this repository.

The public arithmetic examples and small matrices in unit tests are software fixtures only. They are not physiological evidence. The current project has not demonstrated a researcher decision benefit over standard resolution measures, calibrated source-localization uncertainty, or generalization across participants. See [project results and limits](../project/results-and-limits.md).
