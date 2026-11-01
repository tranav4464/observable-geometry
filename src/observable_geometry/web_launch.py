"""Launch the optional local Streamlit interface."""
from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path
import subprocess
import sys


def main() -> int:
    if find_spec("streamlit") is None or find_spec("pandas") is None:
        print('Install the web extra first: python -m pip install "observable-geometry[web]"', file=sys.stderr)
        return 2
    app = Path(__file__).with_name("web_app.py")
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(app),
                            "--server.address", "127.0.0.1", "--server.port", "8501"])


if __name__ == "__main__":
    raise SystemExit(main())
