# Fresh user audit, 1 November 2026

## Scope and environment

I cloned the public repository into a new directory and installed the current `0.1.3.dev2` source with the `test`, `web`, `figures`, and `research-audit` extras in a new Python 3.12.14 environment. This checks the public install path. The local participant-model export used for the measured-anatomy demonstration was supplied separately and was not included in the clone. The web integrity correction described below was made after the initial clone and then tested in the main repository; the completed audit therefore combines a fresh public installation with targeted post-fix tests.

## Executed checks

| Check | Result |
|---|---|
| Fresh clone, editable install, and CLI launch | Passed |
| Fresh clone test suite | 214 passed, 2 expected skips (private workspace gate evidence and absent WSGZP dataset) |
| Main workspace after web integrity correction | 219 passed |
| `distinguish` on public four-source arithmetic example | 4 sources, covariance rank 3, 12 ranked rows; completed |
| `family-frontier` and `robust-audit` public examples | Both completed; their supplied numerical bounds were not independently authenticated by the commands |
| Streamlit AppTest: run public example | Completed, displayed 4 sources, 12 rows and median similarity 0.958 |
| Streamlit AppTest: inspect participant result | Completed, displayed 8,196 sources, 40,980 rows and median similarity 0.916 |
| Browser and CLI CSV parity for same public model | Byte-identical |
| Fresh clone with separately held Localize-MI-derived model-only inputs | 8,196 sources, 235 supported covariance directions, 40,980 ranked rows; CSV equal to the earlier verified notebook run |
| Output SHA-256 checks | All files named in the distinguish manifest matched their recorded hashes |
| No-overwrite control | Existing result directory rejected with exit code 2 |
| Forbidden `data` array | Rejected before a result directory was published, exit code 2 |
| Non-positive-semidefinite covariance | Rejected, no result directory published |
| Missing metadata | Rejected, no result directory published |
| Browser result-integrity correction | Three focused tests passed; a complete run is accepted, modified CSV and missing manifest are rejected |

The first row of the participant-model result is source ID 21 to candidate ID 9627 at 22.348103167 mm, absolute cosine 0.9022051367696975, and profiled unit-pattern residual 0.43130718888788705. The median best eligible cosine is 0.915556984605132. These are model-conditional quantities, not recorded event outcomes. The fresh-clone CSV matched the earlier 40,980-row result exactly.

## Fixes made in this audit

The browser previously accepted an existing directory containing only `summary.json` and `ranked_pairs.csv`. It now checks the complete `run_manifest.json` output-hash set before displaying the run. This detects a changed or incomplete local output, although a self-authored manifest is not independent authentication. The notebook README now explains how to register or select the kernel in a fresh environment.

## Remaining limits

The public clone cannot reproduce the participant run without separately obtaining the licensed Localize-MI-derived model inputs. The data-free public example checks the interface and arithmetic, not neuroscience. The participant run compares predicted sensor fields, not a measured neural source event. The browser displays the same nominal score as the CLI, with no calibrated threshold or proven decision benefit over standard resolution diagnostics. Physical channel/reference alignment and head-model accuracy must be checked from source provenance; the metadata strings and software dimension checks cannot establish them alone. The accepted B8 decision applies to the earlier `0.1.3.dev1` snapshot; the dev2 browser iteration and this correction have local automated and end-to-end checks but no separate external human acceptance.
