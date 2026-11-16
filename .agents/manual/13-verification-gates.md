# Verification gates — never show a film before these pass

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

0. `python3 tools/score.py video-projects/<page>/<film>` → **PASS**. The 80 gate, the fact sheet,
   the five beats with a real revelation, the word budget against the measured voice,
   `ceil(seconds / 3)` distinct plates, and every card landing **on a word start rather than
   inside one** are all checked here, before anything renders. The reveal check reads `scenes.py`
   and the film's `transcript.json`: within `±0.10 s` of a word start or clear of every word span
   is legal, mid-word is a FAIL, and a card under `0.15 s` from its scene edge warns. A film under
   80 is not built, so this gate runs first.
1. `npm run lint -- video-projects/<page>/<film>` → **0 errors, 0 warnings**.
2. `npm run check -- video-projects/<page>/<film>/renders/<out>.mp4` → `frame0_blank: false`,
   `black_frames: []`, `one_frame_pops: []`. `hard_jumps` are expected **only** at the scene seams
   (reference: frames 253–260, 564–570, 784–789, 877–884, 975–981); a jump anywhere else is a
   fault.
3. **Look at the frames yourself.** Contact sheet, then the seams and both ends:

```bash
ffmpeg -y -v error -i video-projects/<page>/<film>/renders/<out>.mp4 \
  -vf "select='eq(n,0)+eq(n,120)+eq(n,300)+eq(n,470)+eq(n,790)+eq(n,1115)',scale=360:-1,tile=3x2" \
  -frames:v 1 video-projects/<page>/<film>/qa/final-sheet.jpg
```

4. **Prove every reveal lands on its word** — the sheet the contact sheet cannot give you. Sample
   each `kick_at` / `b1_at` / `b2_at` / `lab_at` / `foot_at` at the frame of its word and again
   `0.30 s` later, and read the tiles: the card is only **just entering** on the first (faint, or
   mid-slam) and **settled** on the second, a roll is still spinning then locked
   (`16,969 → 14,000`), and nothing is fully on screen before its word or changes mid-word. Times
   in `scenes.py` are **absolute film time** (the builder subtracts the scene start), so no offset
   is added here:

```bash
python3 - <<'PY'
import importlib.util, json, subprocess
from pathlib import Path
proj = Path("video-projects/<page>/<film>")
out = json.loads((proj / "meta.json").read_text())["output"]
spec = importlib.util.spec_from_file_location("s", proj / "scenes.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
end = sum(sc["frames"] for sc in m.SCENES)
frames = []
for sc in m.SCENES:
    for k in ("kick_at", "b1_at", "b2_at", "lab_at", "foot_at"):
        if sc.get(k) is not None:
            frames += [round(sc[k] * m.FPS), round((sc[k] + 0.30) * m.FPS)]
frames = sorted({n for n in frames if 0 <= n < end})
cols, rows = 6, -(-len(frames) // 6)
mp4 = proj / "renders" / (out if out.endswith(".mp4") else out + ".mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-vf",
                "select='" + "+".join(f"eq(n,{n})" for n in frames) + "',scale=180:-1,"
                f"tile={cols}x{rows}", "-frames:v", "1", str(proj / "qa" / "check-reveals.jpg")], check=True)
print(len(frames), "frames ->", proj / "qa" / "check-reveals.jpg")
PY
```

5. Audio: `-14.2 LUFS ±0.3`, peak ≤ −1.3 dBFS, voice clearly above the bed, no rev touching a
   spoken word. Speech section measured on its own.
6. Facts, word count, caption format re-read against `MASTER PROMPT.md` before sending.
7. The file is named after its title — **5–11 words**, the same words as the caption's first line,
   `meta.json` `output` the same ([Delivery name](06-pipeline.md#delivery-name)). Count the words
   out loud, not by eye: does it name the car and still make a stranger stop? If not, rewrite it.

Report checks that failed or could not run. Never call a film verified because it compiled.

---
