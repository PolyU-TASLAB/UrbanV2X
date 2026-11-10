"""Check local asset links, video loading rules and publication size budgets."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'sensors/index.html', 'calibration/index.html',
         'download/index.html', 'positioning/index.html', '404.html']


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.videos = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ['src', 'href', 'poster', 'data-src', 'data-poster']:
            if attrs.get(key):
                self.links.append(attrs[key])
        if attrs.get('srcset'):
            self.links.extend(item.strip().split()[0] for item in attrs['srcset'].split(','))
        if tag == 'meta' and attrs.get('property') == 'og:image':
            self.links.append(attrs['content'])
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])
        if tag == 'video':
            self.videos.append(attrs)


def local_path(owner, url):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    path = (owner.parent / unquote(parts.path)).resolve()
    assert path.is_relative_to(ROOT), f'Outside site: {owner}: {url}'
    if path.is_dir():
        path /= 'index.html'
    assert path.is_file(), f'Missing asset: {owner.relative_to(ROOT)}: {url}'
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracked', action='store_true', help='Require assets in the Git index')
    parser.add_argument('--asset-list', type=Path, help='Write publication asset paths')
    args = parser.parse_args()
    assets = {ROOT / name for name in PAGES}
    # Data URLs assembled at runtime by positioning.js.
    assets.update(ROOT / f'assets/data/{name}.json' for name in ['positioning-timeline', 'hkstp-map'])
    for name in PAGES:
        owner = ROOT / name
        page = Page()
        page.feed(owner.read_text())
        for url in page.links:
            path = local_path(owner, url)
            if path:
                assets.add(path)
        for url in page.images:
            path = local_path(owner, url)
            if path:
                assert path.stat().st_size <= 1024 ** 2, f'Inline image exceeds 1 MiB: {path.name}'
        for video in page.videos:
            assert video.get('preload') == 'none', f'Video preloads in {name}'
            assert not video.get('src'), f'Use lazy data-src in {name}'
            path = local_path(owner, video['data-src'])
            limit = 10 if video.get('id') == 'full-film' else 1.2
            assert path.stat().st_size <= limit * 1024 ** 2, f'Video exceeds {limit} MiB: {path.name}'
    for owner in list(assets):
        if owner.suffix == '.css':
            content = owner.read_text()
            assert 'fonts.googleapis.com' not in content, 'External render-blocking font stylesheet'
            for url in re.findall(r'url\([\'"]?([^\)\'\"]+)', content):
                path = local_path(owner, url)
                if path:
                    assets.add(path)
    relative = sorted(path.relative_to(ROOT).as_posix() for path in assets)
    if args.tracked:
        tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
        missing = set(relative) - tracked
        assert not missing, f'Assets not staged: {sorted(missing)}'
    if args.asset_list:
        args.asset_list.write_text('\n'.join(relative) + '\n')
    print(f'{len(PAGES)} pages: asset links and loading budgets passed; {len(relative)} referenced files.')


if __name__ == '__main__':
    main()
