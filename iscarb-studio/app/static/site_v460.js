/* Language and theme controls for the ISCARB landing page.
   The page is always in ONE language at a time. English is the default; the
   single header button switches the complete interface to Arabic and back. */
(function () {
  'use strict';
  var root = document.documentElement;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private window */ } }
  };

  function languageButton() {
    var host = document.querySelector('.langPick');
    if (!host) return null;
    var button = document.getElementById('pageLangToggle');
    if (!button) {
      host.innerHTML = '<button type="button" id="pageLangToggle" class="languageToggle"></button>';
      button = document.getElementById('pageLangToggle');
    }
    return button;
  }

  function applyLang(value) {
    value = value === 'ar' ? 'ar' : 'en';
    root.setAttribute('data-lang', value);
    root.setAttribute('lang', value);
    root.setAttribute('dir', value === 'ar' ? 'rtl' : 'ltr');
    var button = languageButton();
    if (button) {
      button.textContent = value === 'ar' ? 'English' : 'العربية';
      button.setAttribute('lang', value === 'ar' ? 'en' : 'ar');
      button.setAttribute('dir', value === 'ar' ? 'ltr' : 'rtl');
      button.setAttribute('aria-label', value === 'ar' ? 'Switch interface to English' : 'تحويل الواجهة إلى العربية');
      button.title = value === 'ar' ? 'Switch to English' : 'التحويل إلى العربية';
    }
    try { document.dispatchEvent(new CustomEvent('iscarb:language', { detail: { language: value } })); } catch (e) { /* old browser */ }
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
    var langBtn = event.target.closest ? event.target.closest('#pageLangToggle') : null;
    if (langBtn) {
      var next = root.getAttribute('data-lang') === 'ar' ? 'en' : 'ar';
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

  // Never enter the old bilingual/no-data-lang state.
  applyLang(store.get('iscarb-lang') === 'ar' ? 'ar' : 'en');
  applyTheme(store.get('iscarb-theme') || 'dark');
})();
