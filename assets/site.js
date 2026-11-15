/* Preview interactions run locally. No forms, analytics, network requests or storage. */
(() => {
  const panels = {
    'preview-consultation': {
      kicker: 'Booking preview', title: 'Your consultation, before booking.',
      intro: 'This panel previews the next step. No appointment is booked and no payment is collected.',
      items: ['[CLIENT TO CONFIRM: ₹ price, taxes and call duration]', '[CLIENT TO CONFIRM: meeting platform, preparation and takeaways]', '[CLIENT TO CONFIRM: cancellation and rescheduling terms]'],
      after: 'Planned next step: booking, payment and scheduling. The providers and final sequence will be agreed after review.'
    },
    'preview-course': {
      kicker: 'Enrolment preview', title: 'The X Frame Method.',
      intro: 'An online fitness course. This panel does not enrol you, take payment or create an account.',
      items: ['[CLIENT TO CONFIRM: ₹ course price, taxes and purchase terms]', '[CLIENT TO CONFIRM: curriculum, resources, equipment and access period]', '[CLIENT TO CONFIRM: support, refunds and course platform]'],
      after: 'Planned next step: purchase and student access. Course hosting and the student experience will be specified after review.'
    },
    'preview-coaching': {
      kicker: 'Application preview', title: 'A first introduction to Rahul.',
      intro: 'The planned application will ask for the following. There are no input fields here; nothing is submitted or saved.',
      items: ['Name and email', 'Primary goal and training experience', 'Availability and preferred contact method'],
      after: '[CLIENT TO CONFIRM: approved contact options, privacy notice, application review and response time] Detailed health information belongs in later onboarding.'
    }
  };
  const checklist = [
    ['Credentials & biography', 'Qualifications, experience, approved biography and Rahul’s direct involvement.'],
    ['Photographs & media', 'Portraits, coaching images, course demonstrations, image rights and descriptive alternatives.'],
    ['Client stories', 'Written consent, approved quote, name, images, verified outcome and timeframe.'],
    ['Consultation', '₹ price, tax treatment, duration, platform, scope, preparation, takeaways and rescheduling.'],
    ['Course', 'Actual method, intended audience, outcomes, module titles, lesson count, equipment, resources, support, access and ₹ price.'],
    ['Coaching', 'Training/nutrition scope, check-ins, response times, duration, team involvement, service terms and ₹ price.'],
    ['Later integrations', 'Booking/payment sequence, providers, course platform, student access and application processing.'],
    ['Before public launch', 'Confirmed content, legal name/contact, privacy/refund terms, browser checks and /1-1-coachin/ redirect.']
  ];
  function init() {
    const scope = document.querySelector('.rf') || document.body;
    let host = document.getElementById('rf-panels');
    if (!host) {
      host = document.createElement('div'); host.id = 'rf-panels'; scope.append(host);
    }
    const dialog = document.createElement('dialog');
    dialog.className = 'rf-panel';
    dialog.setAttribute('aria-labelledby', 'rf-panel-title');
    host.append(dialog);
    let returnFocus = null;
    const escape = value => value.replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    function openPanel(id, trigger) {
      const data = panels[id];
      returnFocus = trigger;
      const body = data
        ? `<p class="rf-eyebrow">${data.kicker} / phase one</p><h2 id="rf-panel-title">${data.title}</h2><p>${data.intro}</p><ul>${data.items.map(item => `<li>${escape(item)}</li>`).join('')}</ul><p class="rf-confirm">${data.after}</p>`
        : `<p class="rf-eyebrow">Client review / phase one</p><h2 id="rf-panel-title">The content checklist.</h2><p>Everything still needed to replace the marked placeholders and plan the later integrations.</p><ol class="rf-checklist">${checklist.map(([title, copy]) => `<li><strong>${title}</strong><span>[CLIENT TO CONFIRM: ${escape(copy)}]</span></li>`).join('')}</ol>`;
      dialog.innerHTML = `<div class="rf-panel-body"><button type="button" class="rf-close" aria-label="Close preview">×</button>${body}</div>`;
      dialog.querySelector('.rf-close').addEventListener('click', () => dialog.close());
      dialog.showModal();
      dialog.scrollTop = 0;
      dialog.querySelector('.rf-close').focus();
    }
    document.addEventListener('click', event => {
      const anchor = event.target.closest('a[href]');
      if (!anchor) return;
      const fragment = anchor.getAttribute('href');
      if (!fragment.startsWith('#')) return;
      const id = fragment.slice(1);
      if (panels[id] || id === 'review-checklist') {
        event.preventDefault(); openPanel(id, anchor);
      }
    });
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener('close', () => { if (returnFocus?.isConnected) returnFocus.focus(); });
    const toggle = document.querySelector('.rf-menu-toggle');
    const nav = document.getElementById('rf-main-nav');
    function closeMenu() { if (!toggle || !nav) return; toggle.setAttribute('aria-expanded', 'false'); nav.classList.remove('is-open'); }
    toggle?.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(expanded)); nav.classList.toggle('is-open', expanded);
    });
    nav?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); }
    });
    // The wrapper also works with WordPress draft-preview query strings.
    document.querySelectorAll('.rf-nav a').forEach(anchor => {
      const target = new URL(anchor.href);
      const normalize = value => value.replace(/index\.html$/, '').replace(/\/$/, '');
      const current = new URL(location.href);
      if (normalize(target.pathname) === normalize(current.pathname) &&
          target.searchParams.get('page_id') === current.searchParams.get('page_id')) anchor.setAttribute('aria-current', 'page');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
