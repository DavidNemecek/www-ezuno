"""Maintain the website's plain-text email templates and single destination.

The historical SQL is deliberately not a build input: it also contains private
WordPress data. Current templates are intentionally rewritten for email,
rather than exposing fragments of the old automated form notifications.
"""
from html import escape
import os
from pathlib import Path
import re
from urllib.parse import quote

from bs4 import BeautifulSoup


SHORTCODE = re.compile(r'\[contact-form-7\s+id=[^\d\]]*(319|323|4449)[^\]]*\]')
RECIPIENT = 'ezuno@ezuno.com'
MAIL_REQUESTS = {
    '319': {
        'kind': 'trial',
        'label': 'Request free license',
        'recipient': RECIPIENT,
        'subject': 'ezuno - Free BASIC license request',
        'body': '\r\n'.join([
            'Hello ezuno team,', '',
            'I would like to request a free BASIC license for up to 10 users.', '',
            'Name: [Your name]',
            'Company / organization (optional): [Your company]',
            'Email address for the license: [Your email address]', '',
            'Thank you.', '', 'Kind regards,', '[Your name]',
        ]),
    },
    '323': {
        'kind': 'contact',
        'label': 'Contact sales',
        'recipient': RECIPIENT,
        'subject': 'ezuno - Sales and pricing enquiry',
        'body': '\r\n'.join([
            'Hello ezuno team,', '',
            'I am interested in ezuno and would like to discuss the following request.', '',
            'Request: [Quote, purchase, evaluation or reseller enquiry]',
            'Number of users: [Required number of users]',
            'Current evaluation (optional): [Not started / FREE BASIC / other]',
            'Company / organization (optional): [Your company]', '',
            'My questions or requirements:', '[Please describe your request here.]', '',
            'Kind regards,', '[Your name]',
        ]),
    },
    '4449': {
        'kind': 'support',
        'label': 'Contact support',
        # Form 4449 is absent from the historical SQL. The owner explicitly
        # selected this destination on 2026-11-06. It is not a recovered
        # form-4449 configuration or historical field list.
        'recipient': RECIPIENT,
        'subject': 'ezuno - Support request',
        'body': '\r\n'.join([
            'Hello ezuno support team,', '',
            'I need help with the following issue.', '',
            'Problem:', '[What happens, and what did you expect?]', '',
            'Steps to reproduce:', '1. [First step]', '2. [Next step]', '',
            'ezuno version (if known): [Version]',
            'Alfresco version (if known): [Version]',
            'Operating system: [Windows / macOS / Linux and version]',
            'Error message (if any): [Exact error message]', '',
            'Kind regards,', '[Your name]',
        ]),
    },
}
FORM_IDS_BY_KIND = {spec['kind']: ident for ident, spec in MAIL_REQUESTS.items()}


def mailto_href(form_id):
    """Return an RFC 6068-style link with individually encoded query values."""
    spec = MAIL_REQUESTS[str(form_id)]
    return ('mailto:' + spec['recipient'] + '?subject=' +
            quote(spec['subject'], safe='') + '&body=' +
            quote(spec['body'], safe=''))


def form_html(form_id, page=None):
    """Retain the old exporter API, while producing only an email button."""
    spec = MAIL_REQUESTS[str(form_id)]
    return ('<div class="ezuno-mail-actions">'
            '<a class="ezuno-mail-button" data-ezuno-mail="' + spec['kind'] +
            '" href="' + escape(mailto_href(form_id), quote=True) + '">' +
            escape(spec['label']) + '</a></div>')


def replace_request_ctas(soup, page=None):
    """Keep templates at former forms; other CTAs navigate to those sections."""
    count = 0
    root = Path(__file__).resolve().parent.parent
    current = root / (page or 'index.html')
    for link in soup.find_all('a', href=True):
        label = link.get_text(' ', strip=True).casefold()
        ident = FORM_IDS_BY_KIND.get(link.get('data-ezuno-mail'))
        if link.find_parent(class_='ezuno-mail-actions'):
            if ident:
                link['href'] = mailto_href(ident)
                count += 1
            continue
        if label in ('get 10 users free', 'request free license'):
            ident = '319'
        elif label in ('get order form', 'get quote', 'contact sales'):
            ident = '323'
        if ident and '@' not in label:
            target = 'support/index.html' if ident == '4449' else 'index.html'
            href = os.path.relpath(root / target, current.parent).replace('\\', '/')
            if target == 'index.html':
                fragment = 'subscribe' if ident == '319' else 'contact'
                href = ('#' + fragment) if (current.name == 'index.html' and soup.find(id=fragment)) else href + '#' + fragment
            link['href'] = href
            link.attrs.pop('data-ezuno-mail', None)
            classes = [name for name in link.get('class', []) if name != 'ezuno-mail-button']
            if classes:
                link['class'] = classes
            else:
                link.attrs.pop('class', None)
    return count


def normalize_email_links(soup):
    """Only former forms have drafts; ordinary contact links remain plain."""
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href.lower().startswith('mailto:'):
            continue
        if link.find_parent(class_='ezuno-mail-actions'):
            ident = FORM_IDS_BY_KIND[link['data-ezuno-mail']]
            link['href'] = mailto_href(ident)
        else:
            link['href'] = 'mailto:' + RECIPIENT
            link.attrs.pop('data-ezuno-mail', None)
        if re.fullmatch(r'[^\s@]+@[^\s@]+', link.get_text(' ', strip=True)):
            link.clear()
            link.append(RECIPIENT)


def reconstruct_forms(soup, page=None):
    """Replace both original CF7 shortcodes and the previous static forms."""
    count = 0
    for form in list(soup.select('form[data-ezuno-form]')):
        ident = FORM_IDS_BY_KIND[form['data-ezuno-form']]
        fragment = BeautifulSoup(form_html(ident, page), 'html.parser')
        form.replace_with(fragment.div)
        count += 1
    for node in list(soup.find_all(string=SHORTCODE)):
        parts = SHORTCODE.split(str(node))
        node.parent['class'] = list(node.parent.get('class', [])) + ['ezuno-form-section']
        for index, part in enumerate(parts):
            if index % 2:
                fragment = BeautifulSoup(form_html(part, page), 'html.parser')
                node.insert_before(fragment.div)
                count += 1
            elif part.strip():
                node.insert_before(part)
        node.extract()
    replace_request_ctas(soup, page)
    normalize_email_links(soup)
    return count
