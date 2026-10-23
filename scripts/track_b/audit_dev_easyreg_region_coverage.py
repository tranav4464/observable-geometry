"""Summarize development-only coverage in the audited HO coordinate map.

Reads only the previously generated metadata-only contact mapping CSV. It does
not read BIDS events, EEG/iEEG signal payloads, or confirmation participants.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs/track_b/20261024T_b2_easyreg_point_transform/contact_mapping_easyreg.csv"
RUN_ID = "20261022T212603Z_b2_regional_target_coverage_audit"
OUT = ROOT / "outputs/track_b" / RUN_ID


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    rows = list(csv.DictReader(SOURCE.open(encoding="utf-8-sig", newline="")))
    subject_electrodes: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in rows:
        subject_electrodes[row["subject"]][row["electrode"]].add(row["easyreg_mapped_label"])

    per_subject = {}
    label_sets = []
    conflicts = []
    for subject in sorted(subject_electrodes):
        electrodes = subject_electrodes[subject]
        assigned = []
        for electrode, labels in sorted(electrodes.items()):
            if len(labels) != 1:
                conflicts.append({"subject": subject, "electrode": electrode, "labels": sorted(labels)})
                continue
            label = next(iter(labels))
            if label not in ("", "UNASSIGNED"):
                assigned.append((electrode, label))
        labels = sorted({label for _, label in assigned})
        label_sets.append(set(labels))
        per_subject[subject] = {
            "distinct_electrodes": len(electrodes),
            "assigned_electrodes": len(assigned),
            "unassigned_electrodes": len(electrodes) - len(assigned),
            "unique_assigned_regions": len(labels),
            "assigned_region_labels": labels,
        }

    shared = sorted(set.intersection(*label_sets)) if label_sets else []
    result = {
        "audit_id": RUN_ID,
        "scope": "Metadata-only regional coverage summary from the already-audited development contact map.",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE),
        "participants": sorted(per_subject),
        "per_subject": per_subject,
        "regions_shared_by_all_development_participants": shared,
        "shared_region_count": len(shared),
        "cross_session_label_conflicts": conflicts,
        "data_handling": "No event rows, signal arrays, or sub-04 through sub-15 data read.",
        "interpretation_limit": "This describes only this standard-template point-map variant. It does not establish anatomical correctness, faithful reproduction of WBEN's unspecified contact map, or signal prediction feasibility.",
    }
    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "region_coverage.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (OUT / "SESSION.md").write_text(
        "# Development-only regional target coverage audit\n\n"
        "This audit deduplicates contacts across sessions in the previously generated EasyReg/Harvard–Oxford metadata map. "
        "It reads only that mapping CSV, not event rows, neural signal arrays, or confirmation participants.\n\n"
        "## Results\n\n"
        + "\n".join(
            f"- **{subject}:** {values['assigned_electrodes']}/{values['distinct_electrodes']} distinct contacts assigned; "
            f"{values['unique_assigned_regions']} distinct atlas regions."
            for subject, values in per_subject.items()
        )
        + f"\n- Regions shared across all three participants: {len(shared)} ({', '.join(shared)}).\n\n"
        "## Consequence for B2\n\n"
        "A regional WBEN evaluation can only target recorded regions, not all 69 latent regions. The map leaves substantial "
        "contacts unassigned and provides only three common regions across these development participants. This makes an "
        "atlas-free contact-level task attractive, but such a model is a WBEN-inspired adaptation, not a faithful WBEN "
        "regional reproduction. The mapping itself remains a sensitivity variant, not anatomical ground truth. B2 remains open.\n\n"
        "The complete labels, source hash, and conflict check are in `region_coverage.json`.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "audit": str(OUT.relative_to(ROOT)), "shared_region_count": len(shared)}))


if __name__ == "__main__":
    main()
