"""Validate Track B gate dependencies and evidence paths; read-only."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from observable_geometry.track_b.gates import validate_gate_register


REGISTER = ROOT / "docs" / "track_b" / "GATE_REGISTER.json"


def main() -> None:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    errors = validate_gate_register(register, ROOT)
    if errors:
        raise SystemExit("FAIL Track B gate register:\n- " + "\n- ".join(errors))
    summary = {gate["id"]: gate["status"] for gate in register["gates"]}
    print(json.dumps({"status": "PASS", "gates": summary,
                      "evidence_paths_checked": sum(len(g.get("evidence", [])) for g in register["gates"]),
                      "read_only": True}, indent=2))


if __name__ == "__main__":
    main()
