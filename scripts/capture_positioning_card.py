"""Render the dataset card from the recorded positioning data and cached OSM map."""
import argparse
import base64
import io
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FRAME = 281  # A moving epoch with a recorded range to the mapped UWB anchor.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://localhost:8080/positioning/')
    args = parser.parse_args()
    data = json.loads((ROOT / 'assets/data/positioning-timeline.json').read_text())
    frame = data['frames'][FRAME]
    assert frame['ranges'][data['uwb_ids'].index(data['anchor']['id'])] is not None
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome',
                                    headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1200, 'height': 950})
        page.goto(args.url, wait_until='domcontentloaded')
        page.wait_for_function('!!window.positioningScene')
        page.evaluate('window.positioningScene.stop()')
        page.add_style_tag(content='#positioning-canvas{width:960px!important;height:600px!important}')
        page.evaluate('(frame) => { window.positioningScene.setYaw(-.32); window.positioningScene.render(frame); }', FRAME)
        png = page.locator('#positioning-canvas').evaluate('(canvas) => canvas.toDataURL().split(",")[1]')
        browser.close()
    output = ROOT / 'assets/previews/positioning-card.webp'
    Image.open(io.BytesIO(base64.b64decode(png))).convert('RGB').save(output, quality=88, method=6)
    print(f'{output.name}: {output.stat().st_size:,} bytes; timeline frame {FRAME}, UTC {frame["utc"]}')


if __name__ == '__main__':
    main()
