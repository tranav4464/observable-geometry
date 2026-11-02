# Results and limits

The participant-model example used Localize-MI sub-01. Its prepared forward model contains 236 accepted EEG channels and 8,196 fixed-orientation cortical candidate sources, with covariance rank 235. The diagnostic compared modeled leadfield columns; it did not read EEG event samples.

| Reported result | Meaning |
|---|---|
| **40,980 ranked rows** | Five directed, eligible alternatives were saved for each of 8,196 query sources under a 20 mm minimum-distance setting. This is not the number of all possible unordered source pairs. |
| **0.91556 median best-match score** | The median across query sources of the best distant noise-whitened absolute cosine in this one model. |
| **6.04% at or above 0.95** | Fraction of query sources whose best eligible score reached this descriptive threshold. The threshold is not calibrated and is not a probability cutoff. |
| **Independent numerical agreement** | The recorded replay and separate calculation agreed to numerical precision for the declared inputs. This supports arithmetic reproducibility, not biological accuracy. |

## Evidence boundary

This is one participant-specific forward model. The candidate sources are modeled hypotheses, not known endogenous neural events. The same score may change with the head model, covariance, sensor reference, orientation, source family and distance threshold. The project has not shown that a high score predicts an actual localization error, improves a research decision, or generalizes to other participants.

The public repository excludes the licensed participant model inputs and recorded data. Readers can run the data-free arithmetic example; reproducing the participant-specific numbers requires lawful access to the matching model-only inputs and the exact run configuration.
