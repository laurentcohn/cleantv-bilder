#!/bin/bash
# Fotos ohne Metadaten ins Repo bringen und hochladen.
#   tools/add.sh ~/Desktop/Matterhorn.heic ~/Desktop/See.jpg
#   tools/add.sh --name abendrot-zugersee ~/Desktop/IMG_1234.HEIC
#   NO_PUSH=1 tools/add.sh …   → nur aufbereiten, nicht committen
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv"
[[ $# -gt 0 ]] || { sed -n 2,5p "$0"; exit 2; }

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Richte Python-Umgebung ein (einmalig) …"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --disable-pip-version-check -r "$ROOT/tools/requirements.txt"
fi

"$VENV/bin/python" "$ROOT/tools/add.py" "$@"

[[ "${NO_PUSH:-}" == 1 ]] && exit 0
cd "$ROOT"
git add fotos
git diff --cached --quiet && { echo "Nichts Neues."; exit 0; }
git commit --quiet -m "Fotos hinzufügen: $(git diff --cached --name-only | sed 's|fotos/||' | paste -sd ', ' -)"
git push --quiet
echo "Hochgeladen. Der TV holt die neuen Bilder automatisch (spätestens nach einer Stunde)."
