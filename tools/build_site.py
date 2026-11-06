#!/usr/bin/env python3
"""Build the whitelisted static website and its ordinary installer download."""
import json
from pathlib import Path
import shutil
import tempfile

from package_download import FILENAME, assemble
from check_licenses import check_licenses

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / '_site'
PAGE_FILES = (
    'index.html', 'download/index.html', 'support/index.html',
    'blog-page/index.html', 'terms-of-use/index.html', 'our-terms-of-use/index.html',
    'our-privacy-policy/index.html', 'ezuno-end-user-license-agreement-eula/index.html',
    'home/index.html', 'home/modern-tools/index.html', 'home/features/index.html',
    'home/our-video/index.html', 'home/our-pricing/index.html', 'home/clients/index.html',
    'home/contact/index.html', 'home/our-solutions/index.html',
    'home/testimonials/index.html', 'home/our-team/index.html',
    'home/subscribe/index.html', 'home/upper-footer/index.html',
)


def site_sources():
    """Explicit allowlist: never publish tooling, Git, chunks, or private backups."""
    manifest = json.loads((ROOT / 'snapshot.json').read_text(encoding='utf-8'))
    if set(manifest['pages']) != set(PAGE_FILES) or len(manifest['pages']) != len(PAGE_FILES):
        raise ValueError('Snapshot page inventory differs from the reviewed 20-page site')
    paths = [ROOT / name for name in PAGE_FILES]
    for name in ('assets', 'licenses'):
        paths.extend(path for path in (ROOT / name).rglob('*') if path.is_file())
    paths.extend(ROOT / name for name in ('.nojekyll', 'CNAME', 'LICENSE-REVIEW.md'))
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or not path.is_file():
            raise ValueError('Missing, linked, or non-project website source: ' + str(path))
    return sorted(set(paths))


def build():
    sources = site_sources()
    output = OUTPUT.resolve()
    # This is the only directory the builder may replace recursively.
    if output != ROOT.resolve() / '_site' or OUTPUT.is_symlink():
        raise ValueError('Unexpected build output directory')
    cache = ROOT / '.mirror'
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pages-build-', dir=cache) as temporary:
        stage = Path(temporary).resolve()
        if not stage.is_relative_to(ROOT.resolve() / '.mirror'):
            raise ValueError('Unexpected staging directory')
        for source in sources:
            destination = stage / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        check_licenses(stage, PAGE_FILES)
        assemble(stage / 'releases' / FILENAME)
        size = sum(path.stat().st_size for path in stage.rglob('*') if path.is_file())
        if size >= 1024 * 1024 * 1024:
            raise ValueError('Built website exceeds the GitHub Pages 1 GiB site limit')
        if output.exists():
            shutil.rmtree(output)
        # Both checked absolute paths remain inside this project. No shell move
        # or deletion command receives computed paths.
        shutil.move(str(stage), str(output))
    print(f'Built {len(sources) + 2} files ({size:,} bytes) in {output}')
    print('Installer URL: releases/' + FILENAME)
    return output


if __name__ == '__main__':
    build()
