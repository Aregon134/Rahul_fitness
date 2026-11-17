(() => {
  const header = document.querySelector('.site-header');
  const menuButton = document.querySelector('.menu-toggle');
  const menuPanel = document.querySelector('#navigation-panel');
  const setMenu = (open, restoreFocus = false) => {
    if (!menuButton || !menuPanel) return;
    menuPanel.hidden = !open;
    header.classList.toggle('menu-open', open);
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    if (restoreFocus) menuButton.focus();
  };
  menuButton?.addEventListener('click', () => setMenu(menuPanel.hidden));
  document.addEventListener('pointerdown', event => {
    if (menuPanel && !menuPanel.hidden && !header.contains(event.target)) setMenu(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuPanel && !menuPanel.hidden) setMenu(false, true);
  });
  header?.addEventListener('focusout', event => {
    if (event.relatedTarget && !header.contains(event.relatedTarget)) setMenu(false);
  });
  header?.querySelectorAll('nav a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  const navigationLinks = [...document.querySelectorAll('.desktop-nav > a, .expanded-links > a')];
  const sections = ['programs', 'about', 'contact'].map(id => document.getElementById(id)).filter(Boolean);
  const syncNavigation = () => {
    let current = '';
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= Math.min(250, innerHeight * .35)) current = section.id;
    }
    navigationLinks.forEach(link => {
      if (new URL(link.href).hash === '#' + current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  let scrollPending = false;
  window.addEventListener('scroll', () => {
    if (!scrollPending) requestAnimationFrame(() => { syncNavigation(); scrollPending = false; });
    scrollPending = true;
  }, { passive: true });
  syncNavigation();
  const openDialog = (dialog) => {
    if (!dialog || dialog.open) return;
    setMenu(false);
    dialog.returnFocus = document.activeElement;
    dialog.showModal();
    document.body.classList.add('dialog-open');
  };
  document.querySelectorAll('[data-open-finder], a[href="#find-program"]').forEach(button => button.addEventListener('click', event => { event.preventDefault(); openDialog(document.querySelector('#program-dialog')); }));
  document.querySelectorAll('a[href="#enquire"]').forEach(button => button.addEventListener('click', event => { event.preventDefault(); openDialog(document.querySelector('#enquiry-dialog')); }));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.querySelector('[data-close-dialog]')?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
    dialog.querySelectorAll('nav a').forEach(a => a.addEventListener('click', () => dialog.close()));
    dialog.addEventListener('close', () => { document.body.classList.remove('dialog-open'); dialog.returnFocus?.focus(); });
  });

  /* Hero Slider */
  const hero = document.querySelector('.hero');
  const slides = [...document.querySelectorAll('.hero-slide')];
  const controls = [...document.querySelectorAll('[data-slide]')];
  if (!hero || slides.length < 2) return;

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0;
  let timer = null;
  let paused = reducedMotion.matches;
  let isHovered = false;
  let isVisible = true;

  hero.setAttribute('role', 'region');
  hero.setAttribute('aria-roledescription', 'carousel');
  hero.setAttribute('aria-label', 'Featured training programs');

  // Inject visible Previous & Next navigation arrows
  const prevBtn = document.createElement('button');
  prevBtn.className = 'hero-arrow hero-prev';
  prevBtn.setAttribute('type', 'button');
  prevBtn.setAttribute('aria-label', 'Previous slide');
  prevBtn.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M15 18l-6-6 6-6"/></svg>';

  const nextBtn = document.createElement('button');
  nextBtn.className = 'hero-arrow hero-next';
  nextBtn.setAttribute('type', 'button');
  nextBtn.setAttribute('aria-label', 'Next slide');
  nextBtn.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M9 18l6-6-6-6"/></svg>';

  hero.appendChild(prevBtn);
  hero.appendChild(nextBtn);

  const heroControls = document.querySelector('.hero-controls');
  const playback = document.createElement('button');
  playback.className = 'slide-playback';
  playback.setAttribute('type', 'button');
  if (heroControls) {
    heroControls.insertBefore(playback, document.querySelector('.slide-count'));
  }

  const updatePlayback = () => {
    playback.textContent = paused ? 'PLAY' : 'PAUSE';
    playback.setAttribute('aria-label', paused ? 'Play slideshow' : 'Pause slideshow');
    playback.setAttribute('aria-pressed', String(paused));
  };

  const schedule = () => {
    clearTimeout(timer);
    if (!paused && !isHovered && isVisible && !document.hidden) {
      timer = setTimeout(() => displaySlide(active + 1, false), 5000);
    }
  };

  const displaySlide = (index, announce = true) => {
    active = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      const isActive = i === active;
      slide.classList.toggle('is-active', isActive);
      if (isActive) {
        slide.removeAttribute('hidden');
      } else {
        slide.setAttribute('hidden', '');
      }
      slide.setAttribute('aria-label', `Slide ${i + 1} of ${slides.length}`);
      slide.setAttribute('aria-roledescription', 'slide');
      slide.setAttribute('role', 'group');
    });
    controls.forEach((button, i) => button.setAttribute('aria-pressed', String(i === active)));
    const counter = document.querySelector('.slide-count');
    if (counter) {
      counter.setAttribute('aria-live', announce ? 'polite' : 'off');
      counter.textContent = `${String(active + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    }
    schedule();
  };

  // Connect program cards anchor links
  const cards = [...document.querySelectorAll('.program-card')];
  const cardIds = ['program-x-frame', 'program-coaching', 'program-diet'];
  slides.forEach((slide, i) => {
    if (!cards[i]) return;
    cards[i].id = cardIds[i];
    slide.querySelectorAll('a').forEach(link => link.setAttribute('href', '#' + cardIds[i]));
  });

  // Event Listeners
  prevBtn.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); displaySlide(active - 1); });
  nextBtn.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); displaySlide(active + 1); });
  controls.forEach((button, i) => button.addEventListener('click', (e) => { e.preventDefault(); displaySlide(i); }));
  playback.addEventListener('click', (e) => { e.preventDefault(); paused = !paused; updatePlayback(); schedule(); });

  // Keyboard navigation
  hero.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight') { event.preventDefault(); displaySlide(active + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); displaySlide(active - 1); }
  });

  // Hover pauses autoplay, leaving resumes
  hero.addEventListener('mouseenter', () => { isHovered = true; clearTimeout(timer); });
  hero.addEventListener('mouseleave', () => { isHovered = false; schedule(); });

  // Swipe on mobile & drag on desktop
  let startX = 0;
  let isDown = false;
  hero.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
  hero.addEventListener('touchend', e => {
    const diff = e.changedTouches[0].clientX - startX;
    if (Math.abs(diff) > 40) displaySlide(active + (diff < 0 ? 1 : -1));
  }, { passive: true });

  hero.addEventListener('mousedown', e => {
    if (e.target.closest('button, a, input')) return;
    startX = e.clientX;
    isDown = true;
  });
  hero.addEventListener('mouseup', e => {
    if (!isDown) return;
    const diff = e.clientX - startX;
    if (Math.abs(diff) > 45) displaySlide(active + (diff < 0 ? 1 : -1));
    isDown = false;
  });

  document.addEventListener('visibilitychange', schedule);
  reducedMotion.addEventListener('change', () => { paused = reducedMotion.matches; updatePlayback(); schedule(); });
  new IntersectionObserver(entries => { isVisible = entries[0].isIntersecting; schedule(); }, { threshold: .15 }).observe(hero);

  updatePlayback();
  displaySlide(0, false);
})();
