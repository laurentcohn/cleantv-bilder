# CleanTV Bilder

Fotos für die ruhige Hintergrund-Diashow von CleanFrame auf dem Samsung-TV. Der TV holt neue Bilder selbst, eine Neuinstallation ist nicht nötig.

> **Dieses Repo ist öffentlich.** Nur Fotos hochladen, die jeder sehen darf und an denen du die Rechte hast.

## Foto hinzufügen

Immer über das Skript, nie direkt auf github.com. Das Skript entfernt GPS-Ort, Gerät und Datum aus den Fotos, bevor sie öffentlich werden.

```sh
tools/add.sh ~/Desktop/Matterhorn.heic ~/Desktop/Zugersee.jpg
tools/add.sh --name abendrot-zugersee ~/Desktop/IMG_1234.HEIC
```

Das Skript dreht die Bilder richtig, verkleinert sie auf höchstens 3840 px und speichert sie als JPEG in `fotos/`. Danach committet und pusht es. Beim ersten Mal richtet es eine Python-Umgebung ein (`.venv`).

## Gute Fotos für den TV

- Querformat, möglichst 16:9, mindestens 2400 × 1350 px
- JPEG, HEIC (iPhone) oder PNG
- Ruhige Motive: Landschaft, Berge, Wasser, Himmel. Wenig Text, keine Personen.
- Ein ruhiger Bereich unten und oben links hilft, dort liegen Apps und Uhr.

## Was danach passiert

Nach jedem Push bereitet die GitHub Action «Bilder veröffentlichen» die Fotos auf (`tools/build.py`): Hintergrund in 1920 × 1080, Vorschaubild, die Glas-Materialien von CleanFrame und `manifest.json`. Sie veröffentlicht alles auf GitHub Pages: https://laurentcohn.github.io/cleantv-bilder/manifest.json

CleanFrame auf dem TV holt das Manifest beim Start und danach stündlich. Die Fotos laufen in der ruhigen Diashow, sobald niemand bedient, und lassen sich unter *Einstellungen → Hintergrund* auch fest wählen. Der Name im TV kommt aus dem Dateinamen (`abendrot-zugersee.jpg` → «Abendrot zugersee»).

Lokal testen: `.venv/bin/pip install -r tools/requirements.txt && .venv/bin/python tools/build.py` (Ergebnis in `site/`, nicht im Repo).

## Entfernen

Datei in `fotos/` löschen, committen, pushen. Achtung: In der Git-Geschichte bleibt das Bild trotzdem sichtbar.
