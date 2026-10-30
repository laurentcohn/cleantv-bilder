"""Fotos aus fotos/ für CleanFrame aufbereiten: Hintergrund, Vorschau, Glas-Materialien und manifest.json in site/.

Die Materialien folgen den Rezepten von CleanFrame (scripts/build-materials.mjs, docs/assets.md):
gleicher zentrierter 1920×1080-Ausschnitt, gespiegelte Ränder, Weichzeichnen und Sättigung wie CSS-Filter.
Der TV rechnet nichts selbst, er zeigt nur diese JPEGs.
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'fotos'
OUT = ROOT / 'site'
W, H, P = 1920, 1080, 96
RECIPE = 1
INK = np.array([4, 10, 12], dtype=float)


def saturate(a, s):
    """CSS saturate() auf sRGB-Werten (Filter Effects, feColorMatrix saturate)."""
    m = np.array([
        [.213 + .787 * s, .715 - .715 * s, .072 - .072 * s],
        [.213 - .213 * s, .715 + .285 * s, .072 - .072 * s],
        [.213 - .213 * s, .715 - .715 * s, .072 + .928 * s],
    ])
    return np.clip(a @ m.T, 0, 255)


def blur(a, radius):
    """CSS blur(px) entspricht einer Gauss-Unschärfe mit dieser Standardabweichung."""
    image = Image.fromarray(np.uint8(np.clip(np.rint(a), 0, 255)))
    return np.asarray(image.filter(ImageFilter.GaussianBlur(radius)), dtype=float)


def to_linear(a):
    a = a / 255
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)


def to_srgb(a):
    return 255 * np.where(a <= .0031308, 12.92 * a, 1.055 * np.power(np.maximum(a, 0), 1 / 2.4) - .055)


def soft_clip(a):
    """Lichter über 82 % Leuchtdichte weich abfangen, wie im CleanFrame-Rezept."""
    lin = to_linear(a)
    l = lin @ np.array([.2126, .7152, .0722])
    ratio = np.where(l > .82, (.82 + .4 * (l - .82)) / np.maximum(l, 1e-6), 1)
    return np.where((l > .82)[..., None], to_srgb(lin * ratio[..., None]), a)


def save(a, path, quality, subsampling=2):
    Image.fromarray(np.uint8(np.clip(np.rint(a), 0, 255))).save(path, 'JPEG', quality=quality, subsampling=subsampling, optimize=True)


def luma(a):
    return a @ np.array([.2126, .7152, .0722])


def region(a, x0, y0, x1, y1):
    return float(luma(a[y0:y1, x0:x1]).mean())


def name_of(stem):
    words = re.sub(r'-\d+$', '', stem).replace('-', ' ').strip()
    number = re.search(r'-(\d+)$', stem)
    return (words[:1].upper() + words[1:] + (' ' + number.group(1) if number else ''))[:48] or 'Foto'


def build(path, id):
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert('RGB')
    photo_img = ImageOps.fit(image, (W, H), Image.Resampling.LANCZOS, centering=(.5, .5))
    photo = np.asarray(photo_img, dtype=float)
    files = {}

    save(photo, OUT / f'{id}.jpg', 90, 0)
    save(np.asarray(photo_img.resize((512, 288), Image.Resampling.LANCZOS), dtype=float), OUT / f'{id}-thumb.jpg', 85)

    padded = np.pad(photo, ((P, P), (P, P), (0, 0)), mode='symmetric')
    for suffix, radius, sat, quality in [('field-blur', 28, .92, 82), ('field-frost', 42, .92, 82), ('field-clear', 2, 1.06, 86)]:
        field = saturate(blur(padded, radius), sat)[P:P + H, P:P + W]
        if suffix != 'field-clear':
            field = soft_clip(field)
        save(field, OUT / f'{id}-{suffix}.jpg', quality)
        if suffix == 'field-frost':
            panel = Image.fromarray(np.uint8(np.clip(np.rint(field), 0, 255))).resize((320, 180), Image.Resampling.LANCZOS)
            save(np.asarray(panel, dtype=float), OUT / f'{id}-panel.jpg', 85)

    # Sanft (study-soft): unterer Schleier, 14px Unschärfe, Dock-Band ausgleichen, begrenzte Tönung.
    y = np.arange(H, dtype=float)
    t = np.clip((y - 560) / 520, 0, 1)
    alpha = np.where(t <= .7, .42 * t / .7, .42 + .10 * (t - .7) / .3)
    alpha[y < 560] = 0
    base = photo * (1 - alpha[:, None, None]) + INK * alpha[:, None, None]
    soft = saturate(blur(base, 14), 1.12)
    mean = soft[676:908, 96:1824].reshape(-1, 3).mean(axis=0)
    soft = soft * .65 + mean * .35
    high = float(np.percentile(luma(soft[720:908:4, 112:1808:4]), 95))
    tint = max(.28, min(.6, (high - 94) / (high - 8.87))) if high > 8.87 else .28
    soft = soft * (1 - tint) + INK * tint
    save(soft, OUT / f'{id}-study-soft.jpg', 94)

    # Einfache Einordnung statt eigener Farbpalette: helle Zonen bekommen den stärkeren «mist»-Schutz.
    tl, tr, br = region(photo, 100, 40, 760, 200), region(photo, 1100, 20, 1900, 200), region(photo, 1100, 780, 1900, 980)
    dock = region(photo, 96, 676, 1824, 908)
    whole = float(luma(photo).mean())
    entry = {
        'id': id, 'name': name_of(id), 'v': hashlib.sha256(path.read_bytes() + bytes([RECIPE])).hexdigest()[:12],
        'tone': 'light' if whole > 120 else 'dark',
        'ut': {'tr': 'mist' if tr > 110 else 'light', 'br': 'mist' if br > 110 else 'light'},
        'frostVeil': .44 if dock > 160 else .30 if dock > 110 else .20,
        'clockMist': tl > 110,
        'softTint': round(tint, 4),
    }
    print(f'{path.name} → {id}: Ton {entry["tone"]}, oben rechts {entry["ut"]["tr"]}, unten rechts {entry["ut"]["br"]}, Schleier {entry["frostVeil"]}')
    return entry


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    photos = sorted(p for p in SRC.iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png'))
    walls, seen = [], set()
    for path in photos:
        id = re.sub(r'[^a-z0-9]+', '-', path.stem.lower()).strip('-')[:40] or 'foto'
        if id in seen:
            sys.exit(f'Doppelter Name: {id}')
        seen.add(id)
        walls.append(build(path, id))
    manifest = {'recipe': RECIPE, 'size': [W, H], 'walls': walls}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n')
    (OUT / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>CleanTV Bilder</title><p>Bilder für CleanFrame. Daten: <a href="manifest.json">manifest.json</a></p>\n')
    print(f'{len(walls)} Bilder aufbereitet in site/')


if __name__ == '__main__':
    main()
