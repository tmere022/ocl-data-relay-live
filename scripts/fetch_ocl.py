#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

DATASETS = {
    'communications': {
        'url': 'https://lobbycanada.gc.ca/media/mqbbmaqk/communications_ocl_cal.zip',
        'asset': 'communications_ocl_cal.zip',
        'minimum_bytes': 1_000_000,
        'required': [
            'Communication_PrimaryExport.csv',
            'Communication_DpohExport.csv',
            'Communication_SubjectMattersExport.csv',
            'Communication_SubjectMatterDetailsExport.csv',
            'Codes_SubjectMatterTypesExport.csv',
        ],
    },
    'registrations': {
        'url': 'https://lobbycanada.gc.ca/media/zwcjycef/registrations_enregistrements_ocl_cal.zip',
        'asset': 'registrations_enregistrements_ocl_cal.zip',
        'minimum_bytes': 5_000_000,
        'required': ['Registration_PrimaryExport.csv'],
    },
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36',
    'Accept': 'application/zip, application/octet-stream;q=0.9, */*;q=0.8',
    'Referer': 'https://lobbycanada.gc.ca/en/open-data',
}

def download(url, destination):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=600) as response, open(destination, 'wb') as output:
        content_type = response.headers.get('Content-Type', '').lower()
        if response.status != 200:
            raise RuntimeError(f'Unexpected HTTP status {response.status}')
        if 'text/html' in content_type:
            raise RuntimeError('OCL returned HTML instead of a ZIP archive')
        shutil.copyfileobj(response, output, length=1024 * 1024)

def validate_zip(path, spec):
    size = path.stat().st_size
    if size < spec['minimum_bytes']:
        raise RuntimeError(f'{path.name} is implausibly small: {size} bytes')
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'CRC validation failed for {bad}')
        names = {Path(name).name for name in archive.namelist()}
        missing = [name for name in spec['required'] if name not in names]
        if missing:
            raise RuntimeError(f'Missing required files: {missing}')
    digest = hashlib.sha256()
    with open(path, 'rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return size, digest.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        'schema_version': 1,
        'version': args.tag,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'datasets': {},
    }
    for name, spec in DATASETS.items():
        pending = output / (spec['asset'] + '.partial')
        final = output / spec['asset']
        download(spec['url'], pending)
        size, sha256 = validate_zip(pending, spec)
        pending.replace(final)
        manifest['datasets'][name] = {
            'source_url': spec['url'],
            'download_url': f"https://github.com/{args.repository}/releases/download/{args.tag}/{spec['asset']}",
            'bytes': size,
            'sha256': sha256,
            'required_files': spec['required'],
        }
        print(f'{name}: {size} bytes, sha256={sha256}')
    with open(output / 'manifest.json', 'w', encoding='utf-8') as handle:
        json.dump(manifest, handle, indent=2)
        handle.write('\n')

if __name__ == '__main__':
    main()
