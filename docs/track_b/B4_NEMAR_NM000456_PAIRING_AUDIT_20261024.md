# B4 NEMAR nm000456 modality-pairing audit

**Audit date:** 24 October 2026  
**Purpose:** Resolve whether the 13-participant NEMAR `nm000456` release contains same-participant scalp EEG and SEEG recordings that could support a paired scalp-to-intracranial evaluation.  
**Data boundary:** Versioned directory listings and published metadata only. No EEG/SEEG samples, outcomes, or derived signal arrays were opened.

## Result

The release does **not** contain paired scalp EEG and SEEG participants. The NEMAR v1.0.2 top-level listing contains 13 participant directories. Reading each participant's directory listing shows 11 participants with an `eeg/` directory only and two with an `ieeg/` directory only. No participant directory contains both modalities.

| Released modality folder | Participants |
|---|---|
| EEG only (11) | `sub-PennEPI00037`, `sub-PennEPI01899`, `sub-PennEPI02012`, `sub-PennEPI02014`, `sub-PennEPI02032`, `sub-PennEPI02152`, `sub-PennEPI02194`, `sub-PennEPI02195`, `sub-PennEPI02197`, `sub-PennEPI02198`, `sub-PennEPI02201` |
| iEEG only (2) | `sub-PennEPI00202`, `sub-PennEPI02154` |
| Both EEG and iEEG | **0** |

Each participant-level listing contained the modality directory above and a `*_scans.tsv` file. The modality split agrees with the primary article, which reports scalp EEG for 11 patients and intracranial EEG for two patients. The NEMAR catalog's combined `EEG, IEEG` modality labels describe the dataset as a whole; they do not indicate within-participant pairing.

## Reproduction procedure

The following read-only PowerShell procedure requests only NEMAR's JSON directory listings. It does not request signal files:

```powershell
$base = 'https://data.nemar.org/nm000456/v1.0.2'
$root = Invoke-RestMethod -Uri "$base/?format=json"
foreach ($subject in $root.children | Where-Object { $_.kind -eq 'dir' -and $_.name -like 'sub-*' }) {
  $entry = Invoke-RestMethod -Uri "$base/$($subject.name)/?format=json"
  $modalities = @($entry.children | Where-Object { $_.kind -eq 'dir' } | ForEach-Object name)
  [pscustomobject]@{ subject = $subject.name; modalities = ($modalities -join ',') }
}
```

The pinned version is important: NEMAR versions may change. A future release must be audited again before any protocol uses it.

## B4 interpretation

This release cannot support paired EEG-to-SEEG prediction or a scalp-to-intracranial source validation, regardless of its combined modality label. It therefore does not meet the active B4 requirement for a simultaneous independent intracranial reference. No change to B4, B5, or B6 status is warranted. The dataset may remain relevant to separate scalp-only seizure monitoring or iEEG-only analyses, which are outside this GBF source-distinguishability evaluation.

This audit establishes only the released modality pairing. It does not certify sensor geometry, participant-specific forward models, endpoint validity, or adequacy for other analyses.

## Sources

- [NEMAR nm000456 v1.0.2 record](https://nemar.org/dataset/nm000456?v=v1.0.2) and its [versioned directory listing](https://data.nemar.org/nm000456/v1.0.2/?format=json).
- [Goldblum et al., *Human–artificial intelligence collaboration for comanaging epilepsy in real time*, Nature Medicine (2026)](https://doi.org/10.1038/s41591-026-04680-4). The paper reports 13 enrolled participants: 11 with scalp EEG and two with iEEG.
