"""Check local article links and requested lengths before the TKS handoff."""
from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TKS = ROOT / "docs" / "tks"
FILES = [
    ROOT / "README.md",
    TKS / "README.md",
    TKS / "submission.md",
    TKS / "article-1-observable-geometry.md",
    TKS / "article-2-source-validation.md",
    TKS / "six-paper-research-matrix.md",
    TKS / "learn-build-overlap-map.md",
    TKS / "article-claim-audit.md",
    TKS / "article-2-claim-audit.md",
    TKS / "final-editorial-scientific-audit.md",
]
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def main() -> None:
    broken: list[str] = []
    for source in FILES:
        for target in LINK.findall(source.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (source.parent / target).exists():
                broken.append(f"{source.relative_to(ROOT)} -> {target}")
    words: dict[str, int] = {}
    for name in ("article-1-observable-geometry.md", "article-2-source-validation.md"):
        words[name] = len((TKS / name).read_text(encoding="utf-8").split())
    if not 2800 <= words["article-1-observable-geometry.md"] <= 3200:
        broken.append("Article 1 outside requested 2,800–3,200 words")
    if not 2600 <= words["article-2-source-validation.md"] <= 3200:
        broken.append("Article 2 outside approximately 12–13 minutes at 220–250 wpm")
    print({"article_words": words, "broken_local_links": broken})
    if broken:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
