#!/usr/bin/env python3
"""Maintain the reviewed static pages without importing WordPress assets.

The HTML documents are the maintained sources. This command is idempotent and
needs neither a WordPress server nor the private historical database backup.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup, Comment

from static_forms import reconstruct_forms

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / 'snapshot.json'
CSS_URL = re.compile(r'url\(\s*[\'"]?([^\s\)\'\"]+)', re.I)
INSTALLER_PATH = 'releases/ezuno-5.10.19-Installation-Package.zip'
EXTERNAL_REPLACEMENTS = {
    'http://www.faw.at': 'https://www.faw.at/',
    'http://www.faw.at/impressum/': 'https://www.faw.at/impressum/',
    'http://www.signa.at/en/': 'https://signa.at/',
    'http://ec.europa.eu': 'https://ec.europa.eu/',
    'http://www.apple.com': 'https://www.apple.com/',
    'http://www.microsoft.com': 'https://www.microsoft.com/',
    'http://www.alfresco.com': 'https://www.hyland.com/en/solutions/products/alfresco-platform',
    'https://www.alfresco.com': 'https://www.hyland.com/en/solutions/products/alfresco-platform',
    'http://dnr.alaska.gov/': 'https://dnr.alaska.gov/',
    'http://polypoint.ch/': 'https://www.polypoint.ch/de-ch/',
    'http://www.affiris.com/': 'https://affiris.com/',
    'http://www.rechnungshof.gv.at': 'https://www.rechnungshof.gv.at/',
    'https://twitter.com/easyuno': 'https://x.com/easyuno',
    'https://docs.alfresco.com/content-services/latest/install/zip/amp/':
        'https://docs.hyland.com/r/Alfresco/Alfresco-Content-Services/23.3/'
        'Alfresco-Content-Services/Install/Install-with-zip/Install-Alfresco-Module-Package',
    'https://docs.alfresco.com/content-services/latest/develop/share-ext-points/'
        'surf-extension-modules/#moduledeployandevaluators':
        'https://docs.hyland.com/r/Alfresco/Alfresco-Content-Services/23.3/'
        'Alfresco-Content-Services/Develop/Share-UI-Extension-Points/Surf-Extension-Modules',
    'https://docs.alfresco.com/content-services/latest/admin/auth-sync/':
        'https://docs.hyland.com/r/Alfresco/Alfresco-Content-Services-Community-Edition/23.3/'
        'Alfresco-Content-Services-Community-Edition/Administer/Manage-Security/Authentication-and-sync',
}


def repair_content_links(soup, page):
    for link in list(soup.find_all('a', href=True)):
        original = link['href']
        parsed = urlsplit(original)
        label = link.get_text(' ', strip=True)
        if parsed.hostname == 'support.ezuno.com':
            link['href'] = relative('support/index.html', page)
            if label.startswith('http'):
                link.string = 'Support'
        elif parsed.path.endswith('ezuno-5.10.19-Installation-Package.zip'):
            link['href'] = relative(INSTALLER_PATH, page)
            link['download'] = 'ezuno-5.10.19-Installation-Package.zip'
            link['data-ezuno-download'] = ''
            link.attrs.pop('target', None)
        elif original in EXTERNAL_REPLACEMENTS:
            link['href'] = EXTERNAL_REPLACEMENTS[original]
            if label == original:
                link.string = link['href']
            if 'moduledeployandevaluators' in original:
                link.string = 'Surf extension modules (Alfresco Documentation)'
        elif parsed.path.endswith('terms-of-use/index.html') and not parsed.path.endswith('our-terms-of-use/index.html'):
            link['href'] = relative('our-terms-of-use/index.html', page)
        elif parsed.path.endswith('blog-page/index.html') and label.casefold() == 'blog':
            parent = link.parent
            if parent.name == 'p' and parent.get_text(' ', strip=True) == label:
                parent.decompose()
            else:
                link.decompose()
            continue
        elif original == '#' and link.find('img'):
            link['href'] = relative('index.html', page)
        if link.get('target'):
            link['target'] = link['target'].strip()
            if link['target'] == '_blank':
                link['rel'] = sorted(set(link.get('rel', [])) | {'noopener', 'noreferrer'})
        if not link.get_text(' ', strip=True) and not link.get('aria-label'):
            image = link.find('img')
            if image and 'ezuno-' in image.get('src', ''):
                link['aria-label'] = 'ezuno home'
            elif link.select_one('.fa-twitter'):
                link['aria-label'] = 'ezuno on X'
            elif link.select_one('.fa-facebook'):
                link['aria-label'] = 'ezuno on Facebook'

def relative(target, page):
    return os.path.relpath(ROOT / target, (ROOT / page).parent).replace('\\', '/')


def modernize_page(page):
    path = ROOT / page
    source = ROOT / 'our-terms-of-use/index.html' if page == 'terms-of-use/index.html' else path
    soup = BeautifulSoup(source.read_text(encoding='utf-8'), 'html.parser')
    if page == 'blog-page/index.html' and soup.select_one('.page-404'):
        soup.title.string = 'Product information - ezuno.com'
        heading = soup.select_one('#header .section-heading')
        if heading:
            heading.string = 'Product information'
        old = soup.select_one('.page-404')
        content = BeautifulSoup('''<section id="single-page" class="section product-information">
          <div class="container"><div class="row single-page-content">
            <h2>Explore ezuno</h2>
            <p>Find product features, installation instructions and support for ezuno.</p>
            <p><a class="primary-button" href="../index.html#features">Explore features</a></p>
            <p><a href="../download/index.html">Download and installation</a></p>
            <p><a href="../support/index.html">Support and frequently asked questions</a></p>
          </div></div></section>''', 'html.parser')
        old.replace_with(content.section)
        soup.body['class'] = [c for c in soup.body.get('class', []) if c != 'error404']
    repair_content_links(soup, page)
    reconstruct_forms(soup, page)
    soup.html['lang'] = 'en'
    for tag in list(soup.find_all(['script', 'style', 'noscript'])):
        tag.decompose()
    for tag in list(soup.find_all('link')):
        if 'icon' not in tag.get('rel', []):
            tag.decompose()
    for tag in list(soup.select('meta[name="generator"]')):
        tag.decompose()
    for node in list(soup.find_all(string=lambda text: isinstance(text, Comment))):
        node.extract()
    soup.head.insert(0, Comment(
        ' HTML structure adapted from KeySoft by Key-Design; modified 2026-11-06. '
        'The adapted HTML template structure, including our modifications to it, '
        'is licensed under the GNU General Public License, version 3 (GPL-3.0-only); see ' +
        relative('licenses/KeySoft-GPL-3.0.txt', page) +
        '. Company text/media and the new independent CSS/JS are separate works; see ' +
        relative('licenses/README.md', page) + '. '))
    if page in ('terms-of-use/index.html', 'our-terms-of-use/index.html'):
        apply_third_party_license_exception(soup, page)
    for selector in ['#preloader', '#cookie-law-info-bar', '#cookie-law-info-again',
                     '#cliSettingsPopup', '.cli-modal-backdrop']:
        for tag in list(soup.select(selector)):
            tag.decompose()
    for tag in list(soup.select('.cli_settings_button, .cli_settings_button_new')):
        tag.decompose()
    for tag in soup.find_all(True):
        if tag.has_attr('style'):
            if tag.get('id') == 'header' and '16091c1d06' in tag['style']:
                tag['class'] = list(dict.fromkeys(tag.get('class', []) + ['ezuno-eula-header']))
            del tag['style']
        for attr in list(tag.attrs):
            if attr.lower().startswith('on'):
                del tag[attr]
        if tag.name == 'img':
            if tag.get('data-src') and (not tag.get('src') or tag['src'].startswith('data:')):
                tag['src'] = tag['data-src']
            if tag.get('data-srcset'):
                tag['srcset'] = tag['data-srcset']
            for attr in ['data-src', 'data-srcset', 'data-sizes']:
                tag.attrs.pop(attr, None)
            tag['class'] = [c for c in tag.get('class', []) if c not in ['lazyload', 'lazyloaded']]
            tag['decoding'] = 'async'
        if tag.name == 'iframe':
            tag.decompose()
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        viewport['content'] = 'width=device-width, initial-scale=1'
    for trigger in soup.select('[data-target="#video-modal"]'):
        trigger['href'] = 'https://vimeo.com/99855952'
        trigger['aria-label'] = 'Play ezuno video on Vimeo'
    # The standalone Features page retains a video CTA from the one-page
    # layout; its target lives on the homepage rather than in that document.
    for link in soup.select('a[href="#our-video"]'):
        if not soup.find(id='our-video'):
            link['href'] = relative('index.html', page) + '#our-video'
    for modal in soup.select('#video-modal'):
        modal['hidden'] = ''
    for section in soup.select('#our-video, #single-page.our-video'):
        if not section.select_one('.ezuno-video-notice'):
            note = soup.new_tag('p', attrs={'class': 'ezuno-video-notice'})
            note.string = 'Playing the video connects to Vimeo. Vimeo may use cookies and process usage data.'
            section.append(note)
    menu_button = soup.select_one('.navbar-toggle')
    if menu_button:
        menu_button['aria-label'] = 'Toggle navigation'
        menu_button['aria-controls'] = 'main-menu'
        menu_button['aria-expanded'] = 'false'
    css = soup.new_tag('link', rel='stylesheet', href=relative('assets/site.css', page))
    soup.head.append(css)
    script = soup.new_tag('script', src=relative('assets/site.js', page))
    script['defer'] = ''
    soup.head.append(script)
    path.write_text(str(soup).rstrip() + '\n', encoding='utf-8')


def apply_third_party_license_exception(soup, page):
    """Keep the proprietary-content terms separate from GPL/OFL permissions."""
    heading = next((tag for tag in soup.find_all(['h2', 'h3', 'h4'])
                    if tag.get_text(' ', strip=True) == 'Copyrights'), None)
    if heading is None:
        raise ValueError(f'{page}: missing Copyrights section')
    notice = soup.find(id='third-party-licenses')
    if notice is None:
        notice = soup.new_tag('p', id='third-party-licenses')
    notice.clear()
    notice.append(
        'The restrictions in this Copyrights section apply only to Materials '
        'that are not governed by a separate license. Third-party and open-source '
        'components, including the adapted GPL-licensed HTML template structure '
        'and the OFL-licensed fonts, are governed by their respective licenses. '
        'Those licenses take precedence over these Terms for the relevant '
        'components. Nothing in these Terms restricts rights granted under '
        'those licenses. See the ')
    link = soup.new_tag('a', href=relative('licenses/README.md', page))
    link.string = 'licensing notices and component licenses'
    notice.append(link)
    notice.append('.')
    heading.insert_after(notice)
    # Updating this section is a new version of the public Terms.
    for paragraph in soup.find_all('p'):
        if paragraph.get_text(' ', strip=True).startswith('Last updated:'):
            paragraph.string = 'Last updated: November 6th, 2026 (Version 1.2)'
            break


def referenced_assets(pages):
    """Find the transitive local asset set in pages and original source CSS."""
    found = set()

    def add(value, source):
        value = value.strip()
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return
        target = (source.parent / unquote(parsed.path)).resolve()
        if target.is_relative_to((ROOT / 'assets').resolve()):
            if not target.is_file():
                raise FileNotFoundError(target)
            found.add(target)

    for page in pages:
        path = ROOT / page
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        for tag in soup.find_all(True):
            for attr in ['href', 'src', 'poster']:
                if tag.get(attr):
                    add(tag[attr], path)
            if tag.get('srcset') and not tag['srcset'].startswith('data:'):
                for item in tag['srcset'].split(','):
                    add(item.strip().split()[0], path)
    for css in [ROOT / 'assets/site.css']:
        for value in CSS_URL.findall(css.read_text(encoding='utf-8')):
            add(value, css)
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prune', action='store_true', help='remove unused files from assets/')
    parser.add_argument('--offline', action='store_true', help='compatibility option; always works offline')
    args = parser.parse_args()
    manifest = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    for page in manifest['pages']:
        modernize_page(page)
    if args.prune:
        for required in ['assets/site.css', 'assets/site.js']:
            if not (ROOT / required).is_file():
                raise FileNotFoundError('Original replacement asset not ready: ' + required)
        used = referenced_assets(manifest['pages'])
        asset_root = (ROOT / 'assets').resolve()
        removed = []
        # Only individual, verified files inside this project's assets directory.
        for path in sorted(asset_root.iterdir()):
            if path.is_file() and path.resolve().is_relative_to(asset_root) and path.resolve() not in used:
                removed.append(path.name)
                path.unlink()
        manifest['assets'] = {url: dest for url, dest in manifest['assets'].items()
                              if (ROOT / dest).is_file()}
        manifest['maintained'] = '2026-11-06'
        manifest['runtime'] = ['assets/site.css', 'assets/site.js']
        manifest['asset_sha256'] = {str(path.relative_to(ROOT)).replace('\\', '/'):
                                   hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in sorted(used)}
        SNAPSHOT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Removed {len(removed)} obsolete assets; retained {len(used)} referenced assets.')
    print(f'Normalized {len(manifest["pages"])} static pages; no WordPress downloads or database access.')


if __name__ == '__main__':
    main()
