/* Static-site compatibility. No server, CMS, or build step is required. */
(function () {
  'use strict';
  // The original redirects /home#section to /#section. A static page has no
  // redirect, so let the theme finish collapsing tabs before anchoring a
  // direct section link. Otherwise browsers can retain its pre-layout offset.
  window.addEventListener('load', function () {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        var id;
        try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
        var target = id && document.getElementById(id);
        if (target) window.scrollTo(window.scrollX, window.scrollY + target.getBoundingClientRect().top);
      });
    });
  });
  // file:// does not implement HTTP cookies. Retain the original consent UI
  // by giving it an expiring cookie store backed by browser local storage.
  if (location.protocol !== 'file:') return;
  var key = 'ezuno-static-cookies';
  var cookies = {};
  try { cookies = JSON.parse(localStorage.getItem(key) || '{}'); } catch (_) {}
  try {
    Object.defineProperty(document, 'cookie', {
      configurable: true,
      get: function () {
        return Object.keys(cookies).filter(function (name) {
          return !cookies[name].expires || cookies[name].expires > Date.now();
        }).map(function (name) { return name + '=' + cookies[name].value; }).join('; ');
      },
      set: function (text) {
        var parts = text.split(';');
        var pair = parts.shift();
        var split = pair.indexOf('=');
        if (split < 0) return;
        var name = pair.slice(0, split).trim();
        var entry = { value: pair.slice(split + 1) };
        parts.forEach(function (part) {
          var option = part.trim();
          if (/^expires=/i.test(option)) entry.expires = Date.parse(option.slice(8));
        });
        cookies[name] = entry;
        try { localStorage.setItem(key, JSON.stringify(cookies)); } catch (_) {}
      }
    });
  } catch (_) { /* Storage can be disabled by browser preferences. */ }
}());
