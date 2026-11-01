# Article 2: claim-to-source audit

**Article:** `article-2-source-validation.md`

**Question:** What evidence distinguishes an identified neural source from a plausible brain map?
**Checked:** 1 November 2026 against the full primary texts and their figure and table captions. This is a source audit, not an independent replication of any of the six experiments.

| Article claim | Primary evidence | Interpretation boundary |
|---|---|---|
| Localize-MI had seven participants and 61 stimulation sessions; best-configuration mean minimum distance 5.39 mm | [Mikulan et al. 2020](https://www.nature.com/articles/s41597-020-0467-x.pdf), dataset description and Fig. 3 | The reference is the known injected-current contact. Best-per-session tuning is optimistic; the pulse artifact is not an endogenous neural event. |
| Unnwongse enrolled 11, analyzed nine, recorded 37 scalp channels, and obtained 3,619 accepted fits from 341 contact-pair averages under 11 skull conductivities | [Unnwongse et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9942548/), Methods, Results, Figs. 1, 3–4 | Repeated model fits are not independent people or stimulation sites. Reported 10.3–26 mm mean errors vary with depth and conductivity. |
| Zauli studied eight participants, four hippocampal and four cortical-dysplasia cases, using simultaneous scalp EEG and SEEG; 82.5 IEDs per person on average and 9.4% scalp detectability | [Zauli et al. 2024](https://air.unimi.it/retrieve/e5cb014e-6527-4977-8590-6d80f9f288e3/1-s2.0-S0165027024001389-main.pdf), Results and Fig. 2 | The 19.20 mm best-per-participant and 35.56 mm across-settings distances refer to SEEG-timed averages, not unaided single-trial recovery. Implanted contacts sample only some sites. |
| In the surgical study, 45 patients had 257-channel recordings; the default 204-channel analysis gave 67% within 10 mm and 83% sublobar concordance among 30 favourable outcomes | [Vorderwülbecke et al. 2020](https://cibm.ch/wp-content/uploads/1-s2.0-S1388245720304934-main.pdf), abstract, Table 1 and Figs. 1–4 | The endpoint is concordance with resection and postoperative outcome. The paper explicitly says poor outcome does not reliably prove incorrect source estimation. It is not exact neural-source ground truth. |
| Hauk used five participants' anatomy and measured resting activity, but injected 500 constructed patches per hemisphere to evaluate inverse resolution | [Hauk et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC7793168/), Methods and Figs. 1–7 | The true patch is known because it was constructed; this does not validate recovery of an unknown endogenous source. |
| Vorwerk varied tissue conductivities while fitting a measured somatosensory response; skin/skull changes had strong location and depth effects | [Vorwerk et al. 2019](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00531/full), Table 1 and Figs. 1, 4, 7–10 | This is one case and a specified conductivity range. It shows model sensitivity, not the location of a verified true generator. |

## Synthesis checks

- The article does not compare error numbers across studies as though they shared an endpoint or independent unit of analysis.
- Its proposed held-out experiment is explicitly a proposal, not a result achieved by Observable Geometry or any one cited paper.
- It distinguishes imposed stimulation, endogenous IEDs, clinical outcome, constructed source injection and forward-model uncertainty throughout.
- All six cited works are original studies or original data-and-analysis reports. The 2020 Vorderwülbecke experimental paper is used rather than the later 2025 dataset description that reuses part of its result.
