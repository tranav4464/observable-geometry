# iES-CCEP OSF license metadata audit

**Date:** 24 October 2026  
**Purpose:** Resolve the apparent discrepancy between the OSF project license metadata and the earlier statement that no license was exposed.  
**Data boundary:** Public JSON metadata only. No archive, neural signal, MRI, event, or outcome file was downloaded or opened.

## Finding

The public OSF node `wsgzp` has a license relationship to OSF license record `563c1cf88c5e4a3877f9e96e`. That record is named **Other** and its text says: “Please see the file named license.txt in the OSF Storage of this project.” The OSF API therefore does expose a license record, so saying that the license field is null is incorrect.

A recursive metadata-only traversal of the project's visible OSF Storage listed seven files: six multipart archive pieces (`ccepcoreg-bids.z01` through `.z05` and `ccepcoreg-bids.zip`) and `additional_info/eeg_badtrials.json`. It found no file named `license.txt`. The storage API pages did not identify another visible file. The license text could be inside the multipart archive or the OSF listing could be incomplete, but checking either possibility would require opening or downloading the archive, which also contains neural data and is outside the current authorization. No reuse permission is inferred from public visibility alone.

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
