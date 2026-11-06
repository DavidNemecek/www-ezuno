#!/usr/bin/env python3
"""Store the existing installer in Git-safe parts and restore its exact bytes.

The deployed website always serves one ordinary ZIP file. Parts are build inputs,
not browser downloads, and no Git LFS or GitHub Release is involved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / 'download-source'
MANIFEST = SOURCE_DIR / 'manifest.json'
FILENAME = 'ezuno-5.10.19-Installation-Package.zip'
EXPECTED_SIZE = 411970655
EXPECTED_SHA256 = 'f0be70bc5429b551ad54cec24c579d4a3a8b9c865b81b0cbf7bb767877e672c3'
PART_SIZE = 48 * 1024 * 1024
BUFFER_SIZE = 4 * 1024 * 1024


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(BUFFER_SIZE), b''):
            digest.update(block)
    return digest.hexdigest()


def split_source(source):
    """One-time preparation from the supplied, already purchased installer."""
    source = Path(source).resolve(strict=True)
    if source.stat().st_size != EXPECTED_SIZE or sha256_file(source) != EXPECTED_SHA256:
        raise ValueError('Source ZIP does not match the reviewed original installer')
    with ZipFile(source) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise ValueError('Source ZIP CRC check failed: ' + bad)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    parts = []
    with source.open('rb') as stream:
        index = 1
        while True:
            block = stream.read(PART_SIZE)
            if not block:
                break
            name = FILENAME + f'.part{index:03d}'
            path = SOURCE_DIR / name
            digest = hashlib.sha256(block).hexdigest()
            if not path.exists() or path.stat().st_size != len(block) or sha256_file(path) != digest:
                temporary = path.with_name(path.name + '.tmp')
                temporary.write_bytes(block)
                temporary.replace(path)
            parts.append({'file': name, 'size': len(block), 'sha256': digest})
            index += 1
    manifest = {
        'format': 1,
        'filename': FILENAME,
        'size': EXPECTED_SIZE,
        'sha256': EXPECTED_SHA256,
        'part_size': PART_SIZE,
        'parts': parts,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Prepared {len(parts)} parts; original ZIP CRC and SHA-256 verified')
    return manifest


def load_manifest(path=MANIFEST):
    path = Path(path).resolve(strict=True)
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if (manifest.get('format') != 1 or manifest.get('filename') != FILENAME or
            manifest.get('size') != EXPECTED_SIZE or manifest.get('sha256') != EXPECTED_SHA256 or
            manifest.get('part_size') != PART_SIZE):
        raise ValueError('Download manifest does not identify the reviewed original installer')
    parts = manifest.get('parts')
    if not isinstance(parts, list) or not parts:
        raise ValueError('Download manifest has no parts')
    size = 0
    for index, part in enumerate(parts, 1):
        if part.get('file') != FILENAME + f'.part{index:03d}':
            raise ValueError('Unexpected or unordered installer part filename')
        if (not isinstance(part.get('size'), int) or not 0 < part['size'] <= PART_SIZE or
                not re.fullmatch(r'[0-9a-f]{64}', part.get('sha256', ''))):
            raise ValueError('Invalid installer part size or SHA-256')
        source = path.parent / part['file']
        if source.is_symlink() or not source.is_file() or source.stat().st_size != part['size']:
            raise ValueError('Missing, linked, or incomplete installer part: ' + part['file'])
        size += part['size']
    if size != EXPECTED_SIZE:
        raise ValueError('Installer part sizes do not add up to the original ZIP size')
    return manifest


def assemble(destination=None, manifest_path=MANIFEST):
    """Verify every part while writing, then atomically expose one complete ZIP."""
    manifest_path = Path(manifest_path).resolve(strict=True)
    manifest = load_manifest(manifest_path)
    destination = Path(destination) if destination is not None else ROOT / 'releases' / FILENAME
    destination = destination.resolve()
    if destination.name != FILENAME or not destination.is_relative_to(ROOT):
        raise ValueError('Installer output must use its reviewed filename inside the project')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.assembling')
    digest = hashlib.sha256()
    total = 0
    try:
        with temporary.open('wb') as output:
            for part in manifest['parts']:
                part_hash = hashlib.sha256()
                part_bytes = 0
                with (manifest_path.parent / part['file']).open('rb') as source:
                    for block in iter(lambda: source.read(BUFFER_SIZE), b''):
                        output.write(block)
                        part_hash.update(block)
                        digest.update(block)
                        part_bytes += len(block)
                if part_bytes != part['size'] or part_hash.hexdigest() != part['sha256']:
                    raise ValueError('Installer part integrity check failed: ' + part['file'])
                total += part_bytes
        if total != EXPECTED_SIZE or digest.hexdigest() != EXPECTED_SHA256:
            raise ValueError('Assembled installer differs from the original ZIP')
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    checksum = destination.with_name(destination.name + '.sha256')
    checksum.write_text(EXPECTED_SHA256 + '  ' + FILENAME + '\n', encoding='ascii', newline='\n')
    print(f'Assembled {destination}: {total} bytes, SHA-256 {digest.hexdigest()}')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    split = commands.add_parser('split', help='Prepare Git-safe parts from the reviewed original ZIP')
    split.add_argument('--source', required=True, type=Path)
    commands.add_parser('assemble', help='Restore the normal ZIP under local releases/')
    args = parser.parse_args()
    if args.command == 'split':
        split_source(args.source)
    else:
        assemble()


if __name__ == '__main__':
    main()
