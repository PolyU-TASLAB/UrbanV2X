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
      <button class="site-navigation-toggle" type="button" data-nav-toggle aria-label="Toggle navigation" aria-expanded="false" aria-controls="site-navigation-menu"><span aria-hidden="true"></span></button>
      <nav class="site-navigation-links" id="site-navigation-menu" data-nav-menu aria-label="Main navigation">
{chr(10).join(links)}
      </nav>
    </div>
  </header>'''
    text = path.read_text()
    text, count = re.subn(r'  <header\b[^>]*>.*?</header>', header, text, count=1, flags=re.S)
    assert count == 1, name
    text = re.sub(r'\s*<link rel="stylesheet" href="[^"]*assets/css/navigation.css">', '', text)
    text = text.replace('</head>', f'  <link rel="stylesheet" href="{prefix}assets/css/navigation.css">\n</head>')
    if not re.search(r'<script\b[^>]*src="[^"]*assets/js/site.js"', text):
        text = text.replace('</body>', f'  <script src="{prefix}assets/js/site.js" defer></script>\n</body>')
    path.write_text(text)
    print(name)
