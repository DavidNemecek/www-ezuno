#!/usr/bin/env python3
"""Check the reviewed website licensing inventory using only the standard library."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
LICENSE_HASHES = {
    'licenses/KeySoft-GPL-3.0.txt': '8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903',
    'licenses/Work-Sans-OFL.txt': '2786ce9d9f2272d1382d3ccb7a6e5887ac87dba5c8dd09266ba1ceb7be16d711',
    'licenses/PT-Sans-OFL.txt': 'a816af9634aae415b38801d3f8ffb815252060c6e3d3f2b95b779436d98aa62c',
}
FONT_HASHES = {
    'assets/37ad2ec9d2-jizYRExUiTo99u79D0e0x8mI.woff2': '1f275d522571c81eb7d02d47015bf4eb1c60ab7520477bd40ba39425c1df49f2',
    'assets/46a61d7159-jizaRExUiTo99u79D0KExQ.woff2': '2dea6190c113af617923c6b71f7f10ffbdf72074556f79963610254fe40e49be',
    'assets/4ac57ec769-jizdRExUiTo99u79D0e8fOydLxUd.woff2': '064f8ebfc7134cdf0da9f34199ae15cbe100ef406d85c0187246a7bd7c57d5b6',
    'assets/57fda182a7-jizfRExUiTo99u79B_mh0O6tLQ.woff2': '05ea99a48ece3c624fd9df15f5cf4e1d94703bde9ed2b384495900f55e28befe',
    'assets/817c6cfc2c-QGYsz_wNahGAdqQ43Rh_fKDp.woff2': '1dd49afc07fb2231b2ff686cbf007725fb2742271bb1f28ebd98f22a0d817343',
}


class Notices(HTMLParser):
    def __init__(self):
        super().__init__()
        self.comments = []
        self.exceptions = []
        self.links = []
        self.in_exception = False

    def handle_comment(self, data):
        self.comments.append(data)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'p' and attrs.get('id') == 'third-party-licenses':
            self.in_exception = True
            self.exceptions.append('')
        if self.in_exception and tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'p':
            self.in_exception = False

    def handle_data(self, data):
        if self.in_exception:
            self.exceptions[-1] += data


def check_licenses(root, pages):
    root = Path(root).resolve()

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    for name, expected in {**LICENSE_HASHES, **FONT_HASHES}.items():
        path = root / name
        require(path.is_file(), 'Missing licensed component: ' + name)
        data = path.read_bytes()
        if name in LICENSE_HASHES:
            data = data.replace(b'\r\n', b'\n')
        require(hashlib.sha256(data).hexdigest() == expected,
                'Reviewed font or license text changed: ' + name)

    assets = {p.relative_to(root).as_posix() for p in (root / 'assets').rglob('*') if p.is_file()}
    fonts = {p for p in assets if Path(p).suffix.lower() in {'.woff2', '.woff', '.ttf', '.otf', '.eot'}}
    require(fonts == set(FONT_HASHES), 'Font inventory differs from the reviewed OFL fonts')
    require({p for p in assets if Path(p).suffix.lower() in {'.css', '.js', '.mjs'}} ==
            {'assets/site.css', 'assets/site.js'}, 'Unreviewed stylesheet or script in assets/')
    readme = (root / 'licenses/README.md').read_text(encoding='utf-8')
    require('GPL-3.0-only' in readme, 'Missing explicit HTML-template license in licenses/README.md')

    for name in pages:
        page = root / name
        parser = Notices()
        parser.feed(page.read_text(encoding='utf-8'))
        notices = [c for c in parser.comments if 'HTML structure adapted from KeySoft' in c]
        require(len(notices) == 1, f'{name}: missing or duplicate template attribution')
        notice = notices[0]
        require(all(text in notice for text in ('Key-Design', 'modified 2026-11-06',
                'including our modifications', 'is licensed under', 'GPL-3.0-only')),
                f'{name}: incomplete template license grant or attribution')
        references = re.findall(r'see ([^\s;]+\.(?:txt|md))', notice)
        require({(page.parent / p).resolve() for p in references} ==
                {root / 'licenses/KeySoft-GPL-3.0.txt', root / 'licenses/README.md'},
                f'{name}: incorrect relative licensing references')
        if name in ('terms-of-use/index.html', 'our-terms-of-use/index.html'):
            require(len(parser.exceptions) == 1, f'{name}: missing or duplicate license exception')
            text = ' '.join(parser.exceptions[0].split())
            require(all(part in text for part in ('restrictions in this Copyrights section',
                    'not governed by a separate license', 'GPL-licensed HTML', 'OFL-licensed fonts',
                    'take precedence over these Terms', 'Nothing in these Terms restricts rights')),
                    f'{name}: general terms do not preserve third-party license rights')
            require(len(parser.links) == 1, f'{name}: missing license inventory link')
            link = urlsplit(parser.links[0])
            require(not link.scheme and not link.netloc and
                    (page.parent / unquote(link.path)).resolve() == root / 'licenses/README.md',
                    f'{name}: license inventory link does not resolve locally')

    print(f'License checks passed: {len(pages)} HTML notices, both Terms exceptions, '
          f'{len(FONT_HASHES)} unchanged fonts and {len(LICENSE_HASHES)} complete license texts.')


if __name__ == '__main__':
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('--site', type=Path, default=ROOT)
    options = arguments.parse_args()
    pages = json.loads((ROOT / 'snapshot.json').read_text(encoding='utf-8'))['pages']
    check_licenses(options.site, pages)
