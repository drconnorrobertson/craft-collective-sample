/* Craft Collective Salon Group — shared behaviour.
   Loaded with `defer`, so it runs after each page's inline scripts have
   registered their own listeners. */
(function () {
  'use strict';

  /* ------------------------------------------------------ mobile nav ---- */

  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links') || document.querySelector('.nav-links');

  if (toggle && links) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      links.classList.toggle('is-open', open);
      document.body.classList.toggle('nav-open', open);
    };

    var isOpen = function () {
      return toggle.getAttribute('aria-expanded') === 'true';
    };

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      setOpen(!isOpen());
    });

    // Navigating away from an anchor on the same page should close the drawer.
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });

    document.addEventListener('click', function (e) {
      if (isOpen() && !links.contains(e.target) && !toggle.contains(e.target)) {
        setOpen(false);
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) {
        setOpen(false);
        toggle.focus();
      }
    });

    // Resizing past the breakpoint leaves the drawer orphaned open otherwise.
    var mq = window.matchMedia('(min-width: 901px)');
    var onChange = function (e) { if (e.matches) setOpen(false); };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }

  /* ---------------------------------------------------- FAQ accordion ---- */

  /* The accordion's open/close is handled by each page's inline script; this
     only keeps the accessibility state in sync with the resulting class. */
  var questions = document.querySelectorAll('.faq-question');

  Array.prototype.forEach.call(questions, function (q, i) {
    var item = q.closest('.faq-item');
    var answer = item && item.querySelector('.faq-answer');

    if (!q.hasAttribute('role')) q.setAttribute('role', 'button');
    if (!q.hasAttribute('tabindex')) q.setAttribute('tabindex', '0');
    q.setAttribute('aria-expanded', item && item.classList.contains('open') ? 'true' : 'false');

    if (answer) {
      if (!answer.id) answer.id = 'faq-answer-' + i;
      q.setAttribute('aria-controls', answer.id);
    }

    var sync = function () {
      // Runs after the inline handler, so the class already reflects the
      // new state. Re-sync every question — the accordion closes siblings.
      Array.prototype.forEach.call(questions, function (other) {
        var oItem = other.closest('.faq-item');
        other.setAttribute(
          'aria-expanded',
          oItem && oItem.classList.contains('open') ? 'true' : 'false'
        );
      });
    };

    q.addEventListener('click', sync);
    q.addEventListener('keyup', function (e) {
      if (e.key === 'Enter' || e.key === ' ') sync();
    });
  });
})();
