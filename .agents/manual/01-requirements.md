# Requirements

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

- **Node 22+**, **ffmpeg**, **python3** (with numpy, for `tools/scan.py`), **Google Chrome**
  (HyperFrames drives it headless through `puppeteer-core`).
- Dependencies are already installed in `node_modules/` (`hyperframes` 0.7.109). If that folder is
  missing, run `npm install` once (needs internet).
- **Nothing is fetched at render time.** All images, fonts and sounds are local files. The only
  network steps are image generation (outside this folder) and the optional local Kokoro voice
  server on `http://localhost:8880`.
- **What the repo carries.** The engine, `.agents/manual/` (this manual, one file per section),
  `assets/` (fonts included), `sound/` (the whole library), `templates/`, `tools/`, the page's
  rules, both workbooks, `data.csv` / `uploaded.csv`, and each film's text sources — `meta.json`,
  `scenes.py`, `compositions/`, `plan/`, the transcripts and every `stills/<shot>.images.json`.
  Generated media does not travel: `node_modules/`, `.env`, `stills/*.png`, `renders/*.mp4` and
  the voice WAVs are ignored, so a fresh clone runs `npm install`, re-creates `.env`, re-shoots
  plates from the recorded prompts and re-takes the voice. Commit the workbooks and both CSVs with
  the rest of a run — they are the calendar and the ledger, not scratch state.
