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
    dialog.querySelector('[data-close-dialog]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
    dialog.querySelectorAll('nav a').forEach(a => a.addEventListener('click', () => dialog.close()));
    dialog.addEventListener('close', () => { document.body.classList.remove('dialog-open'); dialog.returnFocus?.focus(); });
  });
  const hero = document.querySelector('.hero');
  const slides = [...document.querySelectorAll('.hero-slide')];
  const controls = [...document.querySelectorAll('[data-slide]')];
  if (slides.length < 2) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0;
  let timer;
  let paused = reducedMotion.matches;
  let hovering = false;
  let focused = false;
  let visible = true;
  hero.setAttribute('role', 'region');
  hero.setAttribute('aria-roledescription', 'carousel');
  hero.setAttribute('aria-label', 'Featured training programs');
  hero.setAttribute('tabindex', '0');
  const playback = document.createElement('button');
  playback.className = 'slide-playback';
  document.querySelector('.hero-controls').insertBefore(playback, document.querySelector('.slide-count'));
  const updatePlayback = () => {
    playback.textContent = paused ? 'PLAY' : 'PAUSE';
    playback.setAttribute('aria-label', paused ? 'Play slideshow' : 'Pause slideshow');
    playback.setAttribute('aria-pressed', String(paused));
  };
  const schedule = () => {
    clearTimeout(timer);
    if (!paused && !hovering && !focused && visible && !document.hidden) timer = setTimeout(() => displaySlide(active + 1, false), 6000);
  };
  const displaySlide = (index, announce = true) => {
    active = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      // CSS visibility and accessibility state must move together.
      slide.classList.toggle('is-active', i === active);
      slide.hidden = i !== active;
      slide.setAttribute('aria-label', `Slide ${i + 1} of ${slides.length}`);
      slide.setAttribute('aria-roledescription', 'slide');
      slide.setAttribute('role', 'group');
    });
    controls.forEach((button, i) => button.setAttribute('aria-pressed', String(i === active)));
    const counter = document.querySelector('.slide-count');
    counter.setAttribute('aria-live', announce ? 'polite' : 'off');
    counter.textContent = `${String(active + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    schedule();
  };
  // Explore buttons stay on the homepage; product cards retain their detail pages.
  const cards = [...document.querySelectorAll('.program-card')];
  const cardIds = ['program-x-frame', 'program-coaching', 'program-diet'];
  slides.forEach((slide, i) => {
    if (!cards[i]) return;
    cards[i].id = cardIds[i];
    slide.querySelectorAll('a').forEach(link => link.setAttribute('href', '#' + cardIds[i]));
  });
  controls.forEach((button, i) => button.addEventListener('click', () => displaySlide(i)));
  playback.addEventListener('click', () => { paused = !paused; updatePlayback(); schedule(); });
  hero.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      displaySlide(active + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  hero.addEventListener('mouseenter', () => { hovering = true; schedule(); });
  hero.addEventListener('mouseleave', () => { hovering = false; schedule(); });
  hero.addEventListener('focusin', () => { focused = true; schedule(); });
  hero.addEventListener('focusout', event => { focused = hero.contains(event.relatedTarget); schedule(); });
  let startTouch;
  hero.addEventListener('touchstart', event => { startTouch = { x: event.touches[0].clientX, y: event.touches[0].clientY }; }, { passive: true });
  hero.addEventListener('touchend', event => {
    if (!startTouch) return;
    const dx = event.changedTouches[0].clientX - startTouch.x;
    const dy = event.changedTouches[0].clientY - startTouch.y;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) displaySlide(active + (dx < 0 ? 1 : -1));
    startTouch = null;
  }, { passive: true });
  document.addEventListener('visibilitychange', schedule);
  reducedMotion.addEventListener('change', () => { paused = reducedMotion.matches; updatePlayback(); schedule(); });
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; schedule(); }, { threshold: .15 }).observe(hero);
  updatePlayback();
  displaySlide(0, false);
})();
