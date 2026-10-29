# Novelty target selection: fixed-area follow-up prioritization

**Decision status:** selected falsifiable evaluation question; scoring rule remains a candidate\
**Protocol status:** design specified; numeric protocol lock pending readiness gates\
**Signal-analysis status:** NOT AUTHORIZED; geometry, preprocessing and protocol gates remain open\
**Scope:** the existing Observable Geometry source-family analysis; preserve prior releases and evidence

## Selected claim to test

> For a held-out participant, does a source-family-aware scalp-EEG report identify a fixed-area cortical region that contains a larger fraction of the participant's sampled SEEG-responsive contacts than matched-area single-map and patch/resolution baselines?

This is a researcher decision: **where to spend a limited follow-up sampling budget**. It is not a claim that the selected region is the complete generator, that unresponsive or unimplanted cortex is inactive, or that a source family is the biological truth.

## Proposed estimand and scoring rule

For each eligible held-out participant-condition, construct the declared compatibility set

```text
K(y) = union over frozen source families and admitted forward scenarios
       of all sources whose whitened residual against measured scalp field y
       is within the training-only tolerance.
```

For parcel `j`, define source mass using the frozen cortical vertex-area weights
`a_v` and a source field `x_v` expressed in current-density units (or a
documented equivalent integrated-current parameterization). Compute the
**guaranteed parcel-mass fraction**

```text
g_j(y) = inf { sum(v in j) a_v |x_v| / sum(v in cortex) a_v |x_v| : x is in K(y) }.
```

This is a conservative lower envelope, not a probability. Select the cortical area budget `B` by maximizing total `g_j` subject to a fixed parcel-area budget. If the source parameterization cannot be converted consistently to a surface-integrated quantity, all parcel scores are zero, or the optimization cannot certify the selection, the method abstains; it must not substitute optimizer hit counts or an assumed probability map. The exact numeric `B`, parcelization, conversion from model coefficients to cortical current density, fit tolerance, source-family constraints, forward-uncertainty set, and abstention rule still require pre-outcome freeze after the geometry and preprocessing contracts are resolved. Therefore this document is **not** represented as a locked analysis protocol.

For participant `i`, score `c_i = responsive contacts inside selected area / all eligible sampled responsive contacts`. The primary estimate is the participant-macro mean paired difference in `c_i` versus the strongest matched baseline selected using training participants only; report a participant-clustered confidence interval and each comparator separately. The held-out participant is the independent unit, not the contact or event. Include abstentions in the denominator as zero captured contacts and report their rate separately. This is positive-contact capture only. Do not call it source sensitivity, specificity, complete coverage, or true-source accuracy.

## Required matched comparisons

At the identical participant, condition, area budget, channel/reference/preprocessing contract and held-out split, compare against:

1. GBF's single-map priority region.
2. Direct constrained fitting of the same source families and uncertainty set (the answer-equivalence and implementation oracle).
3. MNE, dSPM, eLORETA and LCMV where the same forward model supports a fair implementation.
4. Matched patch/extent and PSF/CTF or spatial-fidelity baselines.
5. XDL-ESI or a documented reason an equivalent comparison cannot be reproduced.

Use participant-level outer splits; tune all tolerances and choices inside training participants. Test whether any gain survives controls for implant density, shaft, region, contact depth and stimulation distance, and whether it survives source-family and forward-uncertainty ablations. Independently replay the selected-region scores and contact-count endpoint from frozen artifacts.

## Novelty pass/fail rule

The proposed analysis earns a **measured decision-utility finding** only if the preregistered held-out positive-contact-capture endpoint improves over the training-selected strongest matched baseline by a predeclared practically meaningful margin, with participant-level uncertainty excluding no gain, and the effect survives the listed sampling and modeling controls. A different map, residual, or score is insufficient. The margin and fixed area budget must be selected and justified before outcome access; they are not set in this design note.

This would not by itself establish a **novel algorithm**. Method novelty additionally requires a distinct mathematical guarantee or independently replayed certified cost/tightness advantage over direct constrained fitting of the identical object. If direct fitting yields the same answer at comparable cost, report no new method. If baselines yield equivalent decisions, classify the result as a software contribution or pivot.

## Prior-art threat and rationale

The WSGZP cohort has already been used for GBF stimulation-site localization and by XDL-ESI for CCEP source extent. PSF/CTF and spatial-fidelity methods already evaluate localization and extent, and set-membership/robust inverse methods cover much of the proposed compatibility mathematics. Therefore, applying these tools to WSGZP or reporting SEEG contact overlap alone is not novel. The narrow candidate delta is the **held-out, fixed-area follow-up decision** under a conservative cross-family lower envelope, if it adds measurable value beyond those baselines. That delta remains unproven and may be rejected by the test.

## Mathematical stress check before protocol lock

The lower-envelope score has a strict degeneracy condition: if even one admissible
`x ∈ K(y)` has zero source mass in parcel `j`, then `g_j(y)=0`. If a compatible
alternative can avoid every parcel, the entire guaranteed-mass map is zero and
the policy must abstain. This may be exactly what a conservative ambiguity
report should say, but it would make the proposed follow-up ranking unusable.
Whether this occurs is unknown because no eligible WSGZP source-family fit has
been run. Before freezing this as the primary algorithm, demonstrate that the
score is nondegenerate on an already permitted measured case, or reject this
ranking rule. Do not relax the infimum or introduce family weights after seeing
the held-out SEEG labels.

There is a relevant existing measured-data control: the Localize-MI
family-validation run compared point, equal-weight local patches, signed local
patches and global ridge on one participant's stimulation-pulse artifact, with
a held-current check. Flexible fits had smaller residuals; this is not a neural
source endpoint, a participant-held-out result, or evidence that a fixed-area
source-family report improves a researcher decision. Preserve it as a
controlled artifact diagnostic only. See
`research/gbf_omitted_activity_20261024/LOCALIZE_FAMILY_VALIDATION_20261028.md`.

## Preconditions before any measured-signal analysis

This document selects the evaluation question, but does **not** yet freeze the scoring rule or unlock signal access. Before fitting or scoring, close and record:

- participant-specific scalp-to-MRI coordinates, registration QC and valid forward models;
- released preprocessing, channel order, reference, filtering, artifact and response-window semantics;
- dataset license/reuse conditions and exact included participant/run-condition table;
- frozen source families, continuous uncertainty set, whitening/covariance, training-only tolerance, parcel grid and area budget;
- eligible SEEG-response definition, participant-grouped splits, controls, comparator versions, stopping rule and independent reviewer approval.

If these cannot be established, stop before signal fitting and report the target as untested. Do not generate synthetic neural observations or use model-generated fields as physiological evidence.

## Current conclusion

The selected target is a **falsifiable empirical decision-value test**, not established novelty. Existing evidence supports neither a novel-method claim nor a measured source-recovery claim. The current project status remains **PROMISING BUT UNVERIFIED** until a valid measured-data comparison is completed; if the gates cannot be cleared, submit the bounded GBF/source-family software contribution with that limitation explicit.
