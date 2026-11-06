/* Original ezuno static-site interactions. No libraries, tracking or storage. */
(function () {
  'use strict';

  function ready() {
    document.documentElement.classList.add('js');
    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    var navigation = document.getElementById('main-menu');
    var menuButton = document.querySelector('.navbar-toggle');

    function closeMenu(restoreFocus) {
      if (!navigation || !menuButton) return;
      navigation.classList.remove('is-open');
      menuButton.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('menu-open');
      if (restoreFocus) menuButton.focus();
    }

    if (navigation && menuButton) {
      menuButton.setAttribute('aria-controls', navigation.id);
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Toggle navigation');
      menuButton.addEventListener('click', function () {
        var open = menuButton.getAttribute('aria-expanded') !== 'true';
        navigation.classList.toggle('is-open', open);
        menuButton.setAttribute('aria-expanded', String(open));
        document.body.classList.toggle('menu-open', open);
      });
      navigation.addEventListener('click', function (event) {
        if (event.target.closest('a[href]')) closeMenu(false);
      });
      document.addEventListener('click', function (event) {
        if (!navigation.contains(event.target) && !menuButton.contains(event.target)) closeMenu(false);
      });
      window.addEventListener('resize', function () {
        if (window.innerWidth >= 992) closeMenu(false);
      });
    }

    var tabGroups = [];
    document.querySelectorAll('.features-tabs').forEach(function (group, groupIndex) {
      var panels = Array.from(group.children).filter(function (child) {
        return child.tagName === 'DIV' && child.id;
      });
      var list = group.querySelector('ul.tabs');
      if (!list || !panels.length) return;
      var tabs = [];
      panels.forEach(function (panel) {
        var item = panel.querySelector('li.tab');
        if (item) list.appendChild(item);
        var link = item && item.querySelector('a');
        if (!link) return;
        link.id = 'feature-tab-' + groupIndex + '-' + tabs.length;
        link.setAttribute('role', 'tab');
        link.setAttribute('aria-controls', panel.id);
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-labelledby', link.id);
        panel.tabIndex = 0;
        item.setAttribute('role', 'presentation');
        tabs.push({ link: link, item: item, panel: panel });
      });
      if (!tabs.length) return;
      list.setAttribute('role', 'tablist');
      list.setAttribute('aria-label', 'ezuno features');
      group.classList.add('has-tabs');

      function select(index, focus) {
        tabs.forEach(function (tab, position) {
          var active = position === index;
          tab.link.setAttribute('aria-selected', String(active));
          tab.link.tabIndex = active ? 0 : -1;
          tab.item.classList.toggle('is-active', active);
          tab.panel.classList.toggle('is-active', active);
          tab.panel.hidden = !active;
        });
        if (focus) tabs[index].link.focus();
      }

      tabs.forEach(function (tab, index) {
        tab.link.addEventListener('click', function (event) {
          event.preventDefault();
          select(index, false);
        });
        tab.link.addEventListener('keydown', function (event) {
          var next;
          if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
          if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
          if (event.key === 'Home') next = 0;
          if (event.key === 'End') next = tabs.length - 1;
          if (event.key === ' ') next = index;
          if (next !== undefined) {
            event.preventDefault();
            select(next, true);
          }
        });
      });
      select(0, false);
      tabGroups.push({ tabs: tabs, select: select });
    });

    var accordions = [];
    document.querySelectorAll('.vc_tta-panel').forEach(function (panel, index) {
      var trigger = panel.querySelector('.vc_tta-panel-heading a');
      var content = panel.querySelector('.vc_tta-panel-body');
      if (!trigger || !content) return;
      content.id = content.id || 'faq-content-' + index;
      trigger.id = trigger.id || 'faq-trigger-' + index;
      trigger.setAttribute('role', 'button');
      trigger.setAttribute('aria-controls', content.id);
      content.setAttribute('aria-labelledby', trigger.id);
      content.setAttribute('role', 'region');

      function setOpen(open) {
        panel.classList.toggle('is-open', open);
        trigger.setAttribute('aria-expanded', String(open));
        content.hidden = !open;
      }

      setOpen(false);
      trigger.addEventListener('click', function (event) {
        event.preventDefault();
        setOpen(trigger.getAttribute('aria-expanded') !== 'true');
      });
      trigger.addEventListener('keydown', function (event) {
        if (event.key === ' ') {
          event.preventDefault();
          trigger.click();
        }
      });
      accordions.push({ panel: panel, setOpen: setOpen });
    });

    document.querySelectorAll('.testimonials').forEach(function (carousel) {
      var slides = Array.from(carousel.children).filter(function (child) {
        return child.classList.contains('tt-content');
      });
      if (slides.length < 2) return;
      var current = 0;
      carousel.setAttribute('role', 'region');
      carousel.setAttribute('aria-roledescription', 'carousel');
      carousel.setAttribute('aria-label', 'Customer testimonials');
      var controls = document.createElement('div');
      controls.className = 'ezuno-carousel-controls';
      var previous = document.createElement('button');
      previous.type = 'button';
      previous.className = 'ezuno-carousel-prev';
      previous.textContent = 'Previous';
      previous.setAttribute('aria-label', 'Previous testimonial');
      var next = document.createElement('button');
      next.type = 'button';
      next.className = 'ezuno-carousel-next';
      next.textContent = 'Next';
      next.setAttribute('aria-label', 'Next testimonial');
      var status = document.createElement('span');
      status.className = 'ezuno-carousel-status';
      status.setAttribute('aria-live', 'polite');
      status.setAttribute('aria-atomic', 'true');
      controls.append(previous, status, next);
      carousel.appendChild(controls);

      function show(index) {
        current = (index + slides.length) % slides.length;
        slides.forEach(function (slide, position) {
          slide.hidden = position !== current;
          slide.classList.toggle('is-active', position === current);
          slide.setAttribute('role', 'group');
          slide.setAttribute('aria-roledescription', 'slide');
          slide.setAttribute('aria-label', (position + 1) + ' of ' + slides.length);
        });
        status.textContent = (current + 1) + ' / ' + slides.length;
      }
      previous.addEventListener('click', function () { show(current - 1); });
      next.addEventListener('click', function () { show(current + 1); });
      show(0);
    });

    var modal = document.getElementById('video-modal');
    var videoOpener = null;
    var closeVideo = function () {};
    if (modal) {
      // Native dialog keeps keyboard focus inside even when Vimeo owns focus.
      if (typeof HTMLDialogElement !== 'undefined') {
        var dialog = document.createElement('dialog');
        Array.from(modal.attributes).forEach(function (attribute) {
          dialog.setAttribute(attribute.name, attribute.value);
        });
        while (modal.firstChild) dialog.appendChild(modal.firstChild);
        modal.replaceWith(dialog);
        modal = dialog;
      }
      var nativeModal = typeof modal.showModal === 'function';
      var content = modal.querySelector('.modal-content') || modal;
      // The HTML contains no active iframe; preserve that rule on reinitialisation.
      modal.querySelectorAll('iframe').forEach(function (frame) { frame.remove(); });
      modal.hidden = true;
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-label', 'ezuno product video');
      modal.tabIndex = -1;
      var close = document.createElement('button');
      close.type = 'button';
      close.className = 'ezuno-video-close';
      close.textContent = '\u00d7';
      close.setAttribute('aria-label', 'Close video');
      content.prepend(close);
      var frameHost = document.createElement('div');
      frameHost.className = 'ezuno-video-frame';
      content.appendChild(frameHost);
      var note = document.createElement('p');
      note.className = 'ezuno-video-note';
      note.textContent = 'Video hosted by Vimeo.';
      content.appendChild(note);
      var background = [];

      function isolateVideo() {
        var branch = modal;
        while (branch.parentElement && branch.parentElement !== document.documentElement) {
          Array.from(branch.parentElement.children).forEach(function (sibling) {
            if (sibling !== branch) {
              background.push({ node: sibling, inert: sibling.inert });
              sibling.inert = true;
            }
          });
          branch = branch.parentElement;
        }
      }

      closeVideo = function () {
        if (modal.hidden) return;
        frameHost.replaceChildren();
        if (nativeModal && modal.open) modal.close();
        modal.hidden = true;
        modal.classList.remove('is-open');
        document.body.classList.remove('modal-open');
        background.forEach(function (entry) { entry.node.inert = entry.inert; });
        background = [];
        if (videoOpener && document.contains(videoOpener)) videoOpener.focus();
      };

      document.querySelectorAll('[data-target="#video-modal"], [data-ezuno-video]').forEach(function (trigger) {
        if (!trigger.hasAttribute('href')) trigger.setAttribute('href', 'https://vimeo.com/99855952');
        trigger.setAttribute('aria-haspopup', 'dialog');
        trigger.setAttribute('aria-controls', modal.id);
        if (!trigger.textContent.trim()) trigger.setAttribute('aria-label', 'Play ezuno product video');
        trigger.addEventListener('click', function (event) {
          event.preventDefault();
          videoOpener = trigger;
          var iframe = document.createElement('iframe');
          iframe.title = 'ezuno product video on Vimeo';
          iframe.allow = 'autoplay; fullscreen; picture-in-picture';
          iframe.setAttribute('allowfullscreen', '');
          iframe.referrerPolicy = 'strict-origin-when-cross-origin';
          iframe.src = 'https://player.vimeo.com/video/99855952?autoplay=1&dnt=1';
          frameHost.replaceChildren(iframe);
          modal.hidden = false;
          modal.classList.add('is-open');
          document.body.classList.add('modal-open');
          if (nativeModal) modal.showModal();
          else isolateVideo();
          close.focus();
        });
      });
      close.addEventListener('click', closeVideo);
      modal.addEventListener('cancel', function (event) {
        event.preventDefault();
        closeVideo();
      });
      modal.addEventListener('click', function (event) {
        if (event.target === modal) closeVideo();
      });
      modal.addEventListener('keydown', function (event) {
        if (event.key !== 'Tab') return;
        var focusable = Array.from(modal.querySelectorAll('button, a[href], iframe, [tabindex="0"]'));
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      });
      document.addEventListener('focusin', function (event) {
        if (!modal.hidden && !modal.contains(event.target)) close.focus();
      });
    }

    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      if (modal && !modal.hidden) closeVideo();
      else if (menuButton && menuButton.getAttribute('aria-expanded') === 'true') closeMenu(true);
    });

    function revealTarget(target) {
      tabGroups.forEach(function (group) {
        group.tabs.forEach(function (tab, index) {
          if (tab.panel === target || tab.panel.contains(target)) group.select(index, false);
        });
      });
      accordions.forEach(function (accordion) {
        if (accordion.panel === target || accordion.panel.contains(target)) accordion.setOpen(true);
      });
    }

    function scrollToTarget(target, animate) {
      revealTarget(target);
      var header = document.querySelector('.navbar');
      var offset = header ? header.getBoundingClientRect().height : 0;
      var top = window.scrollY + target.getBoundingClientRect().top - offset - 16;
      window.scrollTo({ top: Math.max(0, top), behavior: animate && !reducedMotion.matches ? 'smooth' : 'auto' });
    }

    function hashTarget(hash) {
      try { return document.getElementById(decodeURIComponent(hash.slice(1))); }
      catch (_) { return null; }
    }

    document.addEventListener('click', function (event) {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      var link = event.target.closest('a[href]');
      if (!link || link.target === '_blank' || link.hasAttribute('download')) return;
      var url;
      try { url = new URL(link.href, location.href); } catch (_) { return; }
      if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash) return;
      var target = hashTarget(url.hash);
      if (!target) return;
      event.preventDefault();
      closeMenu(false);
      // History APIs can be unavailable for local file URLs; scrolling still works.
      try { history.pushState(null, '', url.hash); } catch (_) {}
      scrollToTarget(target, true);
    });

    function followHash() {
      var target = hashTarget(location.hash);
      if (target) scrollToTarget(target, false);
    }
    window.addEventListener('hashchange', followHash);
    window.addEventListener('load', function () {
      requestAnimationFrame(function () { requestAnimationFrame(followHash); });
    });
    followHash();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready, { once: true });
  else ready();
}());
