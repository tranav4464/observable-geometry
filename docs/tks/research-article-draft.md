# When Two Brain Locations Look Alike to EEG

*What building Observable Geometry taught me about the limits of a convincing brain map*

Imagine two lights behind a frosted window. From outside, you can see a glow, but a bright light farther away and a dimmer light nearby might leave almost the same pattern on the glass. Adding more detail to your drawing of the glow does not tell you which light was on.

EEG source imaging faces a related problem. Electrodes record voltage differences at the scalp. Researchers then use a head model to estimate which brain locations might have generated those measurements. The resulting maps can be detailed enough to show a small region lighting up. But how distinctly did that region appear to the electrodes in the first place? Could a distant region have produced nearly the same predicted scalp pattern?

That question led me to build **Observable Geometry**, a software tool that audits a declared EEG forward model before interpreting a source map. Given a leadfield, candidate coordinates, a matching noise covariance and model metadata, it lists distant candidates whose predicted scalp signals are most alike. Electrode geometry and the sensor reference enter through the supplied forward model and covariance; the command does not reconstruct them from raw electrode files. The tool gives a researcher specific alternatives to inspect. Its answer belongs to the supplied model; it does not identify the sources that were active in a person's brain.

## The trip from brain to scalp, and the trip back

A forward model starts with a proposed neural source and predicts the voltages it would create at the electrodes. It accounts for the geometry and electrical properties assigned to the head and for the electrode positions. If we place one candidate source at each of thousands of cortical locations, the model gives each candidate a column of predicted sensor values. Together these columns form a *leadfield*.

The inverse problem runs in the other direction. We start with scalp measurements and try to estimate their sources. This is difficult because there are many more possible source configurations than independent sensor measurements. Different combinations can produce similar observations. An inverse method therefore needs assumptions about which solutions are preferable. Those assumptions can be sensible and scientifically useful, but the selected map does not by itself show that every plausible alternative has been ruled out. The non-uniqueness of EEG and MEG source inference has long been recognized in the source-imaging literature [1].

One striking recent example is the **geometric-informed basis functions** (GBFs) framework. It represents source activity using modes derived from an individual's cortical geometry and then estimates their contributions to EEG or MEG measurements. This anatomical structure is a way to constrain the inverse problem, and the published framework evaluates reconstruction across several kinds of data [2]. I reproduced a bounded implementation path using fewer modes than the published benchmark and studied how its inverse uses the forward model. That raised a different question for me: before choosing an inverse solution, can I show where the forward model itself predicts lookalike source patterns?

The `distinguish` command in Observable Geometry answers that narrower question. It does not implement GBF source reconstruction or claim that its rankings improve on GBF estimates. It compares columns of a supplied forward model directly. The verified participant example uses fixed-orientation cortical vertices. Another source family could be supplied, but its construction and assumptions would need to be declared.

## What does “looks alike” mean?

Suppose two candidate locations produce sensor patterns with different overall strength but almost the same shape. If source amplitude is unknown, the shape similarity is relevant: one source might imitate the other by changing its amplitude. Polarity can also be reversed under the comparison's declared convention. Observable Geometry therefore compares the absolute cosine between normalized patterns.

Before comparing them, the tool *whitens* the patterns using the supplied noise covariance. In plain language, it gives less weight to combinations of electrodes that are noisier under that covariance and more weight to combinations measured more reliably. This is why the covariance, channel order and reference must match the forward model. Mixing them would make a precise-looking score describe the wrong measurement system.

The resulting score runs from zero to one. A value near one means the two modeled patterns have nearly the same shape after whitening and allowance for polarity. It does **not** mean there is a 95% chance of localization error when the score is 0.95. That probability would require additional assumptions about source amplitudes, noise, competing sources and an actual inference procedure, followed by empirical calibration. Similar angle-based source-separability ideas appeared in the literature decades ago [1]. The mathematical score is established work; my contribution lies in making a bounded comparison inspectable and reproducible.

The tool excludes candidates within a chosen spatial distance, then ranks the remaining alternatives for each location. That distance is a question the researcher sets, not a universal resolution limit. A source can have a nearby lookalike because neighboring cortical locations are similar; the more surprising case is a high-scoring alternative far away. The CSV preserves the source and candidate indices, their distance and score. A manifest records the model and code hashes, and an access log records which arrays the command opened.

## What happened on a real participant model

I tested the diagnostic on a verified Localize-MI forward model for one participant. This model had **236 scalp channels**, **8,196 fixed-orientation candidate cortical vertices** and a noise covariance with supported rank **235**. With a minimum separation of **20 mm** and the five highest-ranked alternatives requested for each vertex, the command wrote **40,980 directed rows**. These are five rows per source, not 40,980 distinct unordered pairs.

The median best distant similarity was **0.91556**. About **6.04%** of vertices had a best distant similarity of at least **0.95** [4]. The 0.95 cutoff describes the distribution; it has not been validated as a rule for accepting or rejecting a source claim. These numbers describe this model, reference, covariance, source family and distance choice. They are not an estimate of how often EEG localization fails in people.

The engineering checks matter because a source ranking is only useful if it can be traced back to the right inputs. A clean installation reproduced the participant model's **40,980 ranked rows** and score arrays exactly [4]. A separate calculation reproduced every ranking, with a maximum cosine difference of about **2.1 × 10⁻¹⁵** [4]. The CLI rejects undeclared arrays in its model bundle, including a recorded EEG `data` array, before opening them. These checks support numerical reproducibility and the stated access boundary; they do not validate the anatomy of a recovered neural source.

## The comparison that changed how I describe the tool

Existing source-imaging software can examine resolution through an inverse operator. A *point-spread function* asks where the chosen inverse method would place activity from one proposed point source; a *cross-talk function* asks which true sources could contribute to one estimated location. These are established ways to inspect leakage and localization behavior [3]. My diagnostic is calculated before choosing an inverse operator, so it asks a related but different question about the predicted sensor patterns themselves.

I paired the best distant similarity for all **8,196** vertices with minimum-norm point-spread summaries on the same participant model. The Spearman rank correlation was **0.480** with peak-location error and **0.434** with point-spread weighted distance [4]. These moderate associations show that the summaries are related and not identical on this model. They do not show that my output makes a researcher choose correctly more often. The vertices are spatially dependent, and the analysis had no independently verified neural-source endpoint, so I did not turn those correlations into population claims or p-values.

This distinction affected the final build. It would have been easy to show a list of pairs with scores around 0.95 and call them “unresolvable.” But the score alone does not set a clinically or scientifically calibrated decision threshold. A researcher could use the list to inspect a planned comparison between two regions and ask for sensitivity checks. I have not yet demonstrated that this changes a reporting decision beyond a direct leadfield-correlation map or a standard resolution report. That is an important next experiment, not a result to assume.

## Why I stopped some tempting experiments

The Localize-MI data also include electrical stimulation pulses. Those pulses have a known contact, which initially looked attractive as a location reference. But the scalp response to a stimulation artifact is not the same thing as an endogenous neural source event. A channel mismatch in an earlier route also made one comparison invalid. I kept the failure and the corrected rerun in the project record rather than using the pulse result to claim neural-source recovery.

I examined other measured-data routes too. For a rigorous source validation, I would need compatible scalp recordings, reliable participant-specific electrode-to-MRI geometry and an independently defensible endpoint. The WSGZP data offer promising simultaneous scalp and intracranial measurements, but the exact registration provenance and quality checks required for participant-specific source analysis remain unresolved in the material available to this build. Sparse intracranial contacts also sample only part of the brain; they cannot silently become a complete ground-truth source map.

The result is a narrower but clearer software release. It can audit the *model's* predicted ambiguity. It has not shown recovery of endogenous brain activity, population generalization, or an advantage in researcher decisions. That boundary is part of the result: the enticing data routes taught me which measurements would actually test the claim and which would merely make it look tested.

## What a researcher can do with it

Consider a study that plans to compare estimated activity in two distant cortical regions. The researcher can supply the same head model, reference, channel set and noise covariance intended for the inverse analysis. Observable Geometry then reports whether those regions contain candidate patterns that appear similar at the sensors. If they do, the report gives concrete pairs and model provenance to inspect while deciding how specific the anatomical interpretation should be.

The researcher still needs the inverse method's resolution analysis, sensitivity checks and empirical evidence appropriate to the claim. My report offers a direct view of the model before those choices. Its usefulness beyond existing diagnostics remains to be tested with a prespecified decision and matched baselines.

The next version should ask whether the ranking survives justified changes in covariance, montage and source orientation, and whether a region-level report helps someone make a better decision than direct leadfield similarity or point-spread analysis alone. An eligible measured-data study would then test whether that decision tracks independently verified neural events. A larger model or a fancier score would not replace those tests.

## What I learned from the build

I started with a broad ambition: find out how much of the brain we can reconstruct from outside the head. Working through GBFs, forward models, inverse resolution and difficult validation datasets made the useful question more precise. A beautiful source map can be computationally valid while the sensors still permit a distant alternative under the chosen model. The first useful step is to make that alternative visible and traceable.

Observable Geometry does that for a declared model. Its strongest result is a reproducible audit of **what the model predicts the electrodes can distinguish**, paired with explicit limits on what the audit can establish about real neural activity. Whether it improves a research decision is still open. That is the next question I want the software, and the evidence, to answer.

## Sources and project evidence

1. Pascual-Marqui, R. D., and Biscay-Lirio, R. (1993). “[Spatial resolution of neuronal generators based on EEG and MEG measurements](https://pubmed.ncbi.nlm.nih.gov/8063519/).” *International Journal of Neuroscience* 68:93–105.
2. Wang, S., et al. (2026). “[A geometry aware framework enhances noninvasive mapping of whole human brain dynamics](https://www.nature.com/articles/s41551-026-01664-0).” *Nature Biomedical Engineering*.
3. MNE-Python contributors. “[Plot point-spread functions (PSFs) and cross-talk functions (CTFs)](https://mne.tools/stable/auto_examples/inverse/psf_ctf_vertices.html).”
4. Observable Geometry: [TKS build submission](https://github.com/tranav4464/observable-geometry/blob/main/docs/tks/submission.md), [B3 results](https://github.com/tranav4464/observable-geometry/blob/main/docs/track_b/B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md), [B4 audit](https://github.com/tranav4464/observable-geometry/blob/main/docs/track_b/B4_DEVELOPMENT_AUDIT_20261024.md), [B7 comparison](https://github.com/tranav4464/observable-geometry/blob/main/docs/track_b/B7_DECISION_VALUE_AUDIT_20261024.md), [B8 acceptance record](https://github.com/tranav4464/observable-geometry/blob/main/docs/track_b/B8_PASS_20261030.md), and the [new public-clone replay](https://github.com/tranav4464/observable-geometry/blob/main/docs/reviews/fresh-public-clone-check-2026-11-01.md). [Code and evidence](https://github.com/tranav4464/observable-geometry).

