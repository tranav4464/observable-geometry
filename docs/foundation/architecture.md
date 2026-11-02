# Architecture

Observable Geometry is a Python package with three user-facing parts:

| Component | Location | Role |
|---|---|---|
| Source-pattern calculations | `src/observable_geometry/` | Validates model inputs, computes similarities and source-family summaries. |
| Command-line interface | `src/observable_geometry/cli.py` | Runs audits, checks metadata, prevents output overwrites, and writes results and provenance. |
| Local browser interface | `src/observable_geometry/web_app.py` | Runs or inspects the same diagnostic through a local web page. |

The package also contains the separately preserved GBFs implementation/reproduction work. The pairwise diagnostic does not call an inverse solver and does not estimate active sources.

## Input flow

A `distinguish` run reads a leadfield, covariance and source coordinates from a model-only NPZ bundle, plus metadata defining channel order, reference and model provenance. Arrays are checked before use. The covariance is factored on its supported subspace; pair scores are computed from the whitened, normalized leadfield columns. The run records input and output hashes, parameters, software identity and the NPZ keys accessed.

CPU float64 is used for the reference calculation. The tool writes ranked alternatives and summary outputs to a new run directory. It never overwrites a previous run.

## Boundaries

The calculation is conditional on the provided forward model, covariance, reference, orientation and source family. The public repository does not distribute licensed participant model inputs. It does not train a model, inspect EEG events, or establish physiological source recovery. See the [mathematical definition](mathematics.md) and [validation scope](validation.md).
