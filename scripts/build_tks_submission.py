"""Package the accepted TKS snapshot without model arrays or recordings."""
from pathlib import Path
import hashlib
import html
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'outputs/track_b/astra_b8_audit_20261030/packet'
DEST = ROOT / 'dist/Observable_Geometry_TKS_20261030'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if DEST.exists():
        raise FileExistsError(f'Refusing to overwrite {DEST}')
    wheel = PACKET / 'wheel/observable_geometry-0.1.3.dev0-py3-none-any.whl'
    source = PACKET / 'source/observable_geometry_source_58570b8.zip'
    for p, expected in [(wheel, '3d38d857afd015630ae55283a24512132e6c444077fc97f971b98d410eb43c56'),
                        (source, '9ec5daca87af0fa9a27838d20ce3c412d50f912d89cdf8d31768583965067b02')]:
        if digest(p) != expected:
            raise ValueError(f'Pinned artifact changed: {p}')
    (DEST / 'package').mkdir(parents=True)
    shutil.copy2(wheel, DEST / 'package' / wheel.name)
    shutil.copy2(source, DEST / source.name)
    # Only text documentation from the repository; no research output trees.
    for p in (ROOT / 'docs').rglob('*'):
        if p.is_file() and p.suffix in {'.md', '.json', '.txt', '.xml', '.log', '.py'}:
            target = DEST / p.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
    for name in ['LICENSE', 'CITATION.cff', 'README.md']:
        shutil.copy2(ROOT / name, DEST / name)
    (DEST / 'evidence').mkdir()
    shutil.copy2(ROOT / 'docs/track_b/b8_ai_audit_20261030/requirements_resolved.txt', DEST / 'evidence/requirements_resolved.txt')
    links = [('docs/TKS_SUBMISSION.md', 'Submission overview'), ('docs/TKS_DEMO.md', 'Run the demo'),
             ('docs/TKS_PITCH.md', 'Two-minute pitch'), ('docs/track_b/B8_PASS_20261030.md', 'B8 acceptance and limits'),
             ('docs/track_b/b8_ai_audit_20261030/ASTRA_B8_AUDIT_20261030.md', 'Executed AI audit'),
             ('docs/NEXT_BUILD_REVIEW_ACTIONS.md', 'Next build and outreach feedback')]
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Observable Geometry | TKS Build</title><style>
body{margin:0;background:#eef2f6;color:#15263a;font:17px/1.6 system-ui,sans-serif}main{max-width:960px;margin:40px auto;padding:0 22px}section,header{background:white;padding:30px;border-radius:14px;margin-bottom:20px;border:1px solid #dbe3ed}h1{font-size:42px;line-height:1.12;margin:14px 0}h2{font-size:24px;margin-top:0}.label{color:#1555ab;font-weight:700}.metrics{display:flex;gap:20px;flex-wrap:wrap}.metric{flex:1;min-width:160px;background:#edf5ff;padding:18px;border-radius:10px}.metric b{display:block;font-size:30px}a{color:#174fa5}li{margin:9px 0}.note{border-left:4px solid #b57712;padding-left:18px}code{background:#eef2f6;padding:2px 4px}footer{font-size:14px;color:#4b596b} @media(max-width:600px){h1{font-size:32px}section,header{padding:22px}}</style><main>
<header><div class="label">TRANAV TYAGI · TKS COMPUTATIONAL NEUROSCIENCE BUILD</div><h1>Observable Geometry</h1><p>Inspect where an EEG model predicts similar scalp patterns for distant candidate brain sources.</p><p><strong>TKS snapshot accepted:</strong> 0.1.3.dev0 · code commit <code>58570b8</code> · 30 October 2026.</p></header>
<section><h2>What it does</h2><p>Input a verified forward model, noise covariance, source coordinates and provenance. The tool compares noise-whitened patterns and ranks distant alternatives for each source. Export a ranked CSV, numerical scores, summary and audit trail.</p><p>Use it to inspect model ambiguity before interpreting a source estimate. The pairwise diagnostic is separate from the reproduced GBF inverse workflow.</p></section>
<section><h2>Recorded verification results</h2><div class="metrics"><div class="metric"><b>8,196</b>modeled source locations</div><div class="metric"><b>40,980</b>directed ranked rows</div><div class="metric"><b>Exact</b>installed-wheel output replay</div></div><p>Fresh archive run: 209 tests passed, two documented skips. Both skipped cases passed separately with local workspace evidence. A separate calculation reproduced every ranking.</p><p>Median best distant similarity: <strong>0.91556</strong> at 20 mm minimum separation. This is a modeled similarity score, not a localization probability. These are saved results, not a live analysis.</p></section>
<section><h2>Open the build</h2><ul>LINKS</ul></section>
<section><h2>Scope of acceptance</h2><p class="note">B8 passed under the owner's accepted same-host AI reproduction criterion. External human review is deferred. This build does not establish endogenous neural-source recovery, a novel mathematical method or improved researcher decisions.</p><p>WSGZP geometry verification and measured-source validation are future extensions. The portable bundle excludes licensed model inputs and recordings; use your own verified model or the existing local demonstration inputs.</p></section>
<footer>Source code: BSD-3-Clause. Dataset terms and upstream GBF licensing remain separate. The software commit and wheel are pinned; current submission documentation records later acceptance.</footer></main></html>'''
    page = page.replace('LINKS', ''.join(f'<li><a href="{html.escape(p)}">{html.escape(label)}</a></li>' for p, label in links))
    for path, _ in links:
        if not (DEST / path).is_file():
            raise FileNotFoundError(path)
    (DEST / 'START_HERE.html').write_text(page, encoding='utf-8')
    (ROOT / 'TKS_BUILD.html').write_text(page, encoding='utf-8')
    (DEST / 'START_HERE.md').write_text('# Observable Geometry TKS submission\n\nOpen START_HERE.html, then docs/TKS_DEMO.md for installation and execution.\n\nThe package and source archive are the audited 58570b8 software. Outer documentation records subsequent B8 acceptance. No recordings or model arrays are included. SHA256_MANIFEST.json identifies every packaged file.\n', encoding='utf-8')
    files = sorted(p for p in DEST.rglob('*') if p.is_file())
    manifest = {p.relative_to(DEST).as_posix(): digest(p) for p in files}
    (DEST / 'SHA256_MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
    archive = DEST.with_suffix('.zip')
    if archive.exists():
        raise FileExistsError(archive)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(DEST).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name, h in manifest.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == h
        assert not any(n.endswith(('.npz', '.fif', '.edf', '.nii', '.nii.gz')) for n in z.namelist())
    receipt = {'status': 'PASS', 'scope': 'Submission packaging; software evidence remains pinned to 58570b8', 'file_count': len(manifest), 'zip_sha256': digest(archive), 'zip_bytes': archive.stat().st_size}
    archive.with_suffix('.verification.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    print(archive)


if __name__ == '__main__':
    main()
