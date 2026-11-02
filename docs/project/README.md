# Observable Geometry

A local EEG source-pattern audit for researchers.

Observable Geometry ranks distant candidate sources whose predicted scalp patterns are similar under a declared forward model and noise covariance. It is designed to make model-conditioned ambiguity inspectable before interpreting a source estimate.

## Start here

- [Project overview](docs/project/project-overview.md)
- [Run a demo](docs/project/demo.md)
- [Open the local browser interface](docs/project/web-interface.md)
- [Read the method](docs/foundation/mathematics.md)
- [Review the validation scope](docs/foundation/validation.md)

## Claim boundary

The project is exploratory research software. Its similarity score is established mathematics. A model-predicted similarity is not a source-recovery probability or proof about activity in a measured EEG event. The current evidence does not establish endogenous neural-source recovery, improved researcher decisions, or generalization across participants. The public repository does not distribute licensed participant data.

The static demo below uses recorded software outputs or arithmetic examples; it does not analyze a visitor's EEG. Use the Python CLI or local browser interface with your own verified model inputs for an actual model audit.
