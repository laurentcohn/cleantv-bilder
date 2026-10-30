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

## Entfernen

Datei in `fotos/` löschen, committen, pushen. Achtung: In der Git-Geschichte bleibt das Bild trotzdem sichtbar.
