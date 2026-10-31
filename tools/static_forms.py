"""Reconstruct the three unavailable Contact Form 7 forms as static HTML."""
from html import escape
import os
import re
from bs4 import BeautifulSoup

SHORTCODE = re.compile(r'\[contact-form-7\s+id=[^\d\]]*(319|323|4449)[^\]]*\]')
FORMS = {
    '319': ('trial', 'Free 10-user license request', 'Request free license'),
    '323': ('contact', 'Contact / quote request', 'Prepare contact email'),
    '4449': ('support', 'Support request', 'Prepare support email'),
}


def form_html(form_id, page):
    kind, title, button = FORMS[form_id]
    prefix = 'ezuno-' + kind
    fields = []

    def field(name, label, *, required=False, field_type='text', autocomplete=None,
              full=False, options=None):
        ident = prefix + '-' + name
        attrs = f'id="{ident}" name="{name}"'
        if required:
            attrs += ' required'
        if autocomplete:
            attrs += f' autocomplete="{autocomplete}"'
        caption = escape(label) + (' <span aria-hidden="true">*</span>' if required else '')
        if field_type == 'textarea':
            control = f'<textarea {attrs} rows="5" maxlength="2000"></textarea>'
        elif options:
            control = f'<select {attrs}>' + ''.join(
                f'<option>{escape(option)}</option>' for option in options) + '</select>'
        else:
            limit = 254 if field_type == 'email' else 160
            control = f'<input {attrs} type="{field_type}" maxlength="{limit}">'
        fields.append(f'<div class="ezuno-form-field{" ezuno-form-wide" if full else ""}">'
                      f'<label for="{ident}">{caption}</label>{control}</div>')

    field('name', 'Your name', required=True, autocomplete='name')
    field('email', 'Your email address', required=True, field_type='email', autocomplete='email')
    if kind != 'support':
        field('company', 'Company (optional)', autocomplete='organization', full=kind == 'trial')
    if kind == 'contact':
        field('request', 'I am interested in', options=[
            'Quote or sales order', 'Enterprise license', 'Reseller partnership', 'Other enquiry'])
    if kind == 'support':
        field('subject', 'Subject', required=True)
        field('version', 'ezuno / Alfresco version (optional)')
    field('message', 'Message (optional)' if kind == 'trial' else 'Your message',
          required=kind != 'trial', field_type='textarea', full=True)
    policy = os.path.relpath('our-privacy-policy/index.html', os.path.dirname(page) or '.')
    return f'''<form class="ezuno-form" data-ezuno-form="{kind}" aria-label="{title}"
        aria-describedby="{prefix}-delivery" action="mailto:ezuno@ezuno.com" method="post" enctype="text/plain">
      <div class="ezuno-form-note ezuno-form-wide">Fields marked * are required.</div>
      {''.join(fields)}
      <div class="ezuno-form-note ezuno-form-wide" id="{prefix}-delivery">
        Opens your email app with a draft addressed to <a href="mailto:ezuno@ezuno.com">ezuno@ezuno.com</a>.
        Send the email there to complete your request. <a href="{policy}">Privacy Policy</a>.
      </div>
      <button class="ezuno-form-submit ezuno-form-wide" type="submit">{button}</button>
      <noscript><div class="ezuno-form-note ezuno-form-wide">You can also email your request directly to
        <a href="mailto:ezuno@ezuno.com">ezuno@ezuno.com</a>.</div></noscript>
      <div class="ezuno-form-result ezuno-form-wide" hidden>
        <div class="ezuno-form-status" role="status" aria-live="polite"></div>
        <div class="ezuno-form-actions">
          <a class="ezuno-form-open" href="mailto:ezuno@ezuno.com">Open email draft again</a>
          <button class="ezuno-form-copy" type="button">Copy request</button>
        </div>
        <label for="{prefix}-draft">Your email draft (copy manually if needed)</label>
        <textarea id="{prefix}-draft" class="ezuno-form-draft" rows="8" readonly></textarea>
      </div>
    </form>'''


def reconstruct_forms(soup, page):
    count = 0
    for node in list(soup.find_all(string=SHORTCODE)):
        parts = SHORTCODE.split(str(node))
        node.parent['class'] = list(node.parent.get('class', [])) + ['ezuno-form-section']
        for index, part in enumerate(parts):
            if index % 2:
                fragment = BeautifulSoup(form_html(part, page), 'html.parser')
                node.insert_before(fragment.form)
                count += 1
            elif part.strip():
                node.insert_before(part)
        node.extract()
    return count
