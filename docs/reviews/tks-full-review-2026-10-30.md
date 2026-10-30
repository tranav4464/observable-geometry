# Observable Geometry: full TKS build review

**Historical findings: all three were subsequently addressed in [the remediation re-review](tks-remediation-review-2026-10-30.md).**

Date: 30 October 2026. This was a same-host technical/product review with prior project involvement, not unaffiliated external review.

Reviewed repository: `23de77fb310c324a20377e8bcfeb4943f597b73f`. Accepted numerical software: `58570b8738080efd6c94b7e44eb5d89f83343be9`, version 0.1.3.dev0. Reviewed download: `Observable_Geometry_TKS_20261030.zip`, SHA-256 `e1868d9e21bd40c5a6dc266b518b7ea9e545545e705faa14a450a52c23be70b6`.

## Verdict

**The bounded local TKS software demonstration passes the checks performed. The distribution has three concrete follow-up issues and should not be described as flawless or fully self-contained.** No numerical blocker was found for the accepted model. B8 remains owner-accepted PASS under its documented amended criterion; this review does not upgrade that to external human validation.

## Findings, in priority order

### 1. P2: standalone run provenance does not identify the numerical implementation

Location: `src/observable_geometry/cli.py:189–194`.

`distinguish` records `implementation_sha256` for `cli.py`, while its numerical implementation is in `track_b/distinguishability.py`. A change to that module can leave the manifest's implementation hash unchanged. The run manifest also does not record the installed package version and numerical-library versions. Inputs and outputs remain hashed, but the run alone cannot identify all code that produced them.

The accepted build is covered by separate wheel/source/installed-module comparisons, so this does not invalidate its successful replay. It matters when a researcher uses the generic tool and shares only an output folder.

Recommended correction: record the numerical module hash, package version, Python/NumPy/SciPy versions, and preferably a package-file or distribution fingerprint. Check with a meaningful regression that changing the numerical module changes provenance. Such a code change needs a new candidate and numerical replay; do not silently replace the accepted wheel.

### 2. P2: the outer ZIP README contains broken links and source-checkout instructions

Locations: `README.md:19`, `README.md:27`, `README.md:103`; `scripts/build_tks_submission.py` copies the repository README unchanged.

The 174 packaged files all pass their hashes, and all six START_HERE navigation links resolve. However, the ZIP's README links to `index.html`, which the ZIP does not contain (it contains `START_HERE.html`), and to a root-level audit script that is only inside the nested source ZIP. It also links to a research report outside the package. The editable source-install instructions apply after extracting the source archive, not in the outer ZIP folder.

Recommended correction: generate a bundle-specific README pointing to START_HERE, package installation, and the source extraction step. Mark workspace-only research references explicitly or supply permitted linked documents. Run link checks on the actual ZIP, not only the workspace. This is a handoff defect, not corrupt software.

### 3. P2: the submission builder depends on an ignored local packet

Location: `scripts/build_tks_submission.py:10–11`.

The original builder hardcoded a private audit-packet path that is absent from a fresh public checkout. It also fixed one destination and refused to overwrite it. Refusing overwrites is appropriate, but there was no documented input/destination argument or artifact-acquisition step. Consequently another developer could not regenerate that submission ZIP merely by cloning the repository and running the script.

Recommended correction: accept explicit source-ZIP, wheel and output paths; verify the pinned hashes; document how to obtain the data-free artifacts or build the exact candidate. Distinguish rebuilding the handoff from reproducing the licensed model result. This issue does not stop installation of the supplied wheel.

## Newly executed verification

| Area | Result |
|---|---|
| Git state and remote | Clean before review; origin/main matches 23de77f |
| Download ZIP CRC | Passed |
| Packaged file hashes | All 174 passed |
| Installed package versus delivered wheel | All 18 Python modules identical |
| Delivered source tests | 209 passed, two expected skips, zero failures |
| Current gate-register tests | Seven passed |
| Live installed-wheel model demo | Completed successfully |
| Directed ranked CSV | All 40,980 rows byte-identical to the previous audited run |
| Score arrays and summary | All nine arrays and full JSON summary identical |
| New output hashes | Match the new run manifest |
| Runtime array-access log | Exactly four permitted model keys, all allowed |
| Committed audit evidence | Git blob bytes match the evidence manifest |
| Desktop presentation | Rendered and visually inspected at 1280px; clear layout |
| Narrow presentation | Rendered and visually inspected at 600px; readable wrapping |
| Front-page navigation | All six targets exist in the ZIP |

The tests and demo reused the isolated environment created during the preceding audit, rather than claiming another fresh install. Its delivered wheel bytes were checked again. Versions: Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1, MNE 1.13.2, pytest 9.2.0. The original fresh-install evidence remains separately available. A 420px headless screenshot was clipped by the rendering setup; a reliable phone-width interaction test was not established. The 600px check should not be represented as comprehensive mobile testing.

The archive skips are the local repository-evidence check and the local WSGZP geometry-status test. These are documented omissions, not hidden failed tests. The previously reported 211-test workspace pass was not represented as a newly rerun full workspace suite in this review.

## Scientific and mathematical review

The implemented metric is the absolute cosine between covariance-whitened forward columns, with magnitude normalization, minimum Euclidean source separation and stable tie ordering. The covariance support check, zero-pattern handling, nonfinite-input checks and scope labels are consistent with a nominal fixed-model diagnostic. Unit-SNR profiled residual is a geometric residual, not a calibrated probability. Candidate rankings do not establish actual source activity or neural source recovery.

The demonstration uses 236 modeled sensors and 8,196 candidate sources with covariance rank 235. Its 40,980 rows are directed top-five alternatives, not 40,980 independent experiments or unique unordered source pairs. Median best distant similarity is 0.915556984605132; about 6.04% are at least 0.95. No validated scientific decision threshold is attached to those values.

The current pitch and landing page acknowledge prior art and the separation between the GBF workflow and the pairwise diagnostic. They do not claim invention of cosine similarity. B4–B7 pivots and the amended B8 criterion are disclosed. That is appropriate for this TKS snapshot. These disclosures do not themselves establish that the tool improves a researcher's decision.

## Product usefulness and remaining boundaries

The build is usable by a researcher who already has compatible forward-model inputs. It returns inspectable alternatives and exportable evidence. The static presentation page is an introduction and a recorded-results view; it is not an interactive source-imaging interface. The live functionality is the CLI.

A reviewer without model inputs cannot reproduce the exact participant demo from the public ZIP alone. That limitation is disclosed and does not require releasing restricted data. The current packet can support a local presentation, a code review and data-free tests; complete outsider model reproduction still needs lawful inputs.

Future work remains: external human review, defensible measured-source validation, WSGZP registration checks, and a prospective decision comparison against direct leadfield correlation and established resolution diagnostics. A novel method, clinical value and journal suitability are not established. None of those claims should be added to improve the pitch.

## Scope of this review

I reviewed the active CLI, numerical diagnostic, test coverage, input/access contracts, delivered source and wheel, acceptance records, submission documents, Git evidence and presentation. I executed the shipped-source suite and an actual model-only run. I did not rerun every historical GBF/scientific experiment, independently re-establish MRI registration, run original recordings, test multiple operating systems, or exhaustively audit every experimental API. Tests establish observed behavior in these cases, not absence of every possible defect.

The source and released artifacts were not modified during this review. The three findings are recommendations, not claimed repairs.

## Evidence

Saved in `outputs/track_b/tks_final_review_20261030/`: `package_review.json`, `installed_wheel.json`, `tests.log`, `tests.xml`, `gate_validation.log`, `demo.log`, the fresh `demo/` output, `replay_and_provenance.json`, and rendered screenshots. The new ranked CSV hash is `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`.
