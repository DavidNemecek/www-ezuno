#!/usr/bin/env python3
"""Build the static snapshot. Downloads are serial, cached, and rate limited."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.mirror'
ORIGIN = 'https://ezuno.com/'
BROWSER_UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')
PAGES = ['index', 'download', 'support', 'blog-page', 'terms-of-use', 'our-terms-of-use',
         'our-privacy-policy', 'ezuno-end-user-license-agreement-eula',
         'home', 'home/modern-tools', 'home/features', 'home/our-video',
         'home/our-pricing', 'home/clients', 'home/contact', 'home/our-solutions',
         'home/testimonials', 'home/our-team', 'home/subscribe', 'home/upper-footer']
CSS_URL = re.compile(r'url\(\s*[\'"]?([^\s\)\'\"]+)[\'"]?\s*\)', re.I)
MANIFEST = CACHE / 'manifest.json'
manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
last_request = 0
offline = False


def save_manifest():
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')


def get(url, expected_status=200):
    global last_request
    if url in manifest and (CACHE / manifest[url]['cache']).exists():
        if manifest[url]['status'] != expected_status:
            raise RuntimeError('Cached HTTP error: ' + url)
        return (CACHE / manifest[url]['cache']).read_bytes()
    if offline:
        raise RuntimeError('Uncached resource: ' + url)
    time.sleep(max(0, 1.5 - (time.monotonic() - last_request)))
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    dest = CACHE / 'assets' / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_request = time.monotonic()
    result = subprocess.run(['curl', '-sS', '-L', '-A', BROWSER_UA, '--connect-timeout', '15',
                             '--max-time', '60', '-o', str(dest), '-w',
                             '%{http_code}\n%{content_type}', url],
                            capture_output=True, text=True)
    info = result.stdout.split('\n')
    status = int(info[0]) if info and info[0].isdigit() else 0
    mime = info[1] if len(info) > 1 else ''
    manifest[url] = {'cache': str(dest.relative_to(CACHE)), 'status': status, 'mime': mime}
    save_manifest()
    print(f'{status} {dest.stat().st_size if dest.exists() else 0:>8} {url}', flush=True)
    if status != expected_status:
        raise RuntimeError(f'HTTP {status}: {url} {result.stderr}')
    return dest.read_bytes()


def local_name(url):
    p = urlsplit(url)
    name = Path(p.path).name or 'font.css'
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    if '.css.php' in name:
        name = name.replace('.css.php', '.css')
    if p.netloc == 'fonts.googleapis.com':
        name = 'google-fonts.css'
    return 'assets/' + hashlib.sha256(url.encode()).hexdigest()[:10] + '-' + name


assets = {}


def asset(url, base):
    url = urljoin(base, url.strip())
    p = urlsplit(url)
    if p.scheme not in ['https', 'http']:
        return url
    fragment = p.fragment
    url = urlunsplit((p.scheme, p.netloc, p.path, p.query, ''))
    if url in assets:
        return assets[url] + ('#' + fragment if fragment else '')
    path = local_name(url)
    assets[url] = path
    data = get(url)
    if path.endswith('.css'):
        css = data.decode('utf-8-sig')
        def replace(m):
            ref = m.group(1)
            if ref.startswith(('data:', '#')):
                return m.group(0)
            target = asset(ref, url)
            return 'url("' + os.path.relpath(target, 'assets') + '")'
        css = CSS_URL.sub(replace, css)
        data = css.encode()
    elif path.endswith('.js'):
        js = data.decode('utf-8-sig')
        # The theme loads Maps on every page although none contains a map.
        js = js.replace('google.maps.event.addDomListener(window,"load",init);',
                        'if(document.getElementById("map")&&window.google)google.maps.event.addDomListener(window,"load",init);')
        # Navigation hrefs have already been resolved at export time.
        start = js.find('e(".navbar-nav li.one-page-link > a:first-child,')
        end = js.find('e(".navbar-collapse ul li a").click', start)
        if start != -1 and end != -1:
            js = js[:start] + js[end:]
        old = 'var n=e(this);e("html, body").stop().animate({scrollTop:e(n.attr("href")).offset().top-64},1500,"easeInOutExpo"),t.preventDefault()'
        new = 'var n=e(this),h=n.attr("href");if(h&&h.charAt(0)==="#"&&e(h).length){e("html, body").stop().animate({scrollTop:e(h).offset().top-64},1500,"easeInOutExpo");t.preventDefault()}'
        js = js.replace(old, new)
        data = js.encode()
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_bytes(data)
    manifest[url]['local'] = path
    save_manifest()
    return path + ('#' + fragment if fragment else '')


def relative(path, page):
    return os.path.relpath(path, str(Path(page).parent))


def page_link(href, page, origin):
    if href.startswith('#'):
        return href
    u = urlsplit(urljoin(origin, href))
    if u.netloc not in ['ezuno.com', 'www.ezuno.com']:
        return href
    path = u.path.strip('/')
    if path.startswith('home/'):
        # These are one-page-navigation targets in the original theme.
        return ('' if page == 'index.html' else relative('index.html', page)) + '#' + path.split('/')[1]
    if not path:
        target = 'index.html'
    elif path in PAGES:
        target = path + '/index.html'
    elif re.search(r'\.(png|jpg|jpeg|gif|svg|webp|pdf|properties)$', path, re.I):
        target = asset(urlunsplit((u.scheme, u.netloc, u.path, u.query, '')), origin)
    else:
        return href
    return relative(target, page) + ('#' + u.fragment if u.fragment else '')


def build_page(name):
    origin = ORIGIN if name == 'index' else ORIGIN + name + '/'
    page = 'index.html' if name == 'index' else name + '/index.html'
    soup = BeautifulSoup((CACHE / 'pages' / (name + '.html')).read_text(), 'lxml')
    for tag in list(soup.select('link')):
        if tag.attrs is None:
            continue
        rel = tag.get('rel', [])
        if 'stylesheet' in rel or 'icon' in rel:
            tag['href'] = relative(asset(tag['href'], origin), page)
        else:
            tag.decompose()
    for tag in list(soup.select('script')):
        if tag.attrs is None:
            continue
        src = tag.get('src', '')
        if ('maps.googleapis.com' in src or tag.get('type') == 'speculationrules'
                or tag.get('id') == 'wp-emoji-settings'
                or 'script#wp-emoji-settings' in tag.get_text()):
            tag.decompose()
        elif src:
            tag['src'] = relative(asset(src, origin), page)
        elif tag.string and 'ajax_url' in tag.string:
            # Cookie choices are stored entirely in the browser; no WP endpoint.
            tag.string = re.sub(r'var log_object = .*?;', 'var log_object = {};', tag.string)
    for tag in soup.find_all(True):
        if tag.name == 'iframe' and urlsplit(tag.get('src', '')).hostname == 'player.vimeo.com':
            # Modern browsers require the embedding page to delegate autoplay.
            # The theme starts this player only after the visitor clicks Play.
            tag['allow'] = 'autoplay; fullscreen; picture-in-picture'
        for attr in ['src', 'data-src', 'poster', 'data-bg', 'data-background']:
            if tag.has_attr(attr) and tag.name not in ['script', 'iframe']:
                val = tag[attr]
                if val and not val.startswith('data:'):
                    tag[attr] = relative(asset(val, origin), page)
        for attr in ['srcset', 'data-srcset']:
            if tag.has_attr(attr) and not tag[attr].startswith('data:'):
                refs = []
                for ref in tag[attr].split(','):
                    parts = ref.strip().split()
                    if parts:
                        refs.append(' '.join([relative(asset(parts[0], origin), page)] + parts[1:]))
                tag[attr] = ', '.join(refs)
        if tag.has_attr('style'):
            tag['style'] = CSS_URL.sub(lambda m: 'url("' + relative(asset(m.group(1), origin), page) + '")', tag['style'])
        if tag.name == 'a' and tag.has_attr('href'):
            tag['href'] = page_link(tag['href'], page, origin)
    # CSS and markup from the original are retained; this small adapter only
    # supplies browser storage on file:// and normalizes the theme's navigation.
    adapter = soup.new_tag('script', src=relative('assets/static.js', page))
    soup.head.insert(0, adapter)
    (ROOT / page).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / page).write_text(str(soup) + '\n')
    print('BUILT', page, flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--offline', action='store_true', help='rebuild using only the cache')
    args = ap.parse_args()
    offline = args.offline
    for name in PAGES:
        source = CACHE / 'pages' / (name + '.html')
        if not source.exists():
            url = ORIGIN if name == 'index' else ORIGIN + name + '/'
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(get(url, 404 if name in ['blog-page', 'terms-of-use'] else 200))
        build_page(name)
    (ROOT / '.nojekyll').touch()
    (ROOT / 'snapshot.json').write_text(json.dumps({
        'source': ORIGIN, 'captured': '2026-10-30',
        'pages': ['index.html' if p == 'index' else p + '/index.html' for p in PAGES],
        'assets': assets,
    }, indent=2) + '\n')
