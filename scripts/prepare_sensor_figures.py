"""Copy the two user-selected sensor images without changing their contents."""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets/previews'
FIGURES = {
    'sensor-architecture.jpg': '20261110-223054.jpg',
    'sensor-onboard.jpg': '20261110-223919.jpg',
}

for name, source in FIGURES.items():
    target = OUTPUT / name
    shutil.copyfile(ROOT / source, target)
    print(f'{target.name}: {target.stat().st_size:,} bytes')

manifest = OUTPUT / 'sources.json'
sources = json.loads(manifest.read_text())
names = set(FIGURES) | {'sensor-platform.webp', 'sensor-layout.webp', 'sensor-system.webp'}
sources = [entry for entry in sources if entry['asset'] not in names]
for name, source in FIGURES.items():
    sources.append({
        'asset': name,
        'source': 'UrbanV2X/' + source,
        'script': 'scripts/prepare_sensor_figures.py',
        'notes': 'User-supplied image copied byte-for-byte. Original annotations, dimensions and composition retained.',
    })
manifest.write_text(json.dumps(sources, indent=2) + '\n')
