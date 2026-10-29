# Observable Geometry B8: revised candidate reviewer packet

**Exact candidate commit:** `58570b8738080efd6c94b7e44eb5d89f83343be9`  
**Package:** `observable-geometry 0.1.3.dev0`  
**B8:** IN_PROGRESS, awaiting outside clean reproduction.

## What changed after the prior 8a19221 packet

The WSGZP coordinate-audit utility and its test now import `mne.transforms` functions explicitly. This resolves an import-order failure observed with MNE 1.11.0. The active `distinguish` numerical code is unchanged. The prior candidate and AI review remain historical; evaluate this exact source commit.

## Owner-executed evidence in this packet

- Exact-commit workspace: 211 passed, no skips or failures.
- Extracted source archive: 209 passed, two documented skips, no failures.
- MNE 1.11.0 no-preimport workspace regression: 211 passed.
- Rebuilt wheel: all 18 packaged modules match committed source; version and license checks pass.
- Fresh Python 3.12 installation: installed modules match the wheel. The installed CLI reproduced all 40,980 model-only ranked pairs, score arrays and summary metrics exactly against the prior clean-wheel reference. Logs declare only the four approved model-array keys.

All listed evidence is **owner-executed**, not an independent outside reproduction. `EVIDENCE_MANIFEST.json` contains hashes for every packed item. The model-only bundle is deliberately excluded under the dataset terms.

## Outside reviewer procedure

1. Check packet CRC and manifest SHA-256 hashes. Inspect the source archive and wheel. The exact source commit is at https://github.com/tranav4464/observable-geometry/tree/58570b8738080efd6c94b7e44eb5d89f83343be9.
2. Use a clean Python 3.12 or newer environment. Install the included wheel, `pytest>=8`, `h5py>=3.10`, `mne>=1.7`, and `nibabel>=5.2`. Extract the source archive, set `PYTHONPATH` to its `src` directory, and run `python -m pytest -q -ra`. Record versions, commands, results and any differences. The two documented skips concern local gate evidence and unavailable WSGZP data. A standalone pure-Python `nibabel` wheel is included for offline collection, but is **not** a complete dependency wheelhouse. Borrowed dependencies do not count as an isolated install.
3. **Required for B8:** lawfully obtain the exact Localize-MI-derived model-only bundle/metadata from the owner or directly witness a clean run on the owner's machine. Verify the input hashes in `evidence/model_only_parity.json`; run `observable-geometry distinguish --bundle <bundle> --metadata <metadata> --output <new-dir> --minimum-distance-mm 20 --top-k 5`; compare the CSV, score arrays, summary, input/output hashes and NPZ access log with the supplied parity report. Do not inspect or redistribute participant recording samples. If this cannot be done, leave B8 open.
4. Return a dated, attributable record: name, affiliation, expertise, conflicts/prior involvement; checks personally performed or witnessed versus supplied evidence; differences; recommendation `PASS`, `HOLD FOR CHANGES`, or `FAIL/PIVOT`.

This software check does not establish endogenous source recovery, clinical validity, generalization, decision benefit, or methodological novelty. A stable release version is deferred until the B8 outside check and any remediation are complete.
