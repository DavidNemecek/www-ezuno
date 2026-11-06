#!/usr/bin/env python3
"""Exercise the maintained static site in Edge without contacting third parties."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
from zipfile import ZipFile

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from static_forms import FORM_IDS_BY_KIND, MAIL_REQUESTS, mailto_href

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / '.mirror/rebuild/review-runtime.json'
PAGES = json.loads((ROOT / 'snapshot.json').read_text(encoding='utf-8'))['pages']
EDGE = Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')


class Handler(SimpleHTTPRequestHandler):
    download_fixture = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        if path.startswith('/project/'):
            path = path[len('/project'):]
        return super().translate_path(path)

    def log_message(self, *args):
        pass

    def do_GET(self):
        fixture = Handler.download_fixture
        if fixture and urlsplit(self.path).path.endswith('/releases/' + fixture['name']):
            # Native Chromium downloads bypass Playwright page routing. Mock at
            # the HTTP boundary so no part of the real installer is transferred.
            fixture['requests'].append(time.monotonic())
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', 'attachment; filename="' + fixture['name'] + '"')
            self.send_header('Content-Length', str(len(fixture['body'])))
            self.end_headers()
            self.wfile.write(fixture['body'])
            return
        super().do_GET()


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('--download-only', action='store_true', help='Run the native download cooldown checks without the full page matrix.')
    options = arguments.parse_args()
    results = []

    def check(name, callback):
        if name.startswith(('interactions:', 'download-click-guard:')):
            print('RUN:', name, flush=True)
        try:
            detail = callback()
            results.append({'name': name, 'passed': True, 'detail': detail})
        except Exception as error:
            results.append({'name': name, 'passed': False, 'detail': str(error)})
            print('FAIL:', name, str(error), flush=True)

    def require(value, message):
        if not value:
            raise AssertionError(message)

    def reviewed_templates():
        expected_kinds = {'trial', 'contact', 'support'}
        require(expected_kinds.issubset(FORM_IDS_BY_KIND), 'Missing one of the three original form purposes')
        required_content = {
            'trial': ['free BASIC', '10 users', 'Email address for the license'],
            'contact': ['Number of users', 'questions or requirements'],
            'support': ['Problem:', 'Steps to reproduce', 'Operating system'],
        }
        subjects = set()
        coverage = {kind: 0 for kind in expected_kinds}
        for kind in expected_kinds:
            ident = FORM_IDS_BY_KIND[kind]
            spec = MAIL_REQUESTS[ident]
            require(spec['recipient'] == 'ezuno@ezuno.com', 'Draft does not use owner-selected inbox')
            subjects.add(spec['subject'])
            require('\r' not in spec['subject'] and '\n' not in spec['subject'], 'Email subject contains a header separator')
            require(spec['body'].startswith('Hello ezuno'), f'Missing greeting: {spec["kind"]}')
            require(len(spec['body']) > 80 and '[Your name]' in spec['body'], f'Unhelpful draft: {spec["kind"]}')
            require(not re.search(r'(?<!\r)\n|\r(?!\n)', spec['body']), f'Non-CRLF line endings: {spec["kind"]}')
            require(all(fragment.casefold() in spec['body'].casefold() for fragment in required_content[spec['kind']]), f'Draft purpose unclear: {spec["kind"]}')
            require(set(parse_qs(urlsplit(mailto_href(ident)).query)) == {'subject', 'body'}, 'Unexpected mail headers')
        require(len(subjects) == 3, 'Request purposes must have distinct subjects')
        form_positions = {}
        for path in PAGES:
            document = BeautifulSoup((ROOT / path).read_text(encoding='utf-8'), 'html.parser')
            for link in document.select('a[href^="mailto:"]'):
                kind = link.get('data-ezuno-mail')
                require(urlsplit(link['href']).path == 'ezuno@ezuno.com', f'{path}: unexpected destination')
                require(bool(link.get_text(' ', strip=True) or link.get('aria-label')), f'{path}: email link has no accessible name')
                if link.find_parent(class_='ezuno-mail-actions'):
                    require(kind in expected_kinds, f'{path}: unclassified original form replacement')
                    require(link['href'] == mailto_href(FORM_IDS_BY_KIND[kind]), f'{path}: outdated or malformed {kind} draft')
                    coverage[kind] += 1
                    form_positions[path] = form_positions.get(path, 0) + 1
                else:
                    require(link['href'] == 'mailto:ezuno@ezuno.com' and not kind, f'{path}: ordinary email link contains a form draft')
        require(coverage == {'trial': 3, 'contact': 3, 'support': 1}, f'Expected exactly seven original form replacements: {coverage}')
        require(form_positions == {'index.html': 2, 'support/index.html': 1, 'home/index.html': 2, 'home/contact/index.html': 1, 'home/subscribe/index.html': 1}, f'Email drafts moved outside original form locations: {form_positions}')
        return coverage

    check('seven-original-form-buttons-three-reviewed-mail-templates', reviewed_templates)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_port
    bases = {
        'http': f'http://127.0.0.1:{port}/',
        'prefix': f'http://127.0.0.1:{port}/project/',
        'file': ROOT.as_uri() + '/',
    }
    with sync_playwright() as engine:
        browser_options = {'headless': True}
        configured_browser = os.environ.get('EZUNO_BROWSER')
        if configured_browser:
            browser_options['executable_path'] = configured_browser
        elif EDGE.exists():
            browser_options['executable_path'] = str(EDGE)
        browser = engine.chromium.launch(**browser_options)
        for width in [1440, 390]:
            for transport, base in bases.items():
                if options.download_only and (transport, width) not in [('http', 1440), ('prefix', 390)]:
                    continue
                context = browser.new_context(viewport={'width': width, 'height': 900 if width == 1440 else 844}, reduced_motion='reduce')
                context.route('https://**/*', lambda route: route.fulfill(status=200, content_type='text/html', body='<html><body>External video test frame</body></html>'))
                context.route('http://**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname in ['127.0.0.1', 'localhost'] else route.abort())
                page = context.new_page()
                external = []
                errors = []
                failed = []
                page.on('request', lambda request: external.append(request.url) if urlsplit(request.url).scheme in ['http', 'https'] and urlsplit(request.url).hostname not in ['127.0.0.1', 'localhost'] else None)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('response', lambda response: failed.append(response.url) if response.status >= 400 else None)

                for path in ([] if options.download_only else PAGES):
                    external.clear()
                    errors.clear()
                    failed.clear()

                    def inspect(path=path):
                        page.goto(base + path, wait_until='load')
                        page.evaluate('document.fonts.ready')
                        require(not errors, f'JavaScript errors: {errors}')
                        require(not failed, f'HTTP failures: {failed}')
                        require(not external, f'Initial external requests: {external}')
                        require(not re.search(r'\b404\b|not found|nicht gefunden', page.title(), re.I), 'Copied error-page title remains')
                        require(page.locator('form,input,textarea,select').count() == 0, 'Form controls remain')
                        require(page.locator('script[src]').count() == 1 and page.locator('script[src]').get_attribute('src').endswith('assets/site.js'), 'Unexpected script dependency')
                        require(page.locator('html').get_attribute('lang') == 'en', 'Incorrect content language')
                        require(page.locator('html').evaluate('(node)=>node.scrollWidth') <= width + 1, 'Horizontal page overflow')
                        require(page.locator('body').inner_text().strip(), 'No visible content')
                        image_details = page.evaluate('''async () => {
                          const images = Array.from(document.images);
                          images.forEach(image => { image.loading = 'eager'; });
                          return Promise.all(images.map(async image => {
                            let error = null;
                            try { await image.decode(); } catch (failure) { error = String(failure); }
                            return {src: image.currentSrc || image.src, width: image.naturalWidth,
                              height: image.naturalHeight, complete: image.complete, error};
                          }));
                        }''')
                        require(all(image['complete'] and image['width'] > 0 and image['height'] > 0 and not image['error'] for image in image_details), f'Broken image: {[image for image in image_details if not image["width"] or image["error"]]}')
                        require(not errors and not failed and not external, f'Resource errors after image decode: {errors + failed + external}')
                        for link in page.locator('a[href^="mailto:"]').evaluate_all('(nodes)=>nodes.map(node=>({href:node.getAttribute("href"),kind:node.dataset.ezunoMail}))'):
                            href = link['href']
                            require(urlsplit(href).path == 'ezuno@ezuno.com', 'Email does not use the selected shared inbox')
                            if not link.get('kind'):
                                require(href == 'mailto:ezuno@ezuno.com', 'Ordinary email link contains an unwanted draft')
                                continue
                            query = parse_qs(urlsplit(href).query)
                            require(link['kind'] in ['trial', 'contact', 'support'], 'Unexpected published email draft purpose')
                            ident = FORM_IDS_BY_KIND[link['kind']]
                            require(href == mailto_href(ident), f'Mail link differs from reviewed template: {link["kind"]}')
                            require(urlsplit(href).path == MAIL_REQUESTS[ident]['recipient'], f'Unexpected recipient: {href}')
                            require(urlsplit(href).path == 'ezuno@ezuno.com', 'Email does not use the selected shared inbox')
                            require(bool(query.get('subject')) and bool(query.get('body')), 'Missing mail draft')
                            require(not re.search(r'\[(?:your-|email-|_site|text-)', query['body'][0]), 'Unresolved mail template token')
                        for href in page.locator('footer a[href], #upper-footer a[href]').evaluate_all('(nodes)=>nodes.map(node=>node.getAttribute("href"))'):
                            parsed = urlsplit(href)
                            if parsed.scheme or parsed.netloc or not parsed.path:
                                continue
                            target = (ROOT / path).parent / parsed.path
                            require(target.exists(), f'Missing footer target: {href}')
                        if width == 390:
                            require(not page.locator('#main-menu').is_visible(), 'Mobile navigation expanded initially')
                            page.locator('.navbar-toggle').click()
                            require(page.locator('#main-menu').is_visible(), 'Mobile menu does not open')
                            page.keyboard.press('Escape')
                            require(not page.locator('#main-menu').is_visible(), 'Escape does not close mobile menu')
                        return {'mail_links': page.locator('a[href^="mailto:"]').count(), 'images_decoded': len(image_details)}

                    check(f'{transport}:{width}:{path}', inspect)

                def interactions():
                    page.goto(base + 'index.html', wait_until='load')
                    tabs = page.locator('[role="tab"]')
                    require(tabs.count() == 4, 'Expected four feature tabs')
                    for index in range(4):
                        tabs.nth(index).click()
                        require(tabs.nth(index).get_attribute('aria-selected') == 'true', 'Tab selection failed')
                        require(page.locator('[role="tabpanel"]:visible').count() == 1, 'Incorrect number of visible tab panels')
                    tabs.nth(3).press('Home')
                    require(tabs.nth(0).get_attribute('aria-selected') == 'true', 'Home key failed')
                    tabs.nth(0).press('ArrowLeft')
                    require(tabs.nth(3).get_attribute('aria-selected') == 'true', 'Arrow navigation failed')
                    page.locator('.ezuno-carousel-next').click()
                    require(page.locator('.ezuno-carousel-status').inner_text() == '2 / 3', 'Testimonial next failed')
                    page.locator('.ezuno-carousel-prev').click()
                    require(page.locator('.ezuno-carousel-status').inner_text() == '1 / 3', 'Testimonial previous failed')
                    opener = page.locator('[data-target="#video-modal"]').first
                    opener.click()
                    frame = page.locator('#video-modal iframe')
                    require(frame.count() == 1, 'Video iframe not created')
                    require(frame.get_attribute('allow') == 'autoplay; fullscreen; picture-in-picture', 'Video permissions missing')
                    close = page.locator('.ezuno-video-close')
                    require(close.evaluate('(node)=>document.activeElement===node'), 'Video close not focused')
                    page.keyboard.press('Shift+Tab')
                    require(frame.evaluate('(node)=>document.activeElement===node'), 'Video backwards focus trap failed')
                    for unused in range(5):
                        page.keyboard.press('Tab')
                        page.wait_for_timeout(50)
                        require(page.evaluate('!document.hasFocus() || document.getElementById("video-modal").contains(document.activeElement)'), 'Video focus escaped to background page')
                    close.focus()
                    page.locator('.navbar-toggle').evaluate('(node)=>node.focus()')
                    require(close.evaluate('(node)=>document.activeElement===node'), 'Background page accepts focus while video is open')
                    page.keyboard.press('Escape')
                    require(frame.count() == 0, 'Video keeps playing after close')
                    require(opener.evaluate('(node)=>document.activeElement===node'), 'Video opener focus not restored')
                    page.goto(base + 'support/index.html', wait_until='load')
                    faq = page.locator('.vc_tta-panel-heading a')
                    for index in range(faq.count()):
                        faq.nth(index).click()
                        require(faq.nth(index).get_attribute('aria-expanded') == 'true', 'FAQ click failed')
                        require(page.locator('html').evaluate('(node)=>node.scrollWidth') <= width + 1, 'Expanded FAQ causes horizontal page overflow')
                        faq.nth(index).press(' ')
                        require(faq.nth(index).get_attribute('aria-expanded') == 'false', 'FAQ Space failed')
                    if width == 390:
                        page.locator('.navbar-toggle').click()
                    page.locator('#main-menu a').first.click()
                    page.wait_for_load_state('load')
                    require(urlsplit(page.url).fragment == 'modern-tools', 'Cross-page section link lost hash')
                    require(page.url.startswith(base), 'Cross-page link escaped site prefix')
                    page.wait_for_function('''() => {
                      const top = document.getElementById('modern-tools').getBoundingClientRect().top;
                      const header = document.querySelector('.navbar').getBoundingClientRect().height;
                      return top >= header && top < header + 60;
                    }''')
                    return 'Tabs, keyboard, testimonials, FAQ, Vimeo modal/focus and cross-page navigation passed.'

                if not options.download_only:
                    check(f'interactions:{transport}:{width}', interactions)
                if (transport, width) in [('http', 1440), ('prefix', 390)]:
                    def download_click_guard():
                        # Keep the native browser download path while substituting
                        # a tiny valid ZIP: the real installer is never transferred.
                        archive = io.BytesIO()
                        with ZipFile(archive, 'w') as package:
                            package.writestr('download-test.txt', 'Runtime verification only.\n')
                        name = 'ezuno-5.10.19-Installation-Package.zip'
                        requests = []
                        downloads = []
                        Handler.download_fixture = {'name': name, 'body': archive.getvalue(), 'requests': requests}
                        page.on('download', lambda download: downloads.append(download))
                        page.goto(base + 'download/index.html', wait_until='load')
                        page.evaluate('document.fonts.ready')
                        button = page.locator('a[data-ezuno-download]')
                        require(button.count() == 1, 'Expected one guarded installer link')
                        original_label = button.text_content()
                        require(button.get_attribute('aria-disabled') is None, 'Download starts disabled')
                        button.scroll_into_view_if_needed()
                        box = button.bounding_box()
                        started = time.monotonic()
                        with page.expect_download(timeout=3000) as first:
                            page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                        require(first.value.suggested_filename == name, 'Native download filename changed')
                        require(len(requests) == 1 and len(downloads) == 1, 'First click did not start exactly one native download')
                        immediate_seconds = requests[0] - started
                        require(immediate_seconds < 2, f'First click delayed the download by {immediate_seconds:.2f}s')
                        require(button.get_attribute('aria-disabled') == 'true', 'Download link does not become disabled')
                        require(button.text_content() == 'Der Download wird gleich gestartet', 'Incorrect busy label')
                        require(button.get_attribute('aria-live') == 'polite', 'Busy status is not announced')
                        require(button.evaluate('(node)=>getComputedStyle(node).textTransform') == 'none', 'Busy label casing is visually altered')
                        require(page.locator('html').evaluate('(node)=>node.scrollWidth') <= width + 1, 'Busy download label causes page overflow')
                        require(button.evaluate('(node)=>node.scrollWidth <= node.clientWidth + 1'), 'Busy label overflows its button')
                        busy_box = button.bounding_box()
                        require(busy_box['x'] >= 0 and busy_box['x'] + busy_box['width'] <= width + 1, 'Busy button extends outside viewport')
                        point = (busy_box['x'] + busy_box['width'] / 2, busy_box['y'] + busy_box['height'] / 2)
                        # locator.click intentionally waits for aria-disabled;
                        # genuine pointer events exercise repeated user clicks.
                        for unused in range(10):
                            page.mouse.click(*point)
                        button.evaluate('(node)=>node.click()')
                        require(len(requests) == 1 and len(downloads) == 1, 'Repeated pointer/programmatic activation started duplicate downloads')
                        busy_screenshot = REPORT.parent / f'download-busy-{width}.png'
                        busy_screenshot.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(busy_screenshot), full_page=False)
                        remaining = started + 14 - time.monotonic()
                        if remaining > 0:
                            page.wait_for_timeout(remaining * 1000)
                        require(button.get_attribute('aria-disabled') == 'true', 'Download unlocked before the requested 15 seconds')
                        require(len(requests) == 1 and len(downloads) == 1, 'A blocked activation triggered a delayed download')
                        page.wait_for_function('''() => !document.querySelector('a[data-ezuno-download]').hasAttribute('aria-disabled')''', timeout=4000)
                        unlocked_seconds = time.monotonic() - started
                        require(unlocked_seconds >= 14.9, f'Download unlocked early after {unlocked_seconds:.2f}s')
                        require(button.text_content() == original_label, 'Original download label was not restored')
                        box = button.bounding_box()
                        with page.expect_download(timeout=3000) as second:
                            page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                        require(second.value.suggested_filename == name and len(requests) == 2 and len(downloads) == 2, 'Download did not work again after unlocking')
                        return {'native_downloads': len(downloads), 'blocked_activations': 11,
                                'first_request_seconds': round(immediate_seconds, 3),
                                'unlock_seconds': round(unlocked_seconds, 3),
                                'mock_zip_bytes': len(archive.getvalue()),
                                'busy_screenshot': str(busy_screenshot.relative_to(ROOT))}

                    check(f'download-click-guard:{transport}:{width}', download_click_guard)
                    Handler.download_fixture = None
                if transport == 'http' and not options.download_only:
                    for label, path in {
                        'hero': 'index.html',
                        'support': 'support/index.html',
                        'contact': 'home/contact/index.html',
                        'subscribe': 'home/subscribe/index.html',
                        'download': 'download/index.html',
                    }.items():
                        def screenshot(label=label, path=path):
                            page.goto(base + path, wait_until='load')
                            page.evaluate('document.fonts.ready')
                            dest = REPORT.parent / f'{label}-{width}.png'
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            page.screenshot(path=str(dest), full_page=label != 'hero')
                            return str(dest.relative_to(ROOT))
                        check(f'screenshot:{label}:{width}', screenshot)
                context.close()

        for width in ([] if options.download_only else [1440, 390]):
            context = browser.new_context(viewport={'width': width, 'height': 844}, java_script_enabled=False)
            context.route('https://**/*', lambda route: route.abort())
            page = context.new_page()
            for path in PAGES:
                def no_js(path=path):
                    page.goto(bases['http'] + path, wait_until='load')
                    page.evaluate('document.fonts.ready')
                    require(page.locator('form,input,textarea,select').count() == 0, 'No-JS form fields remain')
                    require(page.locator('#main-menu').is_visible(), 'No-JS navigation inaccessible')
                    require(page.locator('.navbar-toggle').is_hidden(), 'Nonfunctional no-JS menu button visible')
                    require(page.locator('#video-modal').count() == 0 or page.locator('#video-modal').is_hidden(), 'No-JS video overlay visible')
                    require(page.locator('html').evaluate('(node)=>node.scrollWidth') <= width + 1, 'No-JS horizontal overflow')
                    for selector in ['.features-tabs > div[id]', '.vc_tta-panel-body', '.tt-content']:
                        for node in page.locator(selector).all():
                            require(node.is_visible(), f'No-JS content hidden: {selector}')
                    return 'No-JS navigation, content and mail links available.'
                check(f'nojs:{width}:{path}', no_js)
            context.close()
        browser.close()
    def assembled_installer():
        expected_name = 'ezuno-5.10.19-Installation-Package.zip'
        expected_file = (ROOT / 'releases' / expected_name).resolve()
        checksum_file = expected_file.with_suffix(expected_file.suffix + '.sha256')
        require(expected_file.is_file(), 'Assembled installer is missing; run the documented site build first')
        require(checksum_file.is_file(), 'Installer SHA-256 sidecar is missing')
        digest = hashlib.sha256()
        with expected_file.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        require(digest.hexdigest() == checksum_file.read_text(encoding='utf-8').split()[0], 'Installer differs from its published checksum')
        size = expected_file.stat().st_size
        require(size > 100_000_000, 'Installer appears truncated')
        links = []
        for path in PAGES:
            document = BeautifulSoup((ROOT / path).read_text(encoding='utf-8'), 'html.parser')
            for link in document.select('a[href]'):
                parsed = urlsplit(link['href'])
                if not parsed.path.endswith('.zip'):
                    continue
                require(not parsed.scheme and not parsed.netloc and not parsed.path.startswith('/'), 'Installer link must be relative to the static site')
                target = ((ROOT / path).parent / unquote(parsed.path)).resolve()
                require(target == expected_file, f'Unexpected installer destination: {link["href"]}')
                require(link.get('download') == expected_name, 'Installer lacks a stable download filename')
                for transport in ['http', 'prefix']:
                    url = urljoin(bases[transport] + path, link['href'])
                    with urlopen(Request(url, method='HEAD'), timeout=15) as response:
                        require(response.status == 200, f'Installer not served over {transport}')
                        require(int(response.headers.get('Content-Length', 0)) == size, f'Installer length differs over {transport}')
                links.append({'page': path, 'href': link['href']})
        require(bool(links), 'No installer download link exists')
        return {'links': links, 'bytes': size, 'sha256': digest.hexdigest(), 'http_validation': 'HEAD only; no installer transfer'}

    if not options.download_only:
        check('assembled-installer-relative-link-checksum-and-head', assembled_installer)
    server.shutdown()
    def static_links():
        outcome = subprocess.run([sys.executable, str(ROOT / 'tools/check_links.py')], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        require(outcome.returncode == 0, outcome.stdout + outcome.stderr)
        return outcome.stdout.strip()

    if not options.download_only:
        check('all-local-resources-anchors-and-mail-links', static_links)
    summary = {'checks': len(results), 'passed': sum(result['passed'] for result in results), 'failed': sum(not result['passed'] for result in results), 'results': results}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report_path = REPORT.with_name('review-download-guard.json') if options.download_only else REPORT
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({key: summary[key] for key in ['checks', 'passed', 'failed']}), flush=True)
    raise SystemExit(1 if summary['failed'] else 0)


if __name__ == '__main__':
    main()
