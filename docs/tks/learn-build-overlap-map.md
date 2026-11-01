# Learn article overlap map for the two new articles

Source reviewed: Tranav Tyagi, *Can We Reconstruct Everything the Brain Is Doing Without Going Inside?*, published Learn article (32-page Medium PDF; working transcription at `Neurotech/Learn/Article Project/Working Files/MEDIUM_READY_ARTICLE_FROM_PDF.md`). The PDF is image-only; the working transcription was used to inspect its full section structure and text.

| Already covered in Learn | Build research article | Six-paper validation article |
|---|---|---|
| EEG, MEG, fMRI and fNIRS basics | One-sentence reminder of scalp EEG measurement | Refer to Learn; focus on what could validate an inferred source |
| Neurons, synapses, aligned currents, cancellation and the EEG reference | State only assumptions needed for the leadfield/reference contract | Discuss a measurement mechanism only when a selected paper's validation depends on it |
| Filtering, trial averaging, spatial filtering and CSP | Do not repeat | Do not repeat |
| Forward/inverse problem and regularisation as general concepts | Define the specific forward matrix, covariance, admissible source family and score, then derive the computation | Compare how six studies test or fail to test inverse claims |
| GBFs and anatomy-guided reconstruction | Report the exact bounded reproduction, deviations from the published setup and its separation from `distinguish` | Mention only if relevant to a validation design; avoid another GBF tutorial |
| AI speech/language decoding and SSVEP | Exclude | Exclude unless a primary paper makes a necessary validation analogy |
| Earlier Learn experiments: task prediction and scalp-to-iEEG prediction | Distinguish these from the current model-only Build; do not recast them as Build validation | Do not retell their methods or results |
| Broad answer to whether we can reconstruct everything | Answer the narrower question of what one declared EEG model can distinguish and what the software verified | Ask what independent evidence would justify a source attribution |

## Distinct thesis for each new article

**Build research article:** A reproducible pre-interpretation audit can expose distant source signatures that a declared EEG model predicts are similar. Its scientific value and empirical source validity remain open. The article should teach the derivation and exact implementation, not rebuild the Learn article's introduction.

**Six-paper synthesis:** The six selected primary studies test distinct parts of a validation chain: known or independently supported events, sensor-to-anatomy geometry, forward uncertainty, a matched comparator, and an endpoint that tests the anatomical claim actually made. The [research matrix](six-paper-research-matrix.md) records the methods, figures, results and limitations behind this synthesis.

## Editorial rule

When a paragraph in either new article only explains a term already taught in Learn, compress it to the minimum needed for the new argument and link the Learn article. Give the saved space to derivation, study design, evidence, competing explanations, and limits.
