# Final editorial and scientific audit

**Scope:** the two TKS articles, the six-paper matrix, Learn overlap map, and their consistency with the accepted Observable Geometry software snapshot. This audit checks claims and presentation; it does not make the model-only result into physiological validation.

## Editorial review

| Check | Result |
|---|---|
| Distinct questions | Article 1 explains the Build's method and measured limits. Article 2 asks how a brain map can be validated across six original studies. The [overlap map](learn-build-overlap-map.md) marks Learn background kept brief. |
| Length | Article 1: **3,197 words**, Article 2: **2,932 words**, including citations. Both are approximately **12–13 minutes** at a technical-reading pace, though readers may pause longer over equations or linked figures. |
| Voice and structure | Both articles use a personal but precise voice, readable headings and short transitions. Article 1 has the research-report progression while retaining a reader-facing title; Article 2 is a comparative argument rather than a second Build report. |
| Language pass | Formulaic transitions and repeated stock phrases were replaced with direct descriptions of the work and the author's reasoning. The technical claims, figures, citations and limitations were retained. |
| Non-specialist check | Article 1 now explains the leadfield, covariance, whitening, polarity, cosine, residual and comparison metrics beside their equations. Article 2 introduces dipoles, IEDs, surgical resection, source maxima and the head-model shortcut where they first appear. |
| Visuals and captions | The articles link to source figures and the existing software evidence. No new figure is reproduced in either article, so there is no new caption, visual-permission or image-generation claim to audit. |
| Local links | `python scripts/verify_tks_writing.py` finds **zero broken local links** and enforces the article word ranges. External primary-source links and project links were checked against the cited source pages. |

## Scientific review

| Check | Result and boundary |
|---|---|
| Mathematical derivation | Article 1 derives covariance-supported whitening, normalized absolute cosine and profiled unit-pattern residual. The calculation is conditional on the fixed-orientation, single-column source family; gain is removed by normalization, and source polarity is free. The source/covariance channel-reference contract and eigenvalue support cutoff are stated. |
| Model example | Article 1 states one Localize-MI sub-01 model, 236 channels, 8,196 vertices, rank 235, 20 mm exclusion and five ordered alternatives. The 40,980 rows are directed exports, not independent neural observations. The [Article 1 claim audit](article-claim-audit.md) traces each result to code or saved evidence. |
| Reproducibility | The article separates arithmetic fixtures, frozen float32-to-CPU64 comparison, independent score replay and installed-wheel output replay. The lawful participant model arrays are not in the public bundle; a reader can run the public algebraic example and repeat the licensed-model result only with matching permitted inputs. |
| Comparators and novelty | GBF inverse reproduction, direct leadfield comparison and PSF/CTF resolution are not conflated. The 1993 angular-separability prior art is cited. Moderate one-model PSF correlations are presented as related outputs, with no claimed decision improvement or new method. |
| Failed routes | The stimulation-pulse artifact and WSGZP geometry limitations are included as unresolved validation routes. Neither is called endogenous source ground truth. |
| Six-paper evidence | The [research matrix](six-paper-research-matrix.md) records study population, independent reference, method, figure, result and limitation for each primary paper. The [Article 2 claim audit](article-2-claim-audit.md) traces all key numbers and the distinction between known injection sites, measured neural events, clinical outcomes, constructed patches and model uncertainty. |
| Cross-study inference | Article 2 does not rank methods by incomparable millimetre errors. Its final experiment is a proposed test requiring independent geometry checks and held-out participants, not a demonstrated result. |
| Software checks | The final workspace suite passed **216 tests** on Python 3.12.14. The source archive and wheel were hash-checked and their Python modules compared byte for byte by the submission builder. A new virtual environment installed the packaged wheel and ran the public `robust-audit` arithmetic example successfully. That example checks the public command path; it is not physiological validation. The prior [fresh public-clone check](../reviews/fresh-public-clone-check-2026-11-01.md) records a separate 214-pass/2-skip archive run and licensed participant-model replay. |

## Release boundary

These articles explain a **validated software build and model-conditional finding**. They do not assert a novel mathematical method, exact neural-source identification, measured endogenous-source recovery, clinical readiness, or population-level generalization. The accepted numerical snapshot is commit `3c99ca1`; the submission source archive is commit `bc448c3`, whose diagnostic implementation is unchanged. The bundle README and manifest identify the packaged source, while the B8 record identifies the accepted snapshot. The portable bundle excludes licensed participant model inputs, so a public reader cannot repeat the participant replay from the bundle alone.
