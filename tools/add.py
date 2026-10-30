"""Fotos fürs Repo aufbereiten: drehen nach EXIF, auf max. 3840 px verkleinern, als JPEG ohne Metadaten (kein GPS) nach fotos/ schreiben."""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'fotos'
MAX_SIDE = 3840
MIN_WIDTH = 2400


def slug(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'foto'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--name', help='Dateiname ohne Endung (nur bei einem Foto)')
    args = parser.parse_args()
    if args.name and len(args.files) > 1:
        sys.exit('--name geht nur mit einem Foto.')
    written = []
    for path in args.files:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert('RGB')
        if image.width < image.height:
            print(f'Hinweis: {path.name} ist Hochformat und wird auf dem TV stark beschnitten.')
        if image.width < MIN_WIDTH:
            print(f'Hinweis: {path.name} ist nur {image.width} px breit (empfohlen ab {MIN_WIDTH}).')
        image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
        target = OUT / (slug(args.name or path.stem) + '.jpg')
        n = 2
        while target.exists():
            target = OUT / (slug(args.name or path.stem) + f'-{n}.jpg')
            n += 1
        # Neu kodiert ohne exif/icc/xmp: keine Ortsdaten, kein Gerät, kein Datum.
        image.save(target, 'JPEG', quality=92, optimize=True, progressive=True)
        written.append(target)
        print(f'{path.name} → fotos/{target.name} ({image.width}×{image.height})')
    return written


if __name__ == '__main__':
    main()
