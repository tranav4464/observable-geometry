"""Shared immutable run-directory selection for Track A scripts."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = os.environ.get("TRACKA_RUN_ID", "localize_sub01_run01")
if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", RUN_ID):
    raise ValueError("TRACKA_RUN_ID must be a safe 1-80 character identifier")
OUT = ROOT / "outputs" / RUN_ID
OUT.mkdir(parents=True, exist_ok=True)
