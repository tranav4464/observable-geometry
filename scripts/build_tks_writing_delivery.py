"""Create readable article previews and a compact final handoff from audited Markdown."""

from __future__ import annotations

import argparse
import hashlib
import html
from pathlib import Path
import shutil

import markdown


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = (
    "article-1-observable-geometry.md",
    "article-2-source-validation.md",
)
EVIDENCE = (
    "six-paper-research-matrix.md",
    "article-claim-audit.md",
    "article-2-claim-audit.md",
    "learn-build-overlap-map.md",
    "final-editorial-scientific-audit.md",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--submission-zip", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    bundle = args.submission_zip.resolve()
    if out.exists():
        raise FileExistsError(out)
    if not bundle.is_file():
        raise FileNotFoundError(bundle)
    (out / "Articles").mkdir(parents=True)
    (out / "Research and Audit").mkdir()
    shutil.copy2(bundle, out / "Observable_Geometry_TKS_Build.zip")

    style = """body{max-width:780px;margin:48px auto;padding:0 22px;color:#172434;
font:18px/1.72 Georgia,serif;background:#fff}h1,h2,h3{font-family:system-ui,sans-serif;
line-height:1.2;color:#10253d}h1{font-size:2.4em}h2{margin-top:2.2em;font-size:1.4em}
p{margin:1em 0}a{color:#17579c}blockquote{border-left:4px solid #8da9c5;padding-left:18px}
table{border-collapse:collapse;font:14px/1.45 system-ui,sans-serif}th,td{border:1px solid #cad4de;
padding:8px;vertical-align:top}code{font-size:.87em}li{margin:.45em 0}
@media(max-width:700px){body{font-size:16px;margin:22px auto}table{display:block;overflow-x:auto}}"""
    for name in ARTICLES:
        src = ROOT / "docs" / "tks" / name
        content = src.read_text(encoding="utf-8")
        shutil.copy2(src, out / "Articles" / name)
        body = markdown.markdown(content, extensions=["extra", "tables", "sane_lists"])
        title = content.splitlines()[0].removeprefix("# ")
        page = ("<!doctype html><html lang=\"en\"><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                f"<title>{html.escape(title)}</title><style>{style}</style><body><article>{body}</article></body></html>")
        (out / "Articles" / name.replace(".md", ".html")).write_text(page, encoding="utf-8")
    for name in EVIDENCE:
        shutil.copy2(ROOT / "docs" / "tks" / name, out / "Research and Audit" / name)

    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    (out / "START_HERE.md").write_text(
        "# Observable Geometry: final TKS handoff\n\n"
        "Open `Observable_Geometry_TKS_Build.zip` for the portable software, demo guide, "
        "full documentation, articles and evidence. The `Articles` folder holds readable HTML "
        "previews and editable Markdown for both articles. `Research and Audit` contains the "
        "six-paper matrix, Learn overlap map and claim audits.\n\n"
        f"**Build ZIP SHA-256:** `{digest}`\n\n"
        "## Submission actions for Tranav\n\n"
        "1. Upload the Build ZIP to the TKS submission portal.\n"
        "2. Submit the two article files in the required article fields or platform.\n"
        "3. Include the research matrix and audits if the submission accepts supporting material.\n\n"
        "No article or TKS submission was published by the build process.\n",
        encoding="utf-8",
    )
    print(out)
    print(f"build_zip_sha256={digest}")


if __name__ == "__main__":
    main()
