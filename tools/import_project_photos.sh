#!/usr/bin/env bash
# Optimize project photos into images/<slug>/ at web-appropriate size.
#
#   tools/import_project_photos.sh <source-dir> <slug>
#
# Every JPEG/PNG in <source-dir> is downscaled to 1600px on its long edge and
# written as a quality-tuned JPEG. Uses sips, which ships with macOS — no
# dependencies. Filenames are preserved, so name the source files to match the
# `project_images` entries in tools/towns.json before running.
#
# Photos are only picked up by the site if the filename matches an entry in
# towns.json; the generator skips anything it can't find.

set -euo pipefail

SRC="${1:?usage: import_project_photos.sh <source-dir> <slug>}"
SLUG="${2:?usage: import_project_photos.sh <source-dir> <slug>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/images/$SLUG"

[ -d "$SRC" ] || { echo "error: source dir not found: $SRC" >&2; exit 1; }
mkdir -p "$DEST"

MAX_EDGE=1600
count=0

shopt -s nullglob nocaseglob
for f in "$SRC"/*.jpg "$SRC"/*.jpeg "$SRC"/*.png; do
    base="$(basename "${f%.*}").jpg"
    out="$DEST/$base"
    cp "$f" "$out.tmp"
    sips --setProperty format jpeg \
         --setProperty formatOptions 72 \
         --resampleHeightWidthMax "$MAX_EDGE" \
         "$out.tmp" --out "$out" >/dev/null
    rm -f "$out.tmp"
    size=$(du -h "$out" | cut -f1)
    dims=$(sips -g pixelWidth -g pixelHeight "$out" | awk '/pixel/ {printf "%s", $2 " "}')
    echo "  $base  (${dims%% }, $size)"
    count=$((count + 1))
done
shopt -u nullglob nocaseglob

echo
echo "Imported $count photo(s) into images/$SLUG/"
echo "Next: python3 tools/build_town_pages.py   # then review and commit"
