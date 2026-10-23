# iES-CCEP OSF license metadata audit

**Date:** 24 October 2026  
**Purpose:** Resolve the apparent discrepancy between the OSF project license metadata and the earlier statement that no license was exposed.  
**Data boundary:** Public JSON metadata only. No archive, neural signal, MRI, event, or outcome file was downloaded or opened.

## Finding

The public OSF node `wsgzp` has a license relationship to OSF license record `563c1cf88c5e4a3877f9e96e`. That record is named **Other** and its text says: “Please see the file named license.txt in the OSF Storage of this project.” The OSF API therefore does expose a license record, so saying that the license field is null is incorrect.

A recursive metadata-only traversal of the project's visible OSF Storage listed seven files: six multipart archive pieces (`ccepcoreg-bids.z01` through `.z05` and `ccepcoreg-bids.zip`) and `additional_info/eeg_badtrials.json`. It found no file named `license.txt`. The storage API pages did not identify another visible file. The license text could be inside the multipart archive or the OSF listing could be incomplete, but checking either possibility would require opening or downloading the archive, which also contains neural data and is outside the current authorization. No reuse permission is inferred from public visibility alone.

## EBRAINS mirror metadata route

The published 2025 study reports that the same iES-CCEP recordings were obtained from EBRAINS and are also available on OSF. A metadata-only check was made against the EBRAINS Knowledge Graph record `b1c3e79e-ca4a-4a05-9235-b93cf1cb678d`, indexed under “Simultaneous stereo-EEG and high-density scalp EEG recordings to study the effects of intracerebral stimulation parameters.” The public Search UI route returned HTTP 200 but only its HTML application shell, without the dataset-card metadata in the response. Direct GET requests to the production KG instance endpoint with `stage=RELEASED` returned HTTP 401. EBRAINS documentation states that programmatic KG access requires an EBRAINS account. No authenticated request was made, no access request was submitted, and no dataset files or signals were accessed.

This confirms a second discovery route, not a second verified license. The paper's statement that it used EBRAINS and the Search UI's “Public” listing do not expose the dataset-specific reuse conditions in the unauthenticated metadata available here. Data-use terms remain unresolved pending authorized access to the record or confirmation from the data custodian. This does not change the overlap finding: the published 2026 GBF analysis already evaluates localization on 318 sessions from 35 participants from this data family.

Relevant records: [EBRAINS dataset record](https://search.kg.ebrains.eu/instances/b1c3e79e-ca4a-4a05-9235-b93cf1cb678d), [EBRAINS Knowledge Graph API documentation](https://docs.kg.ebrains.eu/8387ccd27a186dea3dd0b949dc528842/instancesAPI.html), [EBRAINS programmatic access page](https://ebrains.eu/data-tools-services/data-knowledge/find-data), and [Momi et al. 2025](https://www.nature.com/articles/s41467-025-58187-6).

## Reproducible metadata record

Run `python scripts/track_b/audit_osf_wsgzp_license_metadata.py --output outputs/track_b/20261024_b4_osf_license_audit/osf_license_metadata_v2.json`. It traverses JSON metadata endpoints only, follows folder-listing links, never requests `links.download`, and refuses to overwrite an earlier result. The captured result records `public: true`, license `Other`, the license-file instruction, `license_file_listed: false`, and seven visible files. A test checks nested metadata traversal and that no download URL is requested.

Primary records:

- [OSF project](https://osf.io/wsgzp/)
- [OSF node API metadata](https://api.osf.io/v2/nodes/wsgzp/)
- [OSF license API record](https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96e/)
- [OSF storage root metadata](https://api.osf.io/v2/nodes/wsgzp/files/osfstorage/)
- [OSF guidance for “Other” project licenses](https://help.osf.io/article/353-welcome-to-projects)
- [Momi et al. 2025, dataset and study description](https://www.nature.com/articles/s41467-025-58187-6)

## Gate consequence

This corrects the metadata description but does not establish usable data terms. Keep the iES-CCEP candidate at metadata-screen status and do not access its archive or use its recordings. B4 remains pivoted: even if terms are clarified, the published GBF analysis already covers 318 sessions from 35 participants on this data route, so a new test would be a secondary analysis, not independent validation. Any proposed secondary estimand still needs a valid outcome, feasible independent units, explicit reuse permission, overlap accounting, and independent protocol review before data access.
