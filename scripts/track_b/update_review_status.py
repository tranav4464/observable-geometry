"""Refresh gate-status badges on the GBFs-focused live review page."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "REVIEW.html"
GATES = ROOT / "docs" / "track_b" / "GATE_REGISTER.json"
CSS = {"PASS": "pass", "IN_PROGRESS": "progress", "NOT_STARTED": "pending", "FAIL": "fail", "PIVOT": "progress"}


def main() -> None:
    register = json.loads(GATES.read_text(encoding="utf-8"))
    statuses = {gate["id"]: gate["status"] for gate in register["gates"]}
    html = TARGET.read_text(encoding="utf-8")
    for gate in ("B0", "B1", "B2"):
        status = statuses[gate]
        shown = status.replace("_", " ")
        for badge_id in (f"status-{gate}", f"row-{gate}"):
            replacement = f'<span id="{badge_id}" class="tag {CSS[status]}">{shown}</span>'
            html, count = re.subn(
                rf'<span id="{badge_id}" class="tag [^"]+">.*?</span>',
                lambda _: replacement,
                html,
                count=1,
            )
            if count != 1:
                raise ValueError(f"Could not update status badge {badge_id}")
    TARGET.write_text(html, encoding="utf-8")
    print("PASS live review badges refreshed from gate register")


if __name__ == "__main__":
    main()
