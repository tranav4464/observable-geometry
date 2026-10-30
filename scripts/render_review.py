"""Create a standalone readable review packet from the local Markdown docs."""
from pathlib import Path
from html import escape
import markdown
import os
import re

root = Path(__file__).resolve().parents[1]
run_id = os.environ.get("TRACKA_RUN_ID", "localize_sub01_run01")
output_path = root / "outputs" / run_id / "foundation_review.html"
files = [
    ("track-a/completion-report.md", "track-a-completion"),
    ("track-a/audit-2026-10-22.md", "track-a-audit"),
    ("foundation/review-decisions.md", "review-decisions"),
    ("planning/two-track-execution-plan.md", "two-track-plan"),
    ("foundation/foundation-protocol.md", "foundation-protocol"),
    ("foundation/recoverable-source-geometry.md", "recoverable-source-geometry"),
    ("foundation/implementation-readiness.md", "implementation-readiness"),
    ("planning/master-plan.md", "master-plan"),
    ("foundation/research-audit.md", "research-audit"),
    ("foundation/mathematics.md", "mathematics"),
    ("foundation/architecture.md", "architecture"),
    ("foundation/reverse-engineering.md", "reverse-engineering"),
    ("foundation/validation.md", "validation"),
    ("foundation/decisions.md", "decisions"),
]
sections, nav = [], []


def rebase_links(rendered: str, source: Path, destination_directory: Path) -> str:
    """Keep local links valid when nested Markdown is merged into one HTML file."""
    def replace(match: re.Match[str]) -> str:
        attribute, quote, target = match.groups()
        if target.startswith(("#", "http://", "https://", "mailto:", "data:", "javascript:")):
            return match.group(0)
        path, separator, fragment = target.partition("#")
        if not path:
            return match.group(0)
        resolved = (source.parent / path).resolve()
        relative = os.path.relpath(resolved, destination_directory).replace("\\", "/")
        rewritten = relative + (separator + fragment if separator else "")
        return f"{attribute}={quote}{rewritten}{quote}"

    return re.sub(r'(href|src)=(["\'])(.*?)(?:\2)', replace, rendered)


for relative_path, section_id in files:
    source = root / "docs" / relative_path
    content = source.read_text(encoding="utf-8")
    label = content.splitlines()[0].lstrip('# ')
    nav.append(f'<a href="#{section_id}">{escape(label)}</a>')
    rendered = markdown.markdown(content, extensions=['tables', 'fenced_code'])
    rendered = rebase_links(rendered, source, output_path.parent)
    sections.append(f'<article id="{section_id}">' + rendered + '</article>')
css = '''body{margin:0;background:#f3f5f7;color:#1e293b;font:17px/1.65 system-ui,sans-serif} main{max-width:1050px;margin:35px auto;padding:0 25px}article,header{background:white;padding:38px;margin-bottom:25px;border-radius:12px;box-shadow:0 2px 9px #192c4110}h1{font-size:30px;line-height:1.2}h2{font-size:23px;margin-top:35px}h3{font-size:19px}a{color:#125bb3}nav a{display:block;padding:5px 0}table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow:auto}td,th{padding:12px;border:1px solid #d8dfe8;vertical-align:top}th{background:#eff4fa}pre{background:#eff3f7;padding:16px;overflow:auto;font-size:14px}code{font-size:.88em}.status{background:#fff3cf;padding:14px;border-radius:7px}@media print{body{background:white;font-size:11pt}main{margin:0;padding:0}article,header{box-shadow:none;padding:0}article{break-before:page}table{display:table}nav{display:none}}'''
html = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Observable Geometry | Foundation Review</title><style>'+css+'</style><main><header><p>TRANAV TYAGI / FOUNDATION BUILD / 22 OCTOBER 2026</p><h1>Observable Geometry</h1><p>Track A is verified as a reproducible engineering foundation in a cold, uniquely named run with validated inputs, regenerated geometry caches, adversarial checks and a sealed run manifest.</p><p class="status"><strong>Scientific scope:</strong> results concern six stimulation pulse-artifact sites from one participant. They do not validate physiological source recovery, population performance, or a novel RSG method. Track B should begin with prior-art and task-validity decisions, not a breakthrough claim.</p><p><a href="foundation_report.html">Open the interactive Track A result</a></p><nav>'+''.join(nav)+'</nav></header>'+''.join(sections)+'</main></html>'
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(html, encoding='utf-8')
print(output_path)
