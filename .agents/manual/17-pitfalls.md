# Known pitfalls of this engine

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

Traps that have no other page. Where a rule already lives elsewhere, this file carries the pointer
at the end instead of a second copy of the rule.

- **16:9 stills cropped to 9:16 cut the car in half.** Generate vertical natively at 1080×1920.
- `assets/broll.js` deliberately re-decodes the plate and redraws on `hf-seek`. Removing either
  gives a blank first frame or a plate one frame late — leave them alone.
- **Scenes are opened from the engine root**, so their `assets/…` refs hit the shared library and
  their stills are addressed as `video-projects/<page>/<film>/stills/<file>.png`. The film's own
  `index.html`, by contrast, uses project-relative refs (`compositions/…`, `audio/…`) — that is
  what the linter and the render pre-flight resolve against the project folder.
- Rebuilding the scenes (`python3 tools/scene_builder.py video-projects/<page>/<film>`) rewrites
  that project's `compositions/*.html` and `index.html`. Hand edits made in those files are lost —
  put the film's own changes in its `scenes.py`, and anything that should hold for every film in
  `tools/scene_builder.py` or `assets/`.
- `renders/cut/` is disposable — it is regenerated on every render. `audio/final-audio.wav` is
  not: if it is missing, the mux step fails, so run the mix again.
- `magick` is not installed. Use `ffmpeg` for scaling, tiling and contact sheets.
- `tools/scan.py` takes **file paths**, one or more, from the engine root
  (`python3 tools/scan.py video-projects/<page>/<film>/renders/<out>.mp4`); `.mp4` is added if you
  leave it off. It no longer guesses a project.
- 1080×1920 PNGs are large; downscale before attaching them anywhere with a size limit.
- `uploaded.csv` is the truth for what is booked. Never hand-edit its `status`, `post_id` or
  `post_url` — `sync` overwrites those from the API. Correct a caption in `data.csv` *before*
  `schedule`, never after.

## Where the rest of the traps live

- **A closed Chrome, and Flow with no project, are states — not broken routes.** Run
  `python3 tools/brain.py` before diagnosing either: [The two brains](04-the-two-brains.md).
- **Silence detection is not sync**; a word time is measured, never estimated, and a cut lands ~65
  ms before the first word: [Timing law](07-timing-law.md).
- **A number printed flat reads as a caption; a number counted out reads as a fact.** Every figure
  goes through `TX.roll`, `0.75 s` +, seeded: [Numbers law](08-composition.md#numbers-law).
- **A filename is not a sound, a licence or a level.** `01 Boom.wav` decays for six seconds
  instead of hitting, the SFX pack peaks above 0 dBFS, the engines spread `−33` to `−11 dBFS`,
  `SFX Sound Effects/` mostly has no source, `-shortest` eats the tail and the AAC mux lifts true
  peak — all of it, with the numbers to keep, in [Sound law](09-sound-law.md).
- **The workbooks only update where they exist, and a Tracker row is never invented** — [The
  workbooks](15-publishing.md#the-workbooks), [The two spreadsheets](18-workbooks.md).
- **There are no copies of renders** — the row points at the film in its own `renders/`: [What a
  page holds](15-publishing.md#what-a-page-holds).
- **`Used? = Yes`, 90 days, a new row at the bottom** — never overwrite the old row: [Choosing the
  next car](14-choosing-the-next-car.md).

---
