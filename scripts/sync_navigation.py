"""Keep all static pages on the same navigation markup and stylesheet."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    'index.html': 'Overview',
    'sensors/index.html': 'Sensors',
    'calibration/index.html': 'Calibration',
    'download/index.html': 'Download',
    'positioning/index.html': 'Overview',
    '404.html': None,
}
LINKS = [('Overview', 'index.html'), ('Sensors', 'sensors/'),
         ('Calibration', 'calibration/'), ('Download', 'download/')]
VERSION = '20261111-theme'
THEME_INIT = '''  <script data-theme-init>
    (() => {
      let theme;
      try { theme = localStorage.getItem('urbanv2x-theme'); } catch (_) {}
      if (theme !== 'light' && theme !== 'dark') theme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      document.documentElement.dataset.theme = theme;
      document.documentElement.style.colorScheme = theme;
      document.querySelector('meta[name="theme-color"]')?.setAttribute('content', theme === 'dark' ? '#0b1822' : '#ffffff');
    })();
  </script>'''

for name, active in PAGES.items():
    path = ROOT / name
    prefix = '../' if '/' in name else './'
    links = []
    for label, target in LINKS:
        current = ' aria-current="page"' if label == active else ''
        links.append(f'        <a href="{prefix}{target}"{current}>{label}</a>')
    links += [
        '        <a href="https://polyu-taslab.github.io/" target="_blank" rel="noopener noreferrer">TAS Lab ↗</a>',
        '        <a class="site-navigation-paper" href="https://www.overleaf.com/2516394827fhbggmhfvhjr#03cc03" target="_blank" rel="noopener noreferrer">Read the paper ↗</a>',
    ]
    header = f'''  <header class="site-navigation">
    <div class="site-navigation-inner">
      <a class="site-navigation-brand" href="{prefix}index.html" aria-label="UrbanV2X home"><img src="{prefix}assets/img/taslab-icon.jpg" alt="TAS Lab"><span>Urban<span>V2X</span></span></a>
      <nav class="site-navigation-links" id="site-navigation-menu" data-nav-menu aria-label="Main navigation">
{chr(10).join(links)}
      </nav>
      <button class="site-theme-toggle" type="button" data-theme-toggle aria-label="Switch to night mode" aria-pressed="false" title="Switch to night mode">
        <svg class="theme-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 10.7 10.7Z"/></svg>
        <svg class="theme-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4m0-14.2-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>
        <span data-theme-label>Night</span>
      </button>
      <button class="site-navigation-toggle" type="button" data-nav-toggle aria-label="Toggle navigation" aria-expanded="false" aria-controls="site-navigation-menu"><span aria-hidden="true"></span></button>
    </div>
  </header>'''
    text = path.read_text()
    text, count = re.subn(r'  <header\b[^>]*>.*?</header>', header, text, count=1, flags=re.S)
    assert count == 1, name
    text = re.sub(r'\s*<link rel="stylesheet" href="[^"]*assets/css/(?:navigation|theme)\.css(?:\?[^"]*)?">', '', text)
    text = re.sub(r'\s*<script data-theme-init>.*?</script>', '', text, flags=re.S)
    text = text.replace('</head>', f'{THEME_INIT}\n  <link rel="stylesheet" href="{prefix}assets/css/navigation.css?v={VERSION}">\n  <link rel="stylesheet" href="{prefix}assets/css/theme.css?v={VERSION}">\n</head>')
    text, count = re.subn(r'(<script\b[^>]*src=")[^"]*assets/js/site\.js(?:\?[^"]*)?("[^>]*>)', rf'\g<1>{prefix}assets/js/site.js?v={VERSION}\2', text)
    if not count:
        text = text.replace('</body>', f'  <script src="{prefix}assets/js/site.js?v={VERSION}" defer></script>\n</body>')
    path.write_text(text)
    print(name)
