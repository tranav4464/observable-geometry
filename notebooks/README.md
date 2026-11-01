# Reproduce the Build article figures

Open `model_audit_figures.ipynb` from the repository root using Python 3.12+. Install the optional figure dependencies with `python -m pip install -e ".[figures]"`. Run all cells in order.

The notebook reruns the package's `distinguish` diagnostic. If the local, hash-verified Localize-MI sub-01 model-only export is present, it produces the participant-model figures. A public clone falls back to the four-source arithmetic fixture in `examples/`; those demo figures are **not neuroscience evidence**. The notebook never reads recorded EEG waveform arrays.

Outputs are written to a new, timestamped, ignored `outputs/notebook_figures_*` directory. The notebook saves 300 dpi PNG and vector SVG files plus `figure_manifest.json` with input and output hashes and suggested captions. The third figure pairs the new run with the independently audited B7 MNE point-spread table; it is omitted from the public arithmetic demo.

The participant-model inputs and derived figures are not committed to GitHub. Check the Localize-MI dataset terms before redistributing any participant-derived figure. None of these plots establishes physiological source recovery, population generalization or an improved researcher decision.

## Placement in the Build article

Use the participant-model figures only after confirming that their publication is permitted by the dataset terms. The final local submission folder contains the executed notebook, PNG/SVG exports, and the hash manifest.

1. **Figure 1**, after the paragraph reporting the median best similarity and 495 vertices above 0.95. Caption: *Best eligible predicted scalp-pattern similarity for each of 8,196 modeled vertices. Alternatives within 20 mm were excluded. The 0.95 line is a descriptive marker, not a validated decision threshold.*
2. **Figure 2**, after the sentence reporting 42.67 mm as the maximum exported top-five distance. Caption: *Distance versus similarity for the 40,980 exported ranked alternatives. These are directed model comparisons from one participant; pairs outside the top five are not plotted.*
3. **Figure 3**, after the paragraph comparing the diagnostic with minimum-norm point-spread summaries. Caption: *Best eligible forward-pattern similarity versus minimum-norm point-spread peak-location error across 8,196 spatially dependent modeled vertices. Spearman rho = 0.480 is descriptive; it does not demonstrate improved source localization.*

The SVG files are best for layout and the 300 dpi PNG files are useful where SVG is unsupported. Do not describe any of these as measured neural-source recovery or as separate participant experiments.
