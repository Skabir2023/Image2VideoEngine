# templates/

A template here is a **film skeleton**: the files a new film folder starts from, so step 2 of
`AGENTS.md` stops being "copy a sibling film and delete the car out of it".

```
templates/
  film/                 ← the only structure this engine makes: 1080×1920, scene table, generated compositions
    template.json       ← the manifest tools/new_film.py reads
    meta.json           ← placeholders, filled by the scaffolder
    scenes.py           ← a guarded skeleton: it refuses to build until it carries measurements
```

```bash
python3 tools/new_film.py --list
python3 tools/new_film.py video-projects/vintage-motor-house/1959-cadillac-fins \
  --title "1959 Cadillac Eldorado: The Biggest Fins Ever Built"

Classic Card Reel        1080x1920  templates/film
                         A page film: 1080x1920 vertical, one plate per 3 s, scenes generated from a data-only table by tools/scene_builder.py.
```

**Every template is named.** The `name` in its `template.json` is what a person selects
(`--template "Classic Card Reel"`), what `--list` prints, and what the scaffold reports back; the
folder is only its address. The scaffolder refuses a manifest with no `name`, and refuses two
templates sharing one, because a library where two entries answer to the same word cannot be
picked from. The name is a name, not a slug: `Classic Card Reel`, not `classic-card-reel`.

## Why these and not HyperFrames'

HyperFrames ships two examples — `blank` and `warm-grain` — and its registry holds 448 blocks and
components. **None of them matches this project**, and adopting one would break the pipeline rather
than improve it:

| | HyperFrames `warm-grain` | This engine |
| --- | --- | --- |
| Canvas | 1920×1080 landscape | 1080×1920 vertical |
| Look | cream paper, grain | `#050506` ground, Anton cards, red accent |
| Build contract | `index.html` edited by hand | `meta.json` + `scenes.py` → `tools/scene_builder.py` |
| Scenes | three hand-written compositions | `ceil(seconds / 3)` generated scenes, one per plate |
| Stills | none | `stills/*.png`, one per 3 s, driven by `BROLL` |
| Gates | `lint` | `lint`, `score.py`, `scan.py`, loudness, caption |

The registry's blocks are in-scene snippets (a chat card, a notification cascade), not project
scaffolds — 210 blocks and 238 components, 12 of them portrait, none of them a film. Copying one in
would leave a project that `render-all.sh` cannot render, because it has no `meta.json`.

**The structure is the template.** `tools/scene_builder.py` plus `assets/` is the engine; a film is
only data. So a template here is the *shape of that data*, not a different look — the page's style
is fixed on purpose (`AGENTS.md` → *Style of this engine*), and every reel has to be recognisable as
coming from the same page.

## Adding a template

Only when it is a genuinely different **structure**, not a different mood:

1. `mkdir templates/<name>/`, add a `template.json`:

   ```json
   {
     "name": "<Template Name>",
     "description": "one line — what structure this produces",
     "canvas": [1080, 1920],
     "dirs": ["compositions", "stills", "audio/paragraph", "audio/sfx", "plan", "qa", "renders"],
     "render": {"meta.json": "meta.json", "scenes.py": "scenes.py"},
     "copy_from": {"audio/build_final.py": "templates/film/audio/build_final.py"}
   }
   ```

   `name` is required and unique. `render` files are copied with `{{PROJECT}}`, `{{PAGE}}`,
   `{{SLUG}}`, `{{FILM}}`, `{{ID}}`, `{{DIR}}` substituted. `copy_from` copies a file that already
   exists rather than forking it — and it points **into `templates/`**, never at a finished film:
   a film's folder is a record of what was delivered, so the next build must not inherit from it
   or chase it when it changes.

2. Keep `tools/scene_builder.py` as the generator. A template that writes its own compositions is
   a second engine, and the two will drift.

3. Run the scaffolder against a scratch path and build one film with it before trusting it.
