# TKS build remediation and re-review

30 October 2026. This was same-host maintenance verification, not unaffiliated human review.

**Result: PASS for all three scoped review findings.** Numerical software is version `0.1.3.dev1`, commit `3c99ca11bb71d35ca8f4c836a5c2b573fb7f36a3`. The previous accepted `58570b8` source and wheel remain historical artifacts. B8's owner-approved reproducibility scope is unchanged.

## Fixes and evidence

| Finding | Correction | Verification |
|---|---|---|
| Run provenance omitted numerical code | `distinguish` records all 18 package Python-file hashes, a canonical combined fingerprint, installed distribution version, Python, NumPy and SciPy versions | Regression changes the numerical module without changing CLI and confirms a changed fingerprint. Fresh installed-wheel output includes all expected fields; hashes and version independently checked |
| ZIP README links and commands mismatched layout | Builder writes a bundle-specific README, provides START_HERE and TKS_BUILD aliases, and explains wheel installation versus source extraction | All links in the entry page, README, submission overview, demo guide and handoff resolve in the generated ZIP |
| Packaging depended on ignored local packet | Builder takes explicit source, wheel, SHA-256, commit and output arguments, checks Git ZIP commit and exact source/wheel module agreement | Successfully built from the extracted Git source archive with no ignored research-output tree. Deliberately wrong hash rejected before output creation. Clean-checkout commands documented |

## Executed verification

- Full current workspace: **213 passed, zero skipped/failed**.
- Exact code source archive: **211 passed, two expected local-evidence skips, zero failed**.
- Fresh Python 3.12 virtual environment: installed the new wheel with NumPy 2.5.4 and SciPy 1.18.1. System site packages disabled; all 18 installed modules match the wheel.
- New installed CLI run: **40,980 directed ranked rows**, byte-identical CSV, all nine score arrays and full summary identical to the accepted earlier result.
- Input/output hashes and four-key model access log passed. No participant recording sample arrays accessed.
- New provenance fingerprint and each module hash match installed bytes. Run-manifest differences are intentional: stronger provenance, paths and timestamps. The numerical implementation is unchanged.
- Portable builder source/wheel agreement and artifact hashes passed. It rejects existing output destinations and bad hashes.

Wheel SHA-256: `783fd2dce9eb4f424afbe1dd279173f376baedb62a1ee2017a49576d2f323ff8`.
Source ZIP SHA-256: `ad5d1c5b0bc1891e18b505d6d9bc9d734531c4e61f5925e5ee359b8363d19069`.
Ranked CSV SHA-256: `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`.
Package-source fingerprint: `95cdd237926f647507bf13f0e72b07dcac37c94d90e679098a54462e2cb02230`.

Machine-readable evidence and test logs: [remediation evidence](../track_b/tks_remediation_20261030/MANIFEST.json). The code is pinned separately from subsequent documentation and packaging.

## Remaining limits

No unresolved defect from the three-item review remains in the tested scope. This is not proof of absence of every possible defect or a new external human review. The public package still intentionally excludes licensed model arrays. Reproducing the exact participant result requires lawful inputs; the local demo is available on this machine. Internet/package-cache access is needed to install dependencies unless users supply a wheelhouse. The builder checks supplied artifact identities and source/wheel consistency; it does not authenticate an untrusted user's choice of reference hashes.

The provenance enhancement applies to the reviewed `distinguish` workflow. The experimental `robust-audit` and `family-frontier` commands retain their separately documented evidence limits. No numerical algorithm or source-recovery claim was expanded.

Physiological source recovery, WSGZP registration, researcher decision advantage, novelty and independent human review remain future work. B8 PASS continues to mean the owner's accepted bounded software-reproducibility criterion.
