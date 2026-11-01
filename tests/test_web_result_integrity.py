from argparse import Namespace
from pathlib import Path

import pytest

from observable_geometry.cli import run_distinguish
from observable_geometry.web_results import verify_completed_run


def make_run(tmp_path: Path) -> Path:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "run"
    run_distinguish(Namespace(
        bundle=root / "examples/browser_algebra_demo.npz",
        metadata=root / "examples/browser_algebra_demo_metadata.json",
        output=output,
        minimum_distance_mm=20.0,
        top_k=3,
        block_size=128,
    ))
    return output


def test_browser_accepts_complete_run_with_matching_manifest(tmp_path):
    assert verify_completed_run(make_run(tmp_path))["source_count"] == 4


def test_browser_rejects_modified_csv(tmp_path):
    output = make_run(tmp_path)
    with (output / "ranked_pairs.csv").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValueError, match="ranked_pairs.csv"):
        verify_completed_run(output)


def test_browser_rejects_missing_manifest(tmp_path):
    output = make_run(tmp_path)
    (output / "run_manifest.json").unlink()
    with pytest.raises(ValueError, match="run_manifest.json"):
        verify_completed_run(output)
