# Controlled-stimulation source-family validation

## Scope

This is the project's first direct source-family comparison on measured scalp
data. It uses Localize-MI participant `sub-01`, the supplied participant-
specific forward model, and the known intracranial stimulation contact pairs.
The measured endpoint is the short electrical stimulation pulse artifact. It is
not an endogenous neural event and must not be described as spontaneous neural
source recovery.

## Locked computation

`scripts/track_b/run_localize_family_validation.py` uses the common good EEG
channels across all 11 runs, the supplied fixed-orientation forward model, an
average-reference projection and a pooled pre-pulse covariance estimated only
from the five 1 mA runs. The artifact topography is the evoked sample with the
largest global field power in the predeclared -2 to +2 ms window.

The compared families are:

* a fixed-orientation point field at the cortical vertex nearest the contact
  midpoint;
* an equal-weight 10 mm and 20 mm local patch with one profiled scalar;
* signed local-patch ridge fits at the same radii;
* a global ridge bank as a flexible reference.

The five sites with both 1 mA and 5 mA runs provide a held-current check. The
family direction is fitted on one current and scored on the other, with a
profiled scalar amplitude. This is a small within-participant stress test, not
a population estimate.

## Observed result

The result is saved in:

* `outputs/track_b/localize_family_validation/result.json`
* `outputs/track_b/localize_family_validation/family_rows.csv`
* `outputs/track_b/localize_family_validation/held_current_rows.csv`

The deterministic `result.json` SHA-256 after an independent second replay is
`B19F896546154514E622F3D1286362E9571733BDE2CB3FF4ABC8AB047F26151B`.

For the ten held-current directions (five sites in both directions), median
relative whitened residuals were:

| Family | Median held-current residual |
|---|---:|
| Point | 0.9530 |
| Uniform 10 mm patch | 0.8902 |
| Uniform 20 mm patch | 0.7828 |
| Signed 10 mm patch | 0.3287 |
| Signed 20 mm patch | 0.2485 |
| Global ridge | 0.0878 |

The flexible families fit the measured pulse artifact better than the point or
equal-weight patch families. That result is a **family-sensitivity and
endpoint-diagnostic finding**, not evidence that a distributed cortical source
generated the artifact. A pulse artifact can have a current path and orientation
that are not represented by the fixed cortical-normal neural forward model.

## Interpretation and claim boundary

This run satisfies a bounded controlled-stimulation validation requirement:
measured scalp data, an individual forward model and a spatially identified
intracranial stimulation reference were processed under a fixed protocol. It
does not establish that GBF scores recover endogenous neural sources. It also
does not support a novel-method or GBF-superiority claim: the flexible direct
fit gives lower held-current residuals, and no decision advantage over direct
constrained fitting has been demonstrated.

The correct current classification is **validated software contribution with a
real controlled-stimulation diagnostic; novel source-localization method not
supported**. A stronger physiological claim requires an endpoint whose
generator is neural rather than the stimulation pulse, or a laboratory dataset
with validated source ground truth and the same participant-specific geometry.

## Reproduction

From `observable_geometry`:

```powershell
& '.venv/Scripts/python.exe' 'scripts/track_b/run_localize_family_validation.py'
```

The script records the forward-model, transform and epoch hashes in the JSON
result. The full package suite remains independently tested (`130 passed`).
