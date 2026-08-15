/* Craft Collective Salon Group — shared behaviour.
   Loaded with `defer`, so it runs after each page's inline scripts have
   registered their own listeners. */
(function () {
  'use strict';

  /* ------------------------------------------------------ mobile nav ---- */

  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links') || document.querySelector('.nav-links');

  if (toggle && links) {
    /* The dismiss surface. Built here rather than shipped in the markup so
       that a browser with JS off never gets an invisible sheet over the page.
       See the note on `.nav-scrim` in site.css for why a real element is
       required: on iOS Safari a document-level click listener never hears a
       tap that lands on ordinary page content, so "tap outside to close" is
       dead on exactly the devices the drawer is built for. */
    var scrim = document.createElement('div');
    scrim.className = 'nav-scrim';
    scrim.setAttribute('aria-hidden', 'true');
    document.body.appendChild(scrim);

    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      links.classList.toggle('is-open', open);
      // Some pages' own CSS keys the drawer off `.active` instead.
      links.classList.toggle('active', open);
      document.body.classList.toggle('nav-open', open);
    };

    var isOpen = function () {
      return toggle.getAttribute('aria-expanded') === 'true';
    };

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      setOpen(!isOpen());
    });

    // Navigating away from an anchor on the same page should close the drawer.
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });

    /* Dismiss on the scrim. `pointerdown` rather than `click` so the drawer
       is gone by the time the finger lifts — waiting for the click reads as
       lag on touch. The `click` listener is the fallback for pointer-less
       browsers, and both are idempotent. */
    var dismiss = function (e) {
      if (!isOpen()) return;
      e.preventDefault();
      setOpen(false);
    };
    if (window.PointerEvent) scrim.addEventListener('pointerdown', dismiss);
    else scrim.addEventListener('touchstart', dismiss);
    scrim.addEventListener('click', dismiss);

    // Belt and braces for anything that lands outside both the drawer and
    // the scrim — the header bar's own empty space, chiefly.
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

    // A drawer left open across a back/forward restore is disorienting.
    window.addEventListener('pageshow', function () { setOpen(false); });

    // Resizing past the breakpoint leaves the drawer orphaned open otherwise.
    var mq = window.matchMedia('(min-width: 901px)');
    var onChange = function (e) { if (e.matches) setOpen(false); };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }

  /* ---------------------------------------------------- FAQ accordion ---- */

  /* This owns every accordion on the site. The three pages that shipped their
     own inline handler have it stripped at build time — on /faq/ that script
     ended up bound twice, so the first tap after load toggled an item open and
     immediately closed it again, and the accordion looked dead.

     Items toggle independently: closing a sibling to read a second answer is
     busywork when the answers are a few lines long. */

  var questions = document.querySelectorAll('.faq-question');

  var syncAll = function () {
    Array.prototype.forEach.call(questions, function (other) {
      var oItem = other.closest('.faq-item');
      other.setAttribute(
        'aria-expanded',
        oItem && oItem.classList.contains('open') ? 'true' : 'false'
      );
    });
  };

  Array.prototype.forEach.call(questions, function (q, i) {
    var item = q.closest('.faq-item');
    var answer = item && item.querySelector('.faq-answer');
    if (!q.hasAttribute('role')) q.setAttribute('role', 'button');
    if (!q.hasAttribute('tabindex')) q.setAttribute('tabindex', '0');
    q.setAttribute('aria-expanded', item && item.classList.contains('open') ? 'true' : 'false');

    if (answer) {
      if (!answer.id) answer.id = 'faq-a-' + i;
      q.setAttribute('aria-controls', answer.id);
    }

    if (item) {
      q.addEventListener('click', function () {
        item.classList.toggle('open');
        syncAll();
      });
    }

    q.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        q.click();
      }
    });
  });


  /* ------------------------------------------------- scroll reveal ---- */

  /* Sections ease in as they scroll into view.

     This effect hides real page content, so it is built to fail open at every
     step. The class that does the hiding is added by script, so no-JS never
     hides anything. Anything already on screen at load is marked revealed
     without animating — a hero that fades in after paint reads as jank, not
     polish. And a timer removes the whole effect shortly after load, so an
     observer that never fires (an unexpected overflow ancestor, a restored
     scroll position, a browser quirk) costs an animation rather than a
     section of the page. */

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  var targets = document.querySelectorAll(
    '.services, .gallery-preview, .locations, .testimonials, .faq, ' +
    '.faq-block, .xlinks, .svc-work, .content-section, .about-section, ' +
    '.related-posts, .team-section, .trust-bar, .book-cta, .cta-section, ' +
    '.reviews-main, .areas, .pillars, .maps-section, .expect, .why-us'
  );

  if ('IntersectionObserver' in window && !reduceMotion.matches && targets.length) {
    var armed = false;

    /* Geometry fallback, and the reason the effect can no longer strand a
       section. The observer is the nice path; this is the guarantee.

       Anything whose top edge has crossed the bottom of the viewport is
       revealed, which covers both "scrolled into view from below" and
       "already scrolled past" (negative top). It runs on scroll, resize,
       bfcache restore and tab wake, so every way a section can end up on
       screen is covered by plain arithmetic rather than by the observer
       continuing to deliver callbacks. If the observer arms the effect and
       then goes quiet — the failure that blanked everything below the fold —
       the next scroll event still reveals the content. */
    var revealVisible = function () {
      var vh = window.innerHeight || document.documentElement.clientHeight || 0;
      var remaining = 0;
      Array.prototype.forEach.call(targets, function (el) {
        if (el.classList.contains('is-in')) return;
        if (el.getBoundingClientRect().top < vh * 0.98) el.classList.add('is-in');
        else remaining++;
      });
      return remaining;
    };

    var ticking = false;
    var onScroll = function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        ticking = false;
        if (revealVisible() === 0) detach();
      });
    };

    var detach = function () {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      window.removeEventListener('pageshow', onScroll);
      document.removeEventListener('visibilitychange', onScroll);
    };

    var io = new IntersectionObserver(function (entries) {
      /* Mark what is on screen first, then arm the effect. Both happen in one
         task, so the browser paints the end state and nothing flashes. */
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        }
      });

      if (!armed) {
        document.documentElement.classList.add('js-reveal');
        armed = true;
      }
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.02 });

    Array.prototype.forEach.call(targets, function (el) {
      el.classList.add('reveal');
      io.observe(el);
    });

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    window.addEventListener('pageshow', onScroll);
    document.addEventListener('visibilitychange', onScroll);

    /* Sweep once after arming, on the frame the hiding class lands. Anything
       sitting in the opening viewport is revealed here even if the observer's
       first callback disagreed, so the fold is never left blank waiting for a
       scroll that may not come on a short page. */
    window.requestAnimationFrame(function () {
      if (armed && revealVisible() === 0) detach();
    });

    /* Nothing is hidden until the observer has actually fired.

       The first attempt hid every section up front and relied on the observer
       to reveal them. That inverts the risk: any environment where the
       observer does not run — a background tab, where both it and rAF are
       suspended — leaves the whole page blank rather than merely unanimated.
       An observer always delivers an initial entry for each target it is
       given, so arming the effect from inside that first callback makes "the
       observer works" a precondition of hiding anything. No observer, no
       animation, all content visible. */

    var onRM = function (e) {
      if (e.matches) document.documentElement.classList.remove('js-reveal');
    };
    if (reduceMotion.addEventListener) reduceMotion.addEventListener('change', onRM);
    else if (reduceMotion.addListener) reduceMotion.addListener(onRM);
  }
})();
