#!/usr/bin/env python3
"""Export only the maintained static website, without Git or private backups."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from build_site import build

ROOT = Path(__file__).resolve().parent.parent


def export(destination=None):
    destination = destination or ROOT / '.mirror/rebuild/ezuno-static-clean.zip'
    site = build()
    paths = [path for path in site.rglob('*') if path.is_file()]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            if not path.resolve().is_relative_to(site) or path.is_symlink():
                raise ValueError('Export source outside project')
            archive.write(path, path.relative_to(site).as_posix(),
                          compress_type=ZIP_STORED if path.suffix == '.zip' else ZIP_DEFLATED)
    print(f'Exported {len(set(paths))} files to {destination}')
    return destination


if __name__ == '__main__':
    export()
