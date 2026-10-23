# B4 NEMAR catalog-wide paired-modality screen

**Screen date:** 24 October 2026  
**Purpose:** Identify publicly indexed NEMAR releases with both EEG and iEEG modality labels, then determine from versioned metadata whether any newly indexed candidate meets the active GBF source-distinguishability requirements.  
**Data boundary:** Catalog/API metadata, README text, and JSON directory listings only. No EEG, iEEG, ECoG, outcome, or derived signal arrays were opened.

## Query and result

The NEMAR dataset API was queried with `modality=eeg,ieeg`, `limit=200`, and offsets `0, 200, 400, 600, 800`. It returned 814 records with either modality. Filtering the returned `modalities` values as exact comma-separated tokens (`eeg` **and** `ieeg`, rather than substring matching) yielded four dataset-level records on the query date:

| Dataset | Version and license | Pairing/geometry finding | Relevance to active GBF estimand |
|---|---|---|---|
| `on004752` | v1.0.0, CC0 | Fifteen participants; simultaneous low-density scalp EEG and depth iEEG. MNI contact coordinates are available, but no verified individual MRI/head-model contract. | Already screened in B1/B4 and heavily analyzed in adjacent paired EEG/iEEG work. Does not meet the frozen participant-specific forward-model requirement. |
| `nm000456` | v1.0.2, CC-BY-NC-SA-4.0 | Thirteen participant folders: 11 EEG-only and two iEEG-only; zero participants contain both. | Combined catalog labels do not represent within-participant pairing. Excluded; see `B4_NEMAR_NM000456_PAIRING_AUDIT_20261024.md`. |
| `nm000434` (SenseFOG) | v1.0.1, CC-BY-4.0 | Catalog record lists 12 participants. Versioned directory listings show 11 with EEG, STN local-field-potential recordings, and motion; one has motion only. The release README says electrode coordinates are unavailable (`x/y/z = n/a`) and gives target labels only. It does not provide participant MRI or an individualized head model. EEG, LFP, and motion are not resampled or aligned to each other in the BIDS release; the release documents alignment to a stimulation artifact at recording start. | A possible distinct scalp-EEG/STN-LFP association or prediction dataset, but not a valid individual-forward-model/source-pair test. The disease/task and signal target also differ from the active source-distinguishability estimand. |
| `on001785` | v1.0.0, CC0 | NEMAR record and README describe scalp EEG from healthy participants and ECoG from one epilepsy patient. Versioned session listings place EEG under 18 healthy-participant folders and iEEG under a separate `sub-patient` folder; no participant has both. The archive lists 19 participant folders, despite the README describing 20 healthy participants plus the patient. | The dataset-level EEG+iEEG labels combine separate cohorts, so there is no paired scalp–intracranial evaluation. It also lacks the active participant-specific geometry contract. |

The screen is an index-level census of NEMAR records returned by the specified query at that time. The catalog can change, may use modality labels that aggregate separate cohorts, and is not proof that no qualifying dataset exists elsewhere. The two new candidates (`nm000434` and `on001785`) do not reopen B4 for the current estimand. The query and participant-directory checks are reproducible with `scripts/track_b/audit_nemar_eeg_ieeg_catalog.py`; its metadata-only result is preserved at `outputs/track_b/20261024_b4_nemar_catalog_screen/catalog_screen.json`. The script refuses to overwrite that evidence path.

## Reproduction procedure

The API query can be repeated with the following PowerShell procedure. The exact-token check is intentional because `eeg` is a substring of `ieeg` in a case-insensitive filter.

```powershell
$all = @()
foreach ($offset in @(0, 200, 400, 600, 800)) {
  $url = "https://api.nemar.org/datasets?modality=eeg%2Cieeg&limit=200&offset=$offset"
  $page = Invoke-RestMethod -Uri $url
  $all += @($page.datasets)
}
$both = $all | Where-Object {
  $tokens = @($_.modalities -split ',')
  ($tokens -contains 'eeg') -and ($tokens -contains 'ieeg')
}
$both | Select-Object dataset_id, name, latest_version, license, participants, modalities
```

For subject-level modality checks, inspect only JSON directory listings under the pinned release, for example:

```powershell
$base = 'https://data.nemar.org/nm000434/v1.0.1'
$root = Invoke-RestMethod -Uri "$base/?format=json"
foreach ($subject in $root.children | Where-Object { $_.kind -eq 'dir' -and $_.name -like 'sub-*' }) {
  $entry = Invoke-RestMethod -Uri "$base/$($subject.name)/?format=json"
  # For datasets with session directories, inspect the session listing too.
  $subject.name
}
```

The API and NEMAR object-store listings are mutable. A later use must re-pin the dataset version and repeat pairing, file inventory, license, geometry, and alignment checks. This procedure is metadata-only and must not be treated as analysis of the neural recordings.

## Gate consequence

No candidate in this catalog screen satisfies the active requirements for a real-data test of GBF source-pattern distinguishability under a verified participant-specific forward model and independent spatial reference. B4–B6 remain **PIVOT**. This result does not establish that no suitable dataset exists; it narrows only the queried NEMAR catalog. It does not change the B8 external-review requirement or authorize signal-data access.

## Sources

- [NEMAR API dataset search](https://api.nemar.org/datasets?modality=eeg%2Cieeg&limit=200&offset=0), queried across five pages on 24 October 2026.
- The exact query and directory-listing implementation is `scripts/track_b/audit_nemar_eeg_ieeg_catalog.py`; captured metadata-only result: `outputs/track_b/20261024_b4_nemar_catalog_screen/catalog_screen.json`.
- [NEMAR `nm000434` v1.0.1 record](https://www.nemar.org/dataset/nm000434?v=v1.0.1) and [versioned object listing](https://data.nemar.org/nm000434/v1.0.1/?format=json). The record README describes 48-channel scalp EEG, bipolar STN LFP, motion data, absent contact coordinates, alignment limitations, and CC-BY-4.0 terms.
- Klocke et al., [“Supraspinal contributions to defective antagonistic inhibition and freezing of gait in Parkinson’s disease,” *Brain* (2024)](https://doi.org/10.1093/brain/awae223). The primary article describes subthalamic LFP, surface EMG, and gait recordings during walking/freezing, not a participant-specific EEG source-imaging evaluation.
- [NEMAR `on001785` v1.0.0 record](https://www.nemar.org/dataset/on001785?v=v1.0.0) and [versioned object listing](https://data.nemar.org/on001785/v1.0.0/?format=json). The record README describes EEG recordings from healthy participants and a separate ECoG patient; the directory listing separates `eeg/` and `ieeg/` into different participant folders.
- Pereira et al., [“Evidence accumulation relates to perceptual consciousness and monitoring,” *Nature Communications* (2021)](https://doi.org/10.1038/s41467-021-23540-y). The paper reports intracranial evidence from one patient and EEG generalization in healthy volunteers, rather than same-participant paired scalp/intracranial recordings.
- Existing `on004752` and `nm000456` assessments are documented in `B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md` and `B4_NEMAR_NM000456_PAIRING_AUDIT_20261024.md`.
