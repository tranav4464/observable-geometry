from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import observable_geometry

if importlib.util.find_spec("streamlit") is None:
    pytest.skip("web extra is not installed", allow_module_level=True)

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = Path(observable_geometry.__file__).resolve().parent / "web_app.py"
DEMO = ROOT / "examples"


def _run_model_form(at: AppTest, bundle: Path, metadata: Path, output: Path) -> AppTest:
    at.radio[0].set_value("Run a model").run()
    fields = {widget.label: widget for widget in at.text_input}
    fields["Model-only NPZ bundle (absolute path)"].set_value(str(bundle))
    fields["Matching metadata JSON (absolute path)"].set_value(str(metadata))
    fields["New output directory (absolute path)"].set_value(str(output))
    at.run()
    button = next(widget for widget in at.button if widget.label == "Run diagnostic")
    return button.click().run()


def test_browser_run_model_form_creates_and_displays_verified_result(tmp_path):
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    output = tmp_path / "web-run"

    _run_model_form(
        at,
        DEMO / "browser_algebra_demo.npz",
        DEMO / "browser_algebra_demo_metadata.json",
        output,
    )

    assert not at.exception
    assert any("Run complete" in item.value for item in at.success)
    assert (output / "run_manifest.json").is_file()
    assert len(at.metric) == 3
    assert at.session_state["result_directory"] == str(output.resolve())


def test_failed_browser_run_clears_previous_result(tmp_path):
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    output = tmp_path / "successful-run"
    _run_model_form(
        at,
        DEMO / "browser_algebra_demo.npz",
        DEMO / "browser_algebra_demo_metadata.json",
        output,
    )
    assert len(at.metric) == 3

    fields = {widget.label: widget for widget in at.text_input}
    fields["Model-only NPZ bundle (absolute path)"].set_value(str(tmp_path / "missing.npz"))
    fields["New output directory (absolute path)"].set_value(str(tmp_path / "failed-run"))
    at.run()
    button = next(widget for widget in at.button if widget.label == "Run diagnostic")
    button.click().run()

    assert not at.exception
    assert any("input bundle does not exist" in item.value for item in at.error)
    assert not at.metric
    assert "result_directory" not in at.session_state
    assert not (tmp_path / "failed-run").exists()
