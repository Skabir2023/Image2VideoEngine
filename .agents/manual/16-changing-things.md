# Changing things — what else must move

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

| If you change | Also change |
| --- | --- |
| A scene's duration or frame count | `frames` in that film's `scenes.py`, `FRAMES` **and `TOTAL`** in its `audio/build_final.py`, its `plan/TIMELINE.md`; `index.html` is regenerated |
| A new scene-table field | `tools/scene_builder.py` (it must read it), its docstring, and [the scene table](08-composition.md) — never the generated `compositions/*.html`, which is rewritten |
| Script, voice take or `speed` | re-transcribe, then every `*_at` time in `scenes.py`, cut positions in `plan/TIMELINE.md` |
| A still | keep the filename, or change `still` in `scenes.py` |
| Scene slugs or their number | `scenes` in that project's `meta.json` (the render reads it), the layers in `index.html` |
| The output filename | `output` in `meta.json` — the 5–11 word title, the same words as the caption's first line |
| Sound levels | `START_*` / `BED_*` / `DUCK*` / `ROAR_*` in `audio/build_final.py`, the sound section of `plan/TIMELINE.md` |
| A sound file, its slice or a kit level | `sound/kit.json` (the menu) and `START_*` / `BED_*` / `ROAR_*` / `HIT_*` in **every** film's `audio/build_final.py`, since the kit is copied not imported; then `python3 tools/sound.py check` and re-mix the films that use it |
| A caption, title or hashtag after `queue` | that row's `title`/`description`/`hashtags` **and** its `caption` in `data.csv`, before `schedule` books it |
| `social.account` or `platform` in `meta.json` | nothing else, but the account must exist and be connected in BrightBean; `uploaded.csv` keeps the old channel's history |
| A queued film's file | re-render it (a new file has a new fingerprint, so it is allowed) and point the row's `video` at it; never rename or move a render after queueing |
| Anything in the engine (`assets/`, `sound/`, `tools/`) | every project at once — check the reference film still renders before moving on |
