# Research article claim audit

**Article:** `research-article-draft.md`  
**Audit date:** 1 November 2026  
**Status:** Main model-output numbers freshly replayed from an installed public-clone package using lawful local model-only inputs. The local editorial and link review is complete; independent reader feedback remains a future publication check.

| Article claim | Current supporting evidence | Scope and caveat |
|---|---|---|
| One participant, 236 channels, 8,196 fixed cortical vertices, covariance rank 235 | `docs/track_b/B2_GBF_SPEC.md`; `docs/track_b/B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md` | The raw Localize-MI forward file is free orientation. The audited leadfield is converted to fixed surface orientation after channel selection. |
| Minimum separation 20 mm, top five, 40,980 directed rows | `docs/track_b/B2_GBF_SPEC.md`; `docs/track_b/B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md`; `docs/reviews/tks-remediation-review-2026-10-30.md` | Five rows for each of 8,196 vertices. Directed rows must not be called unique unordered pairs. |
| Median best distant absolute cosine 0.91556; 6.04% at or above 0.95 | `docs/track_b/B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md` reports 0.915556984605132 and the fraction; the generated summary is a model-only artifact | Descriptive one-model distribution. The 0.95 cutoff is not a calibrated reporting or clinical threshold. |
| Installed package reproduced 40,980 rows and score arrays | `docs/reviews/tks-remediation-review-2026-10-30.md`; new public-clone replay in `docs/reviews/fresh-public-clone-check-2026-11-01.md` | The fresh CSV, scores NPZ and summary JSON match the prior run byte for byte. Same-host software parity on licensed model-only inputs; public source users do not receive those inputs. |
| Separate calculation differed by about 2.1 × 10⁻¹⁵ at most | `docs/track_b/B8_PASS_20261030.md` reports 2.11e-15; `docs/track_b/B2_GATE_CLOSEOUT_20261024.md` contains the independent CPU64 verification history | Numerical agreement for the declared model and score. No physiological validation follows. |
| B7 correlations 0.480 and 0.434 | `docs/track_b/B7_DECISION_VALUE_AUDIT_20261024.md`, generated paired report and independent statistical check described there | Spatially dependent vertices from one model; no p-values, population inference or demonstrated decision benefit. |
| B4 stimulation route did not validate neural-source recovery; earlier channel join invalid | `docs/track_b/B4_DEVELOPMENT_AUDIT_20261024.md`; `docs/track_b/B4_CHANNEL_MATCH_RECONCILIATION_20261024.md` | The stimulation pulse is an electrical artifact endpoint, not a known endogenous neural event. |
| WSGZP participant registration remains unverified | `README.md` WSGZP geometry status and linked coordinate/provenance audits | Metadata plausibility does not prove electrode-to-MRI registration. Do not imply the dataset itself is unusable for all purposes. |
| Angle-based source separability predates this build | Pascual-Marqui and Biscay-Lirio (1993), DOI 10.3109/00207459308994264, cited as source [1] in the article | Similarity of concepts, not an assertion that every implementation detail is identical. |
| GBFs constrain inversion with individual cortical geometry | Wang et al. (2026), *Nature Biomedical Engineering*, DOI 10.1038/s41551-026-01664-0, source [2] | The article distinguishes the GBF inverse estimator from this package's direct leadfield-column comparison. |
| PSF/CTF are inverse-resolution diagnostics | Official MNE-Python documentation, source [3] | Depends on the chosen inverse operator, whereas this direct column comparison does not choose one. |

## Editorial check

The article was read against the README, submission and demo. Its claims distinguish the model-only `distinguish` result from the unsuccessful measured stimulation-pulse validation route, and it does not present the 0.95 score as a probability or decision threshold. Local Markdown links were checked for existence on 1 November 2026. The external reference destinations and the final publishing format should be checked again at posting time. Independent scientific and non-specialist reader feedback would strengthen a later revision; none is represented as completed here.
