"""Fetch explicitly selected Localize-MI annex payloads and verify dataset MD5.

Metadata must first be cloned into data/Localize-MI. Raw recordings are kept
outside that metadata checkout; no files from the dataset are redistributed.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    *[f'derivatives/epochs/sub-01/eeg/sub-01_task-seegstim_run-{run:02d}_epochs.npy'
      for run in range(1, 12)],
    'derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif',
    'derivatives/sourcemodelling/sub-01/anat/sub-01_hemi-L_pial.surf.gii',
    'derivatives/sourcemodelling/sub-01/anat/sub-01_hemi-R_pial.surf.gii',
]


def main():
    records = []
    for relative in PATHS:
        metadata_file = ROOT/'data/Localize-MI'/relative
        pointer = metadata_file.read_text().strip()
        match = re.search(r'MD5-s(\d+)--([0-9a-f]{32})', pointer)
        destination = ROOT/'data/payload'/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not match:
            if pointer.startswith('<?xml') and '<GIFTI' in pointer:
                shutil.copyfile(metadata_file, destination)
                records.append({'path': relative, 'bytes': destination.stat().st_size,
                    'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                    'source': 'verified metadata checkout Git-tracked GIFTI'})
                continue
            raise ValueError(f'Unrecognized annex pointer: {relative}')
        size, expected = int(match[1]), match[2]
        url = 'https://gin.g-node.org/ezemikulan/Localize-MI/raw/master/' + relative
        if not destination.exists():
            temporary = destination.with_suffix(destination.suffix + '.partial')
            digest = hashlib.md5()
            received = 0
            print(f'Downloading {relative}: {size/1e6:.1f} MB', flush=True)
            with urllib.request.urlopen(url, timeout=90) as response, temporary.open('wb') as out:
                while chunk := response.read(1024*1024):
                    out.write(chunk)
                    digest.update(chunk)
                    received += len(chunk)
            if received != size or digest.hexdigest() != expected:
                raise ValueError(f'Payload verification failed for {relative}: {received}/{size}')
            temporary.replace(destination)
        digest = hashlib.md5(destination.read_bytes()).hexdigest()
        if digest != expected or destination.stat().st_size != size:
            raise ValueError(f'Existing payload invalid: {relative}')
        records.append({'path': relative, 'bytes': size, 'md5': digest, 'url': url})
        print(f'Verified {relative}', flush=True)
    out = ROOT/'outputs'
    out.mkdir(exist_ok=True)
    (out/'download_manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
