#!/usr/bin/env python3
"""Check local HTML/CSS references without making network requests."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit

from static_forms import RECIPIENT

ROOT = Path(__file__).resolve().parent.parent
errors = []
checked = 0
mail_count = 0
draft_count = 0
anchors = []
page_ids = {}


def check(value, source):
    global checked
    parsed = urlsplit(value.strip())
    if parsed.scheme or parsed.netloc or not parsed.path:
        return
    checked += 1
    target = source.parent / unquote(parsed.path)
    if target.is_dir():
        target = target / 'index.html'
    if not target.exists():
        errors.append(f'{source.relative_to(ROOT)}: missing {value}')


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global mail_count, draft_count
        ident = dict(attrs).get('id')
        if ident:
            if ident in page_ids[self.source.resolve()]:
                errors.append(f'{self.source.relative_to(ROOT)}: duplicate id {ident}')
            page_ids[self.source.resolve()].add(ident)
        for key, value in attrs:
            if not value:
                continue
            if key in ['src', 'href', 'poster', 'data-src']:
                check(value, self.source)
                parsed = urlsplit(value)
                if tag == 'a' and key == 'href':
                    if parsed.scheme == 'mailto':
                        mail_count += 1
                        if parsed.path.lower() != RECIPIENT:
                            errors.append(f'{self.source.relative_to(ROOT)}: unexpected email recipient {parsed.path}')
                        query = parse_qs(parsed.query, keep_blank_values=True)
                        if dict(attrs).get('data-ezuno-mail'):
                            draft_count += 1
                        if dict(attrs).get('data-ezuno-mail') and (set(query) != {'subject', 'body'} or not all(query.values())):
                            errors.append(f'{self.source.relative_to(ROOT)}: incomplete email template')
                        elif query and (not query.get('subject', [''])[0].strip() or not query.get('body', [''])[0].strip()):
                            errors.append(f'{self.source.relative_to(ROOT)}: empty email subject or message')
                        elif query and not dict(attrs).get('data-ezuno-mail'):
                            errors.append(f'{self.source.relative_to(ROOT)}: email draft outside former form')
                    elif value.strip() == '#':
                        errors.append(f'{self.source.relative_to(ROOT)}: placeholder link #')
                    elif parsed.scheme == 'http':
                        errors.append(f'{self.source.relative_to(ROOT)}: insecure outdated link {value}')
                if tag == 'a' and key == 'href' and parsed.fragment and not parsed.scheme and not parsed.netloc:
                    anchors.append((self.source, parsed))
            elif key in ['srcset', 'data-srcset'] and not value.startswith('data:'):
                for item in value.split(','):
                    check(item.strip().split()[0], self.source)


pages = [ROOT / p for p in json.loads((ROOT / 'snapshot.json').read_text(encoding='utf-8'))['pages']]
for page in pages:
    parser = Links()
    parser.source = page
    page_ids[page.resolve()] = set()
    html = page.read_text(encoding='utf-8')
    if re.search(r'<title>[^<]*(?:nicht gefunden|not found|404)', html, re.I):
        errors.append(f'{page.relative_to(ROOT)}: copied error page instead of usable content')
    parser.feed(html)
for source, parsed in anchors:
    target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source.resolve()
    if target.is_dir():
        target = target / 'index.html'
    if target in page_ids and unquote(parsed.fragment) not in page_ids[target]:
        errors.append(f'{source.relative_to(ROOT)}: missing anchor {parsed.geturl()}')
for css in (ROOT / 'assets').glob('*.css'):
    for value in re.findall(r'url\([\'\"]?([^\)\'\"]+)', css.read_text(encoding='utf-8')):
        check(value, css)
if list(ROOT.glob('**/*.php')):
    errors.append('Unexpected PHP file')
print(f'{len(pages)} HTML pages, {checked} local references, {len(anchors)} anchor links, {draft_count} form email templates and {mail_count - draft_count} plain email links checked.')
if draft_count != 7:
    errors.append(f'Expected exactly 7 former form locations; found {draft_count}')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('OK: all local resources exist; no PHP files.')
