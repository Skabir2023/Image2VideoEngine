#!/usr/bin/env bash
# Full rebuild of one video project. Everything runs from the engine root, and the project's
# meta.json says which scenes to render, at what frame rate, into which output name.
#   1. rebuild the mix (voice + bed + accents) with the project's audio/build_final.py
#   2. render each scene, in meta.json order, into <project>/renders/cut/
#   3. join them without re-encoding
#   4. mux the mix onto the picture
#   5. scan the finished file for a blank first frame, black frames and one-frame pops
# Usage: bash tools/render-all.sh video-projects/<page>/<film>   (npm run render -- video-projects/<page>/<film>)
set -euo pipefail
cd "$(dirname "$0")/.."                       # engine root; every path below is relative to it

PROJ=${1:?usage: tools/render-all.sh video-projects/<page>/<film>}
PROJ=${PROJ%/}
[ -f "$PROJ/meta.json" ] || { echo "no meta.json in $PROJ" >&2; exit 1; }

# meta.json is the project's build contract: output name, frame rate, scene order
eval "$(python3 - "$PROJ" <<'PY'
import json, shlex, sys
m = json.load(open(f"{sys.argv[1]}/meta.json"))
print(f'OUT={shlex.quote(m["output"])}')
print(f'FPS={m["fps"]}')
print('SCENES=(' + ' '.join(shlex.quote(s) for s in m["scenes"]) + ')')
PY
)"

echo "== 1/5 mix"
python3 "$PROJ/audio/build_final.py"

echo "== 2/5 render ($FPS fps)"
mkdir -p "$PROJ/renders/cut"
: > "$PROJ/renders/cut/concat.txt"
for s in "${SCENES[@]}"; do
  echo "   $s"
  npx hyperframes render -c "$PROJ/compositions/$s.html" -o "$PROJ/renders/cut/$s.mp4" \
    --fps "$FPS" --quality high --video-frame-format png
  echo "file '$s.mp4'" >> "$PROJ/renders/cut/concat.txt"
done

echo "== 3/5 join"
ffmpeg -y -v error -f concat -safe 0 -i "$PROJ/renders/cut/concat.txt" -c copy "$PROJ/renders/cut/picture.mp4"

echo "== 4/5 mux"
ffmpeg -y -v error -i "$PROJ/renders/cut/picture.mp4" -i "$PROJ/audio/final-audio.wav" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart "$PROJ/renders/$OUT.mp4"

echo "== 5/5 check"
python3 tools/scan.py "$PROJ/renders/$OUT.mp4"
echo "done: $PROJ/renders/$OUT.mp4"
