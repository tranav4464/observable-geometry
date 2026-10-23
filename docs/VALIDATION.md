# Recorded-data protocol and verification

## Data roles

Localize-MI is the primary physical benchmark. Its metadata describe 7 participants, 61 sessions, 256 scalp electrodes, stimulation contact coordinates, surfaces and prepared forward models. Confirm exact usable counts after ingestion; metadata counts are not completed analyses. Its license in the cloned dataset is CC-BY-NC-SA 4.0.

The dataset metadata checkout contains annex pointers, not necessarily recordings. The fetch script retrieves explicitly selected payloads to a separate directory, checks expected byte count and MD5 from the annex key, and writes a manifest. A Git clone alone must never be reported as successful physiological-data loading.

First onboarding case is sub-01/run-01, selected before any new performance outcomes. Its event metadata describe K13-14 stimulation at 1 mA. This convenience case is for format and numerical integration checks, not unbiased scientific performance estimation. It remains a development case in later evaluation.

## Ingestion requirements

Verify the epoch time axis from metadata/source acquisition files rather than copying hard-coded sampling rate and tmin from an old notebook. Check whether baseline correction has already been applied. Match forward channels by name, exclude marked bad channels consistently, apply identical reference operators, and record all coordinate transforms and units.

For the pulse-artifact localization task, identify the stimulation waveform window without optimizing over the known source location. For physiological responses after stimulation, use a separate analysis and interpretation because propagated activity need not originate only at the contact. Define the physical target of bipolar stimulation (midpoint, endpoints or a bipolar forward model) before scoring. Do not silently equate a nearest cortical vertex with the actual physical source.

## Development and test split

Participants are the outer grouping unit. Keep repeated stimulation sites and currents together where necessary to prevent near-duplicate leakage. With only 7 participants, grouped nested evaluation has wide uncertainty and needs transparent individual results. Freeze preprocessing, prior/model parameters, location-set construction and sensor-selection objective using training/development information. Record a dated protocol before examining held-out outcomes.

Never use a held-out source coordinate to choose its ideal sensors. A target region can be supplied as prior experimental knowledge only if that information would actually be available to a future user. Candidate sensors must exist among measured electrodes for retrospective validation, and noise statistics must be estimated without access to held-out target outcomes.

## Primary RSG validation task

The first claim is predictive: source-condition pairs assigned greater recoverability should be more distinguishable in held-out recorded scalp data. Define the observation window, feature/preprocessing path, nuisance handling and empirical classifier or decision statistic entirely on development participants. The classifier is an evaluation instrument, not automatically the scientific contribution.

Because the same stimulation artifact may dominate both model predictions and recorded discrimination, report results separately for artifact and post-stimulus physiological windows. Success on artifact data demonstrates a physical localization/discrimination capability, not recovery of ongoing neural computation.

## Comparisons

Baseline A: pinned upstream GBFs with documented data adaptation.
Baseline B: conventional MNE/eLORETA source estimate with equally careful tuning.
Baseline C: nominal lead-field/topographic separation.
Baseline D: resolution-matrix/adaptive-parcellation analysis under a matched inverse method.
Baseline E: robust/Bayesian model-error comparator if compatible with the frozen source family.
Proposed: calibrated forward-family RSG followed by recoverability-limited spatial reporting.

Ablations remove model uncertainty, calibration and nuisance profiling separately; vary reference consistently; and compare nominal versus robust separation. Sensor-layout ablations are deferred.

## Metrics and uncertainty

Report participant-level calibration of predicted distinguishability, empirical confusion ranking and uncertainty. Also report localization error with coordinate convention and spatial extent for the secondary reconstruction task. For any calibrated ambiguity set, report both empirical coverage and size. Conditional amplitude variance is not an empirical location confidence or recoverability score.

If sensor selection is later authorized, evaluate it by adding an already-recorded sensor, refitting consistently and comparing empirical confusion/error changes with equal-budget alternatives. Predicted improvement is not evidence of true benefit.

Hardware perturbations and conductivity changes are sensitivity models, not newly measured data. Matrix fixtures are mathematical tests only. No synthetic neural recording is used as a substitute for this study's real-data evidence.

## Stop and repair conditions

- Missing coordinate transformations, wrong units, unexplained channel ordering or unclear reference: stop the scientific run and repair the adapter.
- Negative prior precision from a transformation: investigate units/domain; do not silently clip values in upstream parity mode.
- Inability to reproduce upstream behavior on identical inputs: diagnose before claiming an extension beats it.
- No performance benefit: report it, revise the hypothesis using development data, and reserve fresh test data for new claims.
- Uncertainty method produces narrow but poorly covered sets: do not call them reliable.

## Completion evidence

Code correctness needs mathematical invariants; scientific usefulness needs real-data comparisons; reproducibility needs manifests and a clean-run check. Passing one category does not establish the others.
