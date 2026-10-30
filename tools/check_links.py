#!/usr/bin/env python3
"""Check local HTML/CSS references without making network requests."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
errors = []
checked = 0


def check(value, source):
    global checked
    parsed = urlsplit(value.strip())
    if parsed.scheme or parsed.netloc or not parsed.path:
        return
    checked += 1
    target = source.parent / unquote(parsed.path)
    if not target.exists():
        errors.append(f'{source.relative_to(ROOT)}: missing {value}')


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if not value:
                continue
            if key in ['src', 'href', 'poster', 'data-src']:
                check(value, self.source)
            elif key in ['srcset', 'data-srcset'] and not value.startswith('data:'):
                for item in value.split(','):
                    check(item.strip().split()[0], self.source)


pages = [ROOT / p for p in json.loads((ROOT / 'snapshot.json').read_text())['pages']]
for page in pages:
    parser = Links()
    parser.source = page
    parser.feed(page.read_text())
for css in (ROOT / 'assets').glob('*.css'):
    for value in re.findall(r'url\([\'\"]?([^\)\'\"]+)', css.read_text()):
        check(value, css)
if list(ROOT.glob('**/*.php')):
    errors.append('Unexpected PHP file')
print(f'{len(pages)} HTML pages, {checked} local references checked.')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('OK: all local resources exist; no PHP files.')
