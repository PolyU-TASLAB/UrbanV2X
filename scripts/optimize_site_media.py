"""Create web encodes from original media, preserving the full frame and duration."""
import argparse
from pathlib import Path
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--film-source', type=Path, default=ROOT / 'assets/video/urbanv2x-full-film.mp4')
    args = parser.parse_args()
    original = Image.open(ROOT / 'assets/img/calibration.png').convert('RGB')
    for width in [640, 1280, 1760]:
        image = original.copy()
        image.thumbnail((width, width))
        image.save(ROOT / f'assets/previews/vehicle-platform-{width}.webp',
                   format='WEBP', quality=85, method=6)
    if not args.film_source.is_file():
        parser.error('Provide the original presentation with --film-source; it is retained locally.')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.film_source),
                    '-vf', 'scale=1280:-2', '-c:v', 'libx264', '-preset', 'slow',
                    '-crf', '25', '-maxrate', '2200k', '-bufsize', '4400k',
                    '-pix_fmt', 'yuv420p', '-threads', '4', '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart', str(ROOT / 'assets/video/urbanv2x-film-web.mp4')], check=True)


if __name__ == '__main__':
    main()
