from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/track_b/audit_nemar_eeg_ieeg_catalog.py"
SPEC = importlib.util.spec_from_file_location("nemar_catalog_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_modality_tokens_do_not_confuse_ieeg_with_eeg() -> None:
    assert MODULE.modality_tokens("ieeg") == {"ieeg"}
    assert MODULE.modality_tokens("eeg") == {"eeg"}


def test_modality_tokens_accept_both_exact_catalog_labels() -> None:
    tokens = MODULE.modality_tokens("eeg,ieeg,motion")
    assert {"eeg", "ieeg"}.issubset(tokens)


def test_modality_tokens_normalize_whitespace_case_and_list_values() -> None:
    assert MODULE.modality_tokens(" EEG, IEEG ") == {"eeg", "ieeg"}
    assert MODULE.modality_tokens(["EEG", "IEEG"]) == {"eeg", "ieeg"}
