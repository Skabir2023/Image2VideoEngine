# The pipeline — do not reorder

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

This is steps 3–5 of [the working procedure](03-working-procedure.md) at film detail; it is the
same order, not a second one.

| # | Step | Output |
| --- | --- | --- |
| 1 | Pick a car, one 3-second shocking fact, score it | `plan/VIRAL.md` |
| 2 | Fact-check year, make/model/trim, engine, production, price/speed | `plan/FACTCHECK.md` |
| 3 | Write the spoken script to the word budget | `plan/SCRIPT.md` |
| 4 | Plates, one per 3 s (the six fixed angles first), native 1080×1920, no living beings | `stills/*.png` |
| 5 | One Kokoro take of the paragraph, `speed: 1.2` | `audio/paragraph/line-01-v120.wav` |
| 6 | Cap every pause at
0.22 s, then measure word times on the refined file | `audio/paragraph/transcript.json` |
| 7 | Fill the scene table: durations, frames, stills, camera, text, word times | `scenes.py` + `tools/scene_builder.py` → `compositions/*.html` |
| 8 | Build the mix from the kit's four slots: voice, start, bed ducked to the words, closing roar, one hit under the card | `audio/build_final.py` → `audio/final-audio.wav` |
| 9 | Render, join, mux, scan | `renders/<title>.mp4` |
| 10 | Write, score (80+) and gate the caption from `MASTER PROMPT.md` | the `queue` row in `data.csv` |

Paths in this manual are inside the film's folder (`video-projects/<page>/<film>/…`) unless they
start with `assets/`, `sound/` or `tools/`, which belong to the shared engine.

**The scripts do not read `transcript.json` at build time.** It is the measurement record; the
word times are copied by hand into the scene table and the sound build. Editing the JSON alone
changes nothing — see [Timing law](07-timing-law.md).

## Delivery name

A finished film is named after its title, and that title is **5–11 words** — the same words as the
first line of its caption (punctuation simplifies for a filename: `—` becomes `-`). Five is the
floor, not the target: the title has to name the year, make and model and still land as a
headline, which takes seven to eleven. Folders keep slugs; the file the person receives and posts
is the title, in clear words:

```
renders/1957 Cadillac Eldorado Brougham - Handbuilt.mp4
```

`meta.json` `output` holds that exact name (spaces and all — every command quotes it), so
`npm run render` writes the right file and a re-render never drops back to a working name.
`output` is therefore **set when the caption is written**, not at the start of the build. Never
deliver a working name — `final`, `v2`, `part2`, `reel-final`, a date, a version: the file name is
what the page posts, and it is chosen before the film is shown, never after.

