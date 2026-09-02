/* Language and theme controls for the ISCARB landing page.
   Both languages ship in the markup: the control decides which is shown, and
   the choice survives a reload. Nothing here touches the compile pipeline. */
(function () {
  var root = document.documentElement;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private window */ } }
  };

  function applyLang(value) {
    if (value === 'ar' || value === 'en') {
      root.setAttribute('data-lang', value);
      root.setAttribute('lang', value);
      root.setAttribute('dir', value === 'ar' ? 'rtl' : 'ltr');
    } else {
      root.removeAttribute('data-lang');
      root.setAttribute('lang', 'en');
      root.setAttribute('dir', 'ltr');
    }
    var buttons = document.querySelectorAll('[data-set-lang]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute('aria-pressed', String(buttons[i].dataset.setLang === value));
    }
  }

  function applyTheme(value) {
    root.setAttribute('data-theme', value === 'light' ? 'light' : 'dark');
    var toggle = document.getElementById('themeToggle');
    if (toggle) {
      toggle.setAttribute('aria-pressed', String(value === 'light'));
      toggle.title = value === 'light' ? 'Switch to dark' : 'Switch to light';
    }
  }

  document.addEventListener('click', function (event) {
    var langBtn = event.target.closest ? event.target.closest('[data-set-lang]') : null;
    if (langBtn) {
      var next = root.getAttribute('data-lang') === langBtn.dataset.setLang ? '' : langBtn.dataset.setLang;
      store.set('iscarb-lang', next);
      applyLang(next);
      return;
    }
    if (event.target.closest && event.target.closest('#themeToggle')) {
      var theme = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      store.set('iscarb-theme', theme);
      applyTheme(theme);
    }
  });

  applyLang(store.get('iscarb-lang') || '');
  applyTheme(store.get('iscarb-theme') || 'dark');
})();
