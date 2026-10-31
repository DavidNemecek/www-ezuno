/* Prepare email drafts locally. Nothing is submitted or stored by this site. */
(function () {
  'use strict';
  var recipient = 'ezuno@ezuno.com';
  var subjects = {
    trial: 'ezuno: Free 10-user license request',
    contact: 'ezuno: Contact / quote request',
    support: 'ezuno: Support request'
  };
  var labels = {
    name: 'Name', email: 'Email', company: 'Company', request: 'Request',
    subject: 'Subject', version: 'ezuno / Alfresco version', message: 'Message'
  };

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-ezuno-form]').forEach(function (form) {
      var result = form.querySelector('.ezuno-form-result');
      var status = form.querySelector('.ezuno-form-status');
      var draft = form.querySelector('.ezuno-form-draft');
      var open = form.querySelector('.ezuno-form-open');
      // Editing invalidates the prepared draft, so a fallback never sends stale details.
      form.addEventListener('input', function (event) {
        if (event.target.name) result.hidden = true;
      });
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        // Native required validation also rejects whitespace-only names/messages.
        Array.prototype.forEach.call(form.elements, function (field) {
          if (field.name && field.required && field.type !== 'select-one') {
            field.value = field.value.trim();
          }
        });
        if (!form.reportValidity()) return;
        var kind = form.dataset.ezunoForm;
        var subject = subjects[kind];
        var lines = [subject, ''];
        Object.keys(labels).forEach(function (name) {
          var field = form.elements.namedItem(name);
          if (field && field.value.trim()) lines.push(labels[name] + ': ' + field.value.trim());
        });
        if (kind === 'trial') lines.push('', 'Please send me a FREE BASIC license for 10 users.');
        var body = lines.join('\r\n').replace(/\r?\n/g, '\r\n');
        // Values belong in the body only; encode each query value to preserve Unicode,
        // ampersands, plus signs and newlines without creating additional mail headers.
        var mailto = 'mailto:' + recipient + '?subject=' + encodeURIComponent(subject) +
          '&body=' + encodeURIComponent(body);
        open.href = mailto;
        draft.value = 'To: ' + recipient + '\r\nSubject: ' + subject + '\r\n\r\n' + body;
        result.hidden = false;
        status.textContent = 'Your email draft is ready. Send it in your email app to complete your request. ' +
          'If no app opens, copy the request below and email it to ' + recipient + '.';
        // This runs directly in the visitor's submit gesture. It opens a draft,
        // and never claims that the email was sent or that a license was issued.
        window.location.href = mailto;
      });
      form.querySelector('.ezuno-form-copy').addEventListener('click', async function () {
        try {
          if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
          await navigator.clipboard.writeText(draft.value);
          status.textContent = 'Request copied. Paste it into an email to ' + recipient + ' and send it there.';
        } catch (_) {
          draft.focus();
          draft.select();
          status.textContent = 'Select and copy the draft below, then email it to ' + recipient + '.';
        }
      });
    });
  });
}());
