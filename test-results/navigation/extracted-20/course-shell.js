/* Shared course navigation and preference. No assessment data is read or changed. */
(() => {
  'use strict';
  const root = document.documentElement;
  const button = document.getElementById('themeBtn');
  const setTheme = value => {
    root.dataset.theme = value;
    if (button) {
      button.textContent = value === 'dark' ? 'Light mode' : 'Dark mode';
      button.setAttribute('aria-label', 'Switch to ' + (value === 'dark' ? 'light' : 'dark') + ' mode');
    }
  };
  let theme = 'light';
  try { theme = localStorage.getItem('iscarb-theme') === 'dark' ? 'dark' : 'light'; } catch {}
  setTheme(theme);
  button?.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    try { localStorage.setItem('iscarb-theme', next); } catch {}
  });
  const toggle = document.getElementById('navToggle');
  const nav = document.getElementById('courseNav');
  if (toggle && nav) {
    const close = () => { nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); };
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { close(); toggle.focus(); }
    });
  }
  if (!document.getElementById('top')) document.body.id = 'top';
  // A chapter ZIP contains its own lecture and sources. Cross-course routes
  // open the complete public site instead of pointing at absent sibling files.
  if (location.protocol === 'file:') {
    const script = [...document.scripts].find(el => el.src.includes('/course-shell.js'));
    if (script) {
      const packageRoot = new URL('.', script.src);
      document.querySelectorAll('.site-header a,.site-footer a,.course-page main a').forEach(link => {
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#')) return;
        const target = new URL(href, location.href);
        if (target.protocol === 'file:' && target.pathname.startsWith(packageRoot.pathname)) {
          link.href = 'https://adeebnoor.github.io/CPIT/' + target.pathname.slice(packageRoot.pathname.length) + target.search + target.hash;
        }
      });
    }
  }
})();
