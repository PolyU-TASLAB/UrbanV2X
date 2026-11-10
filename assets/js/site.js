(() => {
  const themeKey = 'urbanv2x-theme';
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
  let preferredTheme = null;
  try {
    const saved = localStorage.getItem(themeKey);
    if (saved === 'light' || saved === 'dark') preferredTheme = saved;
  } catch (_) {}
  const applyTheme = theme => {
    const dark = theme === 'dark';
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#0b1822' : '#ffffff');
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', dark ? 'Switch to day mode' : 'Switch to night mode');
      button.title = dark ? 'Switch to day mode' : 'Switch to night mode';
      button.querySelector('[data-theme-label]').textContent = dark ? 'Day' : 'Night';
    });
  };
  const defaultTheme = () => systemTheme.matches ? 'dark' : 'light';
  applyTheme(preferredTheme || defaultTheme());
  document.querySelectorAll('[data-theme-toggle]').forEach(button => button.addEventListener('click', () => {
    preferredTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(themeKey, preferredTheme); } catch (_) {}
    applyTheme(preferredTheme);
  }));
  systemTheme.addEventListener('change', () => {
    if (!preferredTheme) applyTheme(defaultTheme());
  });
  window.addEventListener('storage', event => {
    if (event.key !== themeKey && event.key !== null) return;
    preferredTheme = event.newValue === 'light' || event.newValue === 'dark' ? event.newValue : null;
    applyTheme(preferredTheme || defaultTheme());
  });

  const toggle = document.querySelector('[data-nav-toggle]');
  const menu = document.querySelector('[data-nav-menu]');

  if (toggle && menu) {
    const closeMenu = () => {
      toggle.setAttribute('aria-expanded', 'false');
      menu.classList.remove('is-open');
    };

    toggle.addEventListener('click', () => {
      const isOpen = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!isOpen));
      menu.classList.toggle('is-open', !isOpen);
    });

    menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeMenu();
        toggle.focus();
      }
    });

    document.addEventListener('click', (event) => {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) closeMenu();
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 1000) closeMenu();
    });
  }

  document.querySelectorAll('[data-copy-target]').forEach((button) => {
    button.addEventListener('click', async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) return;

      try {
        await navigator.clipboard.writeText(target.textContent.trim());
        const original = button.textContent;
        button.textContent = 'Copied';
        button.dataset.copied = 'true';
        window.setTimeout(() => {
          button.textContent = original;
          button.dataset.copied = 'false';
        }, 1800);
      } catch (error) {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(target);
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = 'Select & copy';
      }
    });
  });
})();
