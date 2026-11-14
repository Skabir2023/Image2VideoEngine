# AGENTS.md — image2videoEngine

This folder is the **reel engine** for the Facebook page *Vintage Motor House*: vertical
(1080×1920, 60 fps) narrated vintage-car reels made from six AI stills, HyperFrames motion
graphics cut to the spoken words, and a real engine recording for sound.

The engine is shared and never copied: one `node_modules`, one set of fonts, one stage, one
sound library. Under `video-projects/` the first level is the **page**, the second is the
**film**: one folder per Facebook page, one folder per film inside it. The page folder holds what
belongs to the channel — the posting rules, the workbooks, the queue — and each film folder holds
only that film's pictures, voice, scenes, plan and render.

```
image2videoEngine/                    ← the engine. Run every command from here.
  assets/                             stage.js, broll.js, text.js, kit-config.js, fonts.css, gsap, fonts/
  sound/engines/                      shared engine recordings + licences
  tools/                              scene_builder.py, render-all.sh, scan.py, meta.py, publish.py + brightbean.py + excel.py
  video-projects/
    vintage-motor-house/              ← the page (the Facebook channel)
      MASTER PROMPT.md                the posting rules, binding for every film on the page
      Vintage-Motor-House-*.xlsx      the page's calendar: 312 cars + the Tracker
      data.csv / uploaded.csv         the page's queue and ledger
      1969-ford-mustang-boss-429/     ← a film: the reference build (18.6 s, 1080×1920)
      1957-cadillac-eldorado-brougham/  ← a film (20.0 s, 1920×1080)
        meta.json scenes.py index.html compositions/ stills/
        audio/ plan/ qa/ renders/
```

`video-projects/vintage-motor-house/1969-ford-mustang-boss-429/` is the **reference build**: one
finished film, its sources, its measurements and its plan. Every other car is a new folder at the
same depth, made the same way. A second page (another channel) is a new sibling of
`vintage-motor-house/` with its own rules, workbooks and queue — films never mix across pages.

You are the operator. You pick the car, check the facts, build the six scenes, make the voice,
mix the sound, render, verify, and write the caption. Then, once they approve that film, you
queue it and book it on the page. The person you work with is a creator: they name a car and get
a video plus a caption. Never ask them to edit code, run commands or choose between libraries —
decide, build, show. Work in the order of `## The working procedure` below, in batches of ten,
and do not skip a step because a film looks easy.

---

## Read in this order before touching anything

0. This file, top to bottom — the layout, the commands, the working procedure, the laws.
   `## The working procedure` is the order every batch runs in; nothing later in this file
   replaces it.
1. `README.md` — the commands and the folder map, in plain words.
2. `video-projects/vintage-motor-house/MASTER PROMPT.md` — the posting rules. **Binding for
   every reel.** Viral-score rubric, fact-check box, the plate cadence and its six fixed
   angles, the no-living-beings rule, and the exact three-line caption format. The `.text` file next to it
   is the same document. Its machine-readable twin is `META PROMPT.md` in the same folder: the
   prompt we actually send to Meta AI, which asks for those rules in one JSON object. If a rule
   ever differs between them, `MASTER PROMPT.md` wins and `META PROMPT.md` is corrected to match.
3. `video-projects/vintage-motor-house/1969-ford-mustang-boss-429/plan/TIMELINE.md` — every
   measured number of the reference build: cuts, word times, frame counts, sound levels.
4. `…/1969-ford-mustang-boss-429/plan/` — VIRAL, FACTCHECK, PROMPTS, SCRIPT, BEATS: how the
   reference build was scored, checked, drawn and written.
5. `video-projects/vintage-motor-house/Vintage-Motor-House-Car-List-300.xlsx` and
   `…-Tracker.xlsx` — the production calendar: which cars are left, what has been posted,
   which angle is due next. Both are read before a batch and written after every film; see
   *What to post next*, and *Publishing a finished film* for the cells `schedule` and `sync`
   fill in themselves.

If these files disagree about a **rule**, this file and `MASTER PROMPT.md` win. If they
disagree about a **number**, that film's `plan/TIMELINE.md` is the measurement and wins.

---

## Requirements

- **Node 22+**, **ffmpeg**, **python3** (with numpy, for `tools/scan.py`), **Google Chrome**
  (HyperFrames drives it headless through `puppeteer-core`).
- Dependencies are already installed in `node_modules/` (`hyperframes` 0.7.109). If that
  folder is missing, run `npm install` once (needs internet).
- **Nothing is fetched at render time.** All images, fonts and sounds are local files.
  The only network steps are image generation (outside this folder) and the optional local
  Kokoro voice server on `http://localhost:8880`.

## Commands

Every command runs from the engine root and takes the **film** folder. The page is
`video-projects/<page>/` (the channel, e.g. `vintage-motor-house`) and the film is the folder
inside it (e.g. `1969-ford-mustang-boss-429`).

```bash
npm run render -- video-projects/<page>/<film>    # mix → every scene → join → mux → frame scan
npm run lint -- video-projects/<page>/<film>      # hyperframes lint — 0 errors, 0 warnings
npm run check -- video-projects/<page>/<film>/renders/<out>.mp4   # blank/black/pop scan

python3 tools/scene_builder.py video-projects/<page>/<film>   # rewrite compositions/*.html + index.html
python3 video-projects/<page>/<film>/audio/build_final.py # rebuild that film's audio/final-audio.wav
```

Publishing (needs `BRIGHTBEAN_API_KEY`) — steps 6–8 of `## The working procedure`, with the detail
under "Publishing a finished film":

```bash
python3 tools/publish.py pick video-projects/<page>                        # the next 10 cars
python3 tools/publish.py queue video-projects/<page>/<film> --title "…" --description "…" \
  --hashtags "…" --car "1969 Ford Mustang Boss 429" --angle "Price / Rarity"
python3 tools/publish.py status video-projects/<page>/<film>     # queue, ledger, last slot
python3 tools/publish.py schedule video-projects/<page>/<film> --dry-run   # the plan, nothing sent
python3 tools/publish.py schedule video-projects/<page>/<film>             # upload, book the row
python3 tools/publish.py sync video-projects/<page>/<film>                 # published? url? sheets
```

`npm run render` reads the project's `meta.json` for the scene order, frame rate and output
name, so a film is rendered by its folder alone. One scene only (fast loop while designing):

```bash
npx hyperframes render -c video-projects/<page>/<film>/compositions/s02-engine.html \
  -o video-projects/<page>/<film>/renders/cut/s02-engine.mp4 \
  --fps 60 --quality high --video-frame-format png
```

Preview the whole film as one timeline: `npx hyperframes preview video-projects/<page>/<film>`
(plays that project's `index.html`). The studio serves the project folder, while the scenes load
the shared library as `assets/…` from the engine root — so a studio preview can look unstyled.
The render is the truth; check stills with single-scene renders instead.

---

## The working procedure — one batch, start to finish

This is the single sequence the project runs on. Every section after it explains one step, and
none of them reorders it. Work in **batches of ten**: one session of building, ten films, ten
posts. A film made on its own, out of order, or "just this once" is the anti-pattern — the Car
List and the Tracker only stay honest when the batch is the unit of work.

### 1. Choose the batch — ten cars, ten angles, ten scores

```bash
python3 tools/publish.py pick video-projects/vintage-motor-house --count 10
```

Ten cars with `Used? = No`, spread across brands and decades — not the ten Cadillacs at the top.
`pick` lists the next ten in row order, so choose across the whole list, not just its first page.

**When the person names or describes something, that is the brief and it outranks the list.**
A car, a fact, a memory, a scene, a feeling — "a barn-find Charger that turned out to be a
Daytona", "something about giant fins and terrible parking" — replaces `pick` for that film: the
car they named is the subject, the detail they gave is a beat of the script, and the feeling they
asked for decides the tone. The brief goes into `META PROMPT.md`'s INPUT block as `Brief: …`, and
Meta returns the five-line `BRIEF` block (heard / car / angle / fact / feeling) before any score.
The fact-check and the 80 gate still apply: a named car that scores under 80 is reported with the
angle that could rescue it, never swapped for a "better" car behind their back. Only an empty
brief falls back to `pick`.

The candidates then go to **Meta AI**, which scores them, names the angle for each, and writes the
script, caption and image prompts (one per 3 s) for the ones that pass — see
[Meta AI does the thinking](#meta-ai-does-the-thinking--the-agent-drives-it). Before any build,
for every candidate:

- the `Car + Angle` pair must not already have a Tracker row — one pair per post, ever;
- a car posted inside **90 days** is out, whatever the angle;
- a car already filmed comes back only with a **different angle**, as a new row at the bottom of
the Car List;
- rotate the six angles so no two neighbours in the batch share one.

Then, in this order: `plan/FACTCHECK.md` (year, model and trim, engine, production, price/speed —
no invented facts) → `plan/VIRAL.md` (the score). **Under 80 the car is not built**: try another
angle, then another car, and leave its row `Used? = No` until a film of it exists.

Step 1 is done when there are ten cars, ten angles, ten scores ≥ 80, and no repeated pair.

### Meta AI does the thinking — the agent drives it

**Meta AI is the default brain for the batch**, through Browser MCP in the person's own signed-in
Chrome — no API key, nothing to pay for. The agent drives it and edits nothing it says. It does
four jobs, always these four: **pick and score the topic, write the script, write every plate
prompt, and write the caption** — a viral title, a long engaging description that talks to the
viewer and ends on a call to action, and four or five hashtags.

**One browser tab, one film.** Every browser step of one film — the batch research, every image
prompt, every download, every retry — runs in **one Browser MCP tab**, opened once and kept for
the whole film. Never open a tab per prompt and never close one between prompts: Meta AI's thread
is the context, and a fresh tab throws it away, which is why the same hero plate came back three
times on the first pass. Use a second tab only when a *different* site is genuinely needed (Flow
instead of Meta AI), never one tab per image. Close the tab once that film's last plate is
downloaded.

```bash
python3 tools/meta.py --check                     # tab list + is the composer there
python3 tools/meta.py ask --prompt-file "video-projects/<page>/META PROMPT.md" \
  --out video-projects/<page>/plan/META-batch-<date>.md --timeout 540
```

- The prompt lives at `video-projects/<page>/META PROMPT.md`. Everything above its
  `<!-- SEND BELOW -->` line is for us; only the text under it is sent. Change nothing but the
  **INPUT** block per batch: candidates, page numbers, posts wanted, angles used so far.
- Meta answers inside `<<<PLAN>>>` … `<<<END>>>`, as one JSON object: every candidate scored
  (with `GO`/`REJECT` and a reason), and for each `GO` a full post — title, description, hashtags,
  script with word count and beat timings, sourced facts, an identity block and one image prompt
  per 3 s of film.
- Browser MCP cuts replies at 10 000 characters, so the JSON must stay compact; the driver reads
  the answer back in slices and refuses to press Enter unless the composer holds the text.
- **Fallback**: if Meta will not answer, the tab is signed out, or the JSON comes back broken, the
  agent does the same work itself in exactly the same shape and says so in `plan/META.md`. The film
  never waits on the tool.
- Meta's facts are **proposals**. Every number is checked against a source before it reaches a
  script, and the check is written into `plan/FACTCHECK.md` (`0 invented facts` still holds).
- Meta AI is a chat window, not the page. **Nothing there can post.** Publishing stays `schedule`,
  behind an explicit yes. Never paste credentials, app passwords or page tokens into it.

These four bits of text are then split into the film folder — `VIRAL.md` (scores and the why),
`SCRIPT.md` (read, beats, caption), `FACTCHECK.md` (sourced numbers), `PLATES.md` (identity block
and six prompts) — so the film carries its own evidence.

### 2. Make the folder and the plan

```bash
PAGE=video-projects/vintage-motor-house
PROJ=$PAGE/1959-cadillac-fins            # slug = year + car, never title words
mkdir -p "$PROJ"/{compositions,stills,audio/paragraph,audio/sfx,plan,qa,renders}
cp $PAGE/1954-mercedes-300sl-gullwing/meta.json "$PROJ"/
cp $PAGE/1954-mercedes-300sl-gullwing/audio/build_final.py "$PROJ/audio"/
```

Edit `meta.json` (page, slug, film, scenes — and clear `status`/`published_at` if the copy came
from a published film), the `SCENES` table, and the numbers at the top of `audio/build_final.py`
(structure stays; it already carries the current sound law). Write the plan as you go:
`FACTCHECK.md`, `VIRAL.md`, `SCRIPT.md` (word budget, and the three-line caption at the end),
`PLATES.md`, `PROMPTS.md`, `BEATS.md`. `TIMELINE.md` is written from measurements at the end, not
up front. One engine, one page folder, one folder per film (30–45 MB); never clone the engine and
never copy the page — the workbooks and the queue would fork.

### 3. Voice first, timing from the voice

One Kokoro take of the whole paragraph (`am_michael`, `speed: 1.2`), then transcribe **that file**
and copy the word times into that film's `scenes.py` and its `audio/build_final.py`. Cuts land on the
transcribed words, never on estimates; a late cut is a re-take, not a stretched clip.

### 4. Plates — one still per 3 seconds

**A new plate every 3 seconds.** `plates = ceil(film_seconds / 3)`: an 18 s film is six plates, a
24 s film is eight, a 27 s film is nine. The six fixed angles come first and in this order —
front ¾ · side · rear · engine bay · interior · wheel — and every plate after them is a close-up
(headlight, badge, wheel, exhaust, gauges, engine detail, steering wheel) placed where a beat needs
a fresh image. No still may run longer than ~3 s; that cadence is the pace of the page. Each prompt
is recorded in `<shot>.images.json`.

Generate them all in the **one** Meta AI tab, one prompt at a time, repeating the identity block
word for word. The prompts come from Meta's post object in `PLATES.md`; the agent may add camera,
light and an empty background (Meta's own prompts run to 45 words) and must never add people,
text, watermarks or invented trim. Look at every plate before anything is built on top of it; if
one drifts, re-shoot just that one.

### 5. Build, render, pass the gates

```bash
npm run render -- $PROJ          # mix → every scene → join → mux → frame scan
npm run lint  -- $PROJ           # 0 errors, 0 warnings
npm run check -- "$PROJ/renders/<title>.mp4"
```

Then the gates in full: lint 0/0, `frame0_blank: false`, `black_frames: []`, `one_frame_pops: []`,
jumps only where the film intends them, −14.2 ±0.3 LUFS with peak ≤ −1.3 dBFS, and the frames
looked at yourself — contact sheet, both ends, every seam. A film that fails a gate is fixed, not
explained, and never shown.

Name it before anyone sees it: **5–11 words**, the caption's first line, in `meta.json` `output`
and on the render. Never a working name, and never a mood line — the file name is the headline
that carries the year, the make, the model and one power word.

### The caption pass — write, score, rewrite, then gate

A caption is two passes, because writing and judging are different jobs and one pass does both
badly. It is the same shape as the batch: score before you spend.

1. **Write** the three parts to the formulas in `MASTER PROMPT.md` — a title of year + make +
   model + one power word, a description of 3–5 sentences doing five jobs in order, 4–5 tags.
2. **Score it yourself** out of 100 on the page's five weights — hook shock 25, relatability 20,
   curiosity gap 20, shareability 15, visual wow 20 — and **rewrite anything under 80**, then
   score the rewrite. The number is not decoration: it goes in `plan/SCRIPT.md` and `queue` reads
   it.
3. **Run the grounding test on the title:** could this title sit on a different car's post? If
   yes it is a mood line, not a headline — rewrite it. `Doors That Opened To Sky` passed every
   length rule in this file and still failed that one test.
4. **Gate it.** `queue` checks the caption with `tools/caption.py` before a row exists: the word
   and sentence bands, the year and model in the title, the power word, the second person, the
   question, the tag rule, and the 80 floor. A failure is a rewrite; `--force` queues it anyway
   and records why in the row's `error` column.

A caption is never written once. The sentence that reads fine to its author is the one that
scores 64, and 64 is the caption nobody answers.

### 6. Queue it in `data.csv`

```bash
python3 tools/publish.py queue $PROJ --title "…" --description "…" \
  --hashtags " #… #…" --car "1959 Cadillac …" --angle "Size / Looks" \
  --caption-score 88
```

`--caption-score` is the number the second pass produced. The row is the queue entry: it points at
the render where it lies (`video`), carries its fingerprint (`video_sha`) and the caption split
into its three parts. Nothing is copied and nothing moves. `queue` refuses a caption that fails
the check, and a film whose bytes or caption are already in either CSV — the first of three gates
against posting the same thing twice.

### 7. Publish — only after an explicit yes

```bash
python3 tools/publish.py schedule $PROJ --dry-run     # the slot, nothing sent
python3 tools/publish.py schedule $PROJ               # upload, book, move the row
```

`schedule` uploads from `renders/`, books the slot (first film 60–120 minutes out, then 4–5 hour
gaps), **moves only the row** into `uploaded.csv`, and marks both workbooks: Car List
`Used? = Yes` with `Angle Used` and `Date Used`, and `Script Done?` / `Images Done?` / `Posted?`
on the Tracker row for that car. It will not invent a Tracker row it cannot find — that one is
written by hand. Uploading is a public, external action: never run the real `schedule` for a film
the person has not said yes to.

### 8. Sync, measure, deliver

```bash
python3 tools/publish.py sync $PROJ     # status, post URL, published_at, workbooks
```

Then `Views (48h)`, `Views (7 days)`, `Star? = Yes` at 50,000+, and `Notes` with the hook and the
fact used, so a Part 2 never repeats them. Deliver the path plus one line on what changed, delete
`renders/cut/` once the film is delivered, and delete unsent drafts outright.

### What never happens, at any step

- **The same film posted twice.** Three gates: `queue` refuses known bytes or caption, `schedule`
  prints `SKIP` when the fingerprint is already in `uploaded.csv`, and BrightBean adopts its own
  earlier post if a run was interrupted.
- **A moved or copied film.** The row points at the render; `videos/` and `uploaded/` no longer
  exist and are not to be recreated.
- **An overwritten Car List row.** A repeat after 90 days is a **new row at the bottom**.
- **A second post for one car + angle.** A different angle, or nothing.
- **A build under 80, or a fact that cannot be sourced.** No film is worth an invented number.
- **Anything posted from a Meta AI chat.** It cannot publish; `schedule` is the only door, and only
  after a yes. No credentials, page tokens or app passwords ever go into a prompt, and no prompt
  is sent to a composer that was not checked first.
- **A paid plate, or a published post, without a yes.** Ask first, every time.
- **Their footage edited.** Work on a copy, or render our own layer on top.

---

## The pipeline — do not reorder

This is steps 3–5 of the working procedure at film detail; it is the same order, not a second one.

| # | Step | Output |
| --- | --- | --- |
| 1 | Pick a car, one 3-second shocking fact, score it | `plan/VIRAL.md` |
| 2 | Fact-check year, make/model/trim, engine, production, price/speed | `plan/FACTCHECK.md` |
| 3 | Write the spoken script to the word budget | `plan/SCRIPT.md` |
| 4 | Plates, one per 3 s (the six fixed angles first), native 1080×1920, no living beings | `stills/*.png` |
| 5 | One Kokoro take of the paragraph, `speed: 1.2` | `audio/paragraph/line-01-v120.wav` |
| 6 | Transcribe that file to word times | `audio/paragraph/transcript.json` |
| 7 | Fill the scene table: durations, frames, stills, camera, text, word times | `scenes.py` + `tools/scene_builder.py` → `compositions/*.html` |
| 8 | Build the mix: voice, engine start, bed ducked to the words, closing roar | `audio/build_final.py` → `audio/final-audio.wav` |
| 9 | Render, join, mux, scan | `renders/<title>.mp4` |
| 10 | Write, score (80+) and gate the caption from `MASTER PROMPT.md` | the `queue` row in `data.csv` |

### Delivery name

A finished film is named after its title, and that title is **5–11 words** — the same words as
the first line of its caption (punctuation simplifies for a filename: `—` becomes `-`). Five is
the floor, not the target: the title has to name the year, make and model and still land as a
headline, which takes seven to eleven. Folders keep slugs; the file the person receives and
posts is the title, in clear words:

```
renders/1957 Cadillac Eldorado Brougham - Handbuilt.mp4
```

`meta.json` `output` holds that exact name (spaces and all — every command quotes it), so
`npm run render` writes the right file and a re-render never drops back to a working name.
`output` is therefore **set when the caption is written**, not at the start of the build. Never
deliver a working name — `final`, `v2`, `part2`, `reel-final`, a date, a version: the file
name is what the page posts, and it is chosen before the film is shown, never after.

Paths in this file are inside the film's folder (`video-projects/<page>/<film>/…`) unless they start
with `assets/`, `sound/` or `tools/`, which belong to the shared engine.

**The scripts do not read `transcript.json` at build time.** It is the measurement record; the
word times are copied by hand into the scene table and the sound build. Editing the JSON alone
changes nothing — see the timing law below.

### Timing law

The voice is the clock. Nothing is placed by eye or by silence detection.

- One paragraph, one take, `speed: 1.2` **in the TTS request** (never `atempo` afterwards).
- `audio/paragraph/transcript.json` is a list of `{text, start, end}` in seconds, measured on
  that WAV. Reference build: 41 words, 17.138 s. It is the JSON sidecar that
  `hyperframes transcribe` writes beside the WAV, renamed in place.
- **Nothing parses that file at build time.** The measured times are copied into the `*_at`
  values in that film's `scenes.py` and the constants in its `audio/build_final.py`. A
  new voice take therefore means re-transcribing *and* rewriting those numbers.
- The voice is placed at `LEAD = 1.00 s`, so **every word time in the transcript is +1.00**
  before it is used for picture. That second is not empty air: it is the engine start playing
alone (see *Sound law*), so the car speaks before the narrator does.
- **A cut lands ~65 ms before the first word of the next line** — the picture changes in the
  pause, never on top of a word.
- **Every text reveal sits on the word it belongs to.** A big card that changes mid-word is
  the classic fault of this engine; it happened once at 12.24 s and must not recur.
- Frame counts are exact: `frames = round(duration × 60)`, and the six must sum to
  `total_duration × 60` (reference: 256+311+218+95+98+138 = 1116 = 18.600 s).
- The closing card holds alone for the last 1.4 s so the engine can answer the final question.

### Composition contract (HyperFrames)

Each scene is `video-projects/<page>/<film>/compositions/<scene>.html`, one root element carrying:

```html
<div id="root" data-composition-id="s01-hero" data-start="0" data-duration="4.266667"
     data-width="1080" data-height="1920">
```

- Timed children are `class="clip"` with `data-start`, `data-duration`, `data-track-index`.
- One paused timeline per composition, registered at the end of the script:

```js
const tl = STAGE.driver(DUR, () => {});
BROLL.live(tl, cam);
window.__timelines = window.__timelines || {};
window.__timelines['s01-hero'] = tl;
```

- **Deterministic only.** No `Math.random()` at draw time (use `STAGE.mulberry32(seed)`), no
  network, no remote fonts, no date/time reads. The same inputs must render the same frames.
- Paths are relative to this folder (`assets/…`), never absolute, never `../`.

Helpers available to every scene (`assets/`, all local):

| API | Use |
| --- | --- |
| `STAGE.driver(dur, frame)` | paused master timeline that calls `frame(t)` every tick and on `hf-seek` |
| `STAGE.mulberry32(seed)` | seeded random for grain/noise |
| `STAGE.E` / `STAGE.impact` / `STAGE.spring` | eases and camera-transient curves |
| `BROLL.make(root, opts)` | camera over a still: `src, duration, seed, zoom0, focus, handheld, grain, vignette, shots[], shakes[]` |
| `BROLL.live(tl, cam)` | binds the camera to the timeline |
| `BROLL.MOVES` | `hold, push, pull, truckR, truckL, craneUp, craneDown, rollR, rollL, orbitR, orbitL` |
| `SEAM.blur(tl, dur, opts)` | the seam: focus in at the head, defocus at the tail — a film's only transition |
| `TX.slam(tl, el, at)` | the big card hits |
| `TX.roll(tl, el, at, dur, seed)` | a number spins through random digits and locks onto its real value — use it for **every** number, price, year or figure |
| `TX.words(tl, el, at, gap)` | kicker/label arriving word by word |
| `TX.typeOn(tl, el, at, per)` | character-by-character, use sparingly |

### Seams

**Seams are a blur cut, not a flash, and they live in the engine.** `assets/seams.js` (loaded
right after `text.js`) exposes one helper:

```js
SEAM.blur(tl, DUR);                        // focus in 0.18 s at the head, defocus 0.20 s at the tail
SEAM.blur(tl, DUR, { in: 0, out: 0.20 });  // frame 0 stays sharp (thumbnail)
SEAM.blur(tl, DUR, { in: 0.18, out: 0 });  // last frame stays sharp (closing card holds)
```

The outgoing frame defocuses over its last `0.20 s` (`blur(0 → 18px)`, ease-in) and the incoming
one focuses in over its first `0.18 s` (`blur(18 → 0px)`, ease-out), on the plate only — the type
stays sharp, like a focus pull. The picture changes inside a camera move instead of as a white
hit. Options: `in` / `out` seconds, `px`, `el`. **A scene writes no transition code of its own** —
one `SEAM.blur` call, and the behaviour is the engine's, so changing the cut changes every film
at once. **Frame 0 of the film and the last frame stay sharp.**

No white flash overlay, no skew whip, no transition sound. The picture changes in a blur; the
mix has no whoosh on the cut (see *Sound law*), so the engine bed carries the change. This
replaced the old `0.20 s` flash-out / `0.16 s` flash-in after the flash read as a strobe on
repeated viewing.

Scenes are joined without re-encoding, so a one-frame error in any scene's duration shifts the
audio against every cut after it.

### Numbers law

**A number never appears as flat text.** Any year, production count, horsepower figure, price or
0–60 time is counted out: the digits spin through random values and lock onto the real one,
left to right, before the reader can finish reading the label. It is the difference between a
caption and a claim.

- `TX.roll(tl, $('b1'), at, dur, seed)` — `dur` `0.75–0.95 s`, its own `seed`.
- The roll starts **on** the word and overlaps the `TX.slam` entrance, never before it.
- Keep the digit count: `547` never flashes `47`, `4.7` never loses its decimal.
- Seeded, so every render spins the same digits. Never `Math.random()` at draw time.
- The label under it (`BUILT`, `HORSEPOWER`, `SECONDS`) arrives word by word *after* the lock,
  so the eye reads the number first and the meaning second.

### Sound law

One engine, one voice, nothing that competes with a word. Three parts, always:

1. **Start, exactly `1.0 s` at the head, before the first word** — the engine catching while
   nothing else is happening, so it is the first thing the viewer hears. The cranking ramp at
   `0.10–1.10 s` of `sound/engines/engine-start-idle-rev_*.mp3`, at full level, level-matched to
   `−20 dBFS` RMS (that recording is quiet; measure and normalise, never guess a multiplier). It
   ends as the first word starts: `LEAD = 1.00 s` in both `scenes.py` and
   `build_final.py`, and scene 1 is 0.7 s longer than its picture needs.
2. **Bed, low, all the way through** — the `14.00–16.00 s` idle of the same file, looped with a
   `0.30 s` equal-power crossfade, highpass `42 Hz`, lowpass `2.2 kHz`, compressed flat,
   level-matched to about `−29 dBFS` RMS. It fades in over `0.8 s` from `1.05 s` so it grows out
   of the start instead of fighting it, and it never stops for the rest of the film.
3. **Roar, `2.0 s`, after the last word, with no voice over it** — the car answers and nothing
   talks across it. Take one clean rev whole (`27.72–29.45 s`), play it at rate `0.86` so it lands
   at `2.01 s` and a deeper edge, and give the last scene that two extra seconds of picture with a
   camera shake on the hit. The roar starts on the frame the closing card lands, after the final
   word has finished, and the tail fades out clean.

**Ducking is built from the transcript, not from a compressor guessing.** Read the word times,
set the bed to `0.100` (−20 dB) across every spoken word and `1.0` in the gaps, then smooth with
`20 ms` attack and `220 ms` release. The gap level is what the viewer hears; the moment a word
begins the bed drops far below it — measured result to keep: about **−35 dB in the pauses** and
**−52 dB under speech**, 35 dB+ below the voice, so the car is felt under the words and never
heard over one.

- **No revs under speech.** Accents live in gaps only; the two allowed ones are the start and the
  closing roar.
- **One low hit, at `17.12 s`, under the closing card only** — it lands with the question and
  the opening roar so the close has weight. That is the only hit in the film.
- `0.10 s` fade-out at the tail. **No whooshes on the cuts, no hits under the numbers, no
  music** — the change of picture is a blur cut and needs no sound; a whoosh on every seam is
  the fastest way to make a reel feel cheap.
- Master: **−14.2 LUFS integrated, true peak no higher than −1.3 dBFS**. The speech section
  alone must measure about −14.2 LUFS, so the voice is loud enough on its own.
- A `2.0 s` roar means the film is `2 s` longer than the voice: extend the **last** scene, keep the
  other five, and re-render — never squeeze the roar in under the final words.
- All knobs live in the first 40 lines of that film's `audio/build_final.py`. Change numbers,
  not structure.

### Style of this engine

Fixed, so every reel is recognisably from the same page:

- Ground `#050506`, type `#F5EFE6`, accent `#E8412B` (the second card line, the rule, the dot).
- Big card: **Anton 208 px**, two lines, `line-height 0.90`, left at 62 px; the second line is
  either red, or "small" at 96 px when the phrase is long.
- Kicker and label: **JetBrains Mono 700**, 31 px / 40 px, letter-spacing 0.28–0.30em, caps.
- Footnote: **Inter 500**, 31 px, 60 % opacity.
- A scrim (top or bottom, 1020 px tall, cubic gradient to transparent) keeps text legible over
  the plate. Full bleed plate, thin red rule under the card, hand-held camera at ~1.0.
- Text block sits in the lower third for most shots; the hero puts it under the hood line.

---

## Content rules — binding, from MASTER PROMPT.md

- **Viral score before the script.** Seven spare lines: hook, rubric score out of 100
  (hook shock 25, relatability 20, curiosity gap 20, shareability 15, visual wow 20).
  **Below 80 is rejected** — show the rejected topics and why, pick another car.
- **No invented facts.** Year, make/model/trim, engine size, production number, and any price
  or speed claim must be verified; if unsure, cut the claim. "Reportedly / around" is allowed,
  a made-up number is not. Horsepower may simply be left out (the reference build does).
- **Script length:** 38–45 words for 15 s, 78–90 for 30 s. Count them and show the count.
- **The script is one chain, not a list.** Every sentence grows out of the one before it — carry
  a word forward, answer the question the last line opened ("So they…", "But it…", "That
  meant…"), or raise the stakes. No "Also" / "Another thing", no fact dropped in from a new
  subject, no two sentences that could swap places. The four beats (setup, turn, proof, payoff)
  are links, not sections. Run the flow test on every script: read it aloud as one breath, delete
  each sentence and check the next still works (if it does, that sentence was a detour), say the
  last line straight after the first (if it still makes sense, the middle was padding). Tone is
  an excited teacher who just found this out — every number lands as a surprise the previous
  line set up, and the viewer ends feeling they learned something they can repeat.
- **One plate per 3 s of film.** The six fixed angles first, in this order: front ¾ hero, side
  profile, rear, engine bay, interior, wheel close-up; then close-ups to fill the cadence.
  **No humans, no animals, no reflections of people, no text, no watermark**, car only. Same
  colour, wheels, tyres and body style in every plate.
- Caption is **exactly three parts, no labels** (title / description / hashtags), blank line
  between each:
  - **title** = year + make + model + one power word, under 12 words, no full stop; it is also
    the file name.
  - **description** = **a real paragraph, 3–5 sentences, 45–80 words** — never a one-liner. Open
    on the hook, spend the middle on the verified numbers the film used, talk to the viewer in
    the second person, compare the car to something they know, and close on a call to action:
    a question they can answer in a comment. No invented facts, no emoji, no links, no hashtags
    inside it.
  - **hashtags** = **4–5**, one line starting with a single space: one brand tag + one
    classic-car tag + one model or year tag (+ one more only if it is specific to this car).
  Never `#viral #fyp #reels #trending #foryou`.
- **The caption is scored, not just formatted.** 80 or more on the same five weights as the car,
  and the title has to pass the grounding test. `queue` runs `tools/caption.py` over it before a
  row exists — see *The caption pass* before step 6. A caption that fails is rewritten, not queued.
- American English, short sentences, no emoji, no "hey guys", no hashtags in the voice.

## Money and other people's media

- Free routes only for images (Google Flow, or Meta AI in a browser) and for voice (local
  Kokoro). **Ask before anything paid** — image APIs, stock footage, music.
- The engine does not generate images. Write the prompts (see the project's `plan/PROMPTS.md`
  for the pattern), generate elsewhere, save as 1080×1920 PNG into that project's `stills/`,
  and record the prompt in the matching `<shot>.images.json`.
- Engine recordings stay under the Pixabay Content License (`sound/README.md`): usable in the
  video, never redistributed as standalone audio files.
- Never edit, re-encode or delete the person's own footage or recordings.
- Voice, if it must be remade (Kokoro running locally). Its new word times must then be copied
  into that project's `scenes.py` and `audio/build_final.py` by hand — the build does not
  read the transcript for you:

```bash
curl -s http://localhost:8880/v1/audio/speech -o audio/paragraph/line-01-v120.wav \
  -H 'Content-Type: application/json' \
  -d '{"model":"kokoro","input":"<the 38–45 word paragraph>","voice":"am_michael",
       "response_format":"wav","speed":1.2}'
npx hyperframes transcribe audio/paragraph/line-01-v120.wav   # → JSON sidecar beside the WAV
```

---

## Verification gates — never show a film before these pass

1. `npm run lint -- video-projects/<page>/<film>` → **0 errors, 0 warnings**.
2. `npm run check -- video-projects/<page>/<film>/renders/<out>.mp4` → `frame0_blank: false`,
   `black_frames: []`, `one_frame_pops: []`.
   `hard_jumps` are expected **only** at the scene seams (reference: frames 253–260, 564–570,
   784–789, 877–884, 975–981); a jump anywhere else is a fault.
3. **Look at the frames yourself.** Contact sheet, then the seams and both ends:

```bash
ffmpeg -y -v error -i video-projects/<page>/<film>/renders/<out>.mp4 \
  -vf "select='eq(n,0)+eq(n,120)+eq(n,300)+eq(n,470)+eq(n,790)+eq(n,1115)',scale=360:-1,tile=3x2" \
  -frames:v 1 video-projects/<page>/<film>/qa/final-sheet.jpg
```

4. Audio: `-14.2 LUFS ±0.3`, peak ≤ −1.3 dBFS, voice clearly above the bed, no rev touching a
   spoken word. Speech section measured on its own.
5. Facts, word count, caption format re-read against `MASTER PROMPT.md` before sending.
6. The file is named after its title — **5–11 words**, the same words as the caption's first line,
   and `meta.json` `output` says the same. Count the words out loud, not by eye, and read the
   title on its own: does it name the car and still make a stranger stop? If not, rewrite it.

Report checks that failed or could not run. Never call a film verified because it compiled.

---

## Choosing the next car

The sequence is `## The working procedure`; this section is the workbook law it relies on.

The page's Car List workbook (`<page>/Vintage-Motor-House-Car-List-300.xlsx`, 312 cars) is the
source of truth for what has been filmed. Work in batches of **10**:

```bash
python3 tools/publish.py pick video-projects/<page> --count 10    # read-only
```

It prints the first 10 cars with `Used? = No`, plus any car that is free again after 90 days.
Then the rule, in the workbook itself:

1. Pick 10 cars with `Used? = No` for the batch.
2. The moment a car is filmed, set `Used? = Yes` and fill `Angle Used` + `Date Used` on its row.
3. A car may be filmed again **90 days after** `Date Used`, with a **different angle**, as a
   **new row at the bottom** of the list — never by overwriting the old row.
4. The list holds 312 cars; `pick` counts them so you always know how much runway is left.

`schedule` marks both workbooks for you when a film is booked (Car List `Used?/Angle/Date`,
Tracker `Date/Script/Images/Posted`), so the only case you mark by hand is a film that is built
but deliberately not scheduled.

Then per car: research the facts, choose the angle, and only continue if the viral score in
`plan/VIRAL.md` is **80 or more** (`plan/FACTCHECK.md` first — no invented facts). The plan phase
writes `plan/VIRAL.md`, `FACTCHECK.md`, `PLATES.md`, `SCRIPT.md`, `BEATS.md`, `TIMELINE.md`; the
caption at the end of `SCRIPT.md` is what becomes the `queue` row.

---

## Publishing a finished film

The person posts on **BrightBean**, which fronts Facebook (and other channels) through one API.
Each **page** books its own films; the tools live in the engine root. Uploading and scheduling are
public, external actions: **ask for a yes on that film before running `schedule` for real.**

### What a page holds

The queue and the ledger belong to the channel, not to one film, so they sit at the page level
and you name the **film** on the command line:

```
video-projects/<page>/                ← the channel: everything here is shared by its films
  data.csv      the queue: one row per film waiting to go out
  uploaded.csv  the ledger: every booked film and its slot
  *.xlsx        the page's workbooks
  <film>/       meta.json, renders/, audio/, compositions/, stills/, plan/, qa/
```

There are no `videos/` or `uploaded/` folders and no copies of renders. A row in `data.csv` **is**
the queue entry, and it points at the finished film where it lies:

| Column | Holds |
| --- | --- |
| `id` | short id binding the row to its post |
| `video` | absolute path of the finished film in its own `renders/` — nothing is copied |
| `video_sha` | fingerprint of that file; what stops a double upload |
| `title`, `description`, `hashtags` | the three caption parts, editable |
| `caption` | the three joined, exactly as Facebook receives them |
| `car`, `angle` | what `schedule` uses to find the workbook rows |
| `status` | `ready` → `uploaded:<post id>` → `scheduled` → `published` |
| `scheduled_at`, `published_at`, `post_id`, `post_url` | written by `schedule` / `sync` |

So `tools/publish.py queue video-projects/<page>/<film>` reads that film's `meta.json` and
`renders/`, and appends one row to the page. Two films from one page share one queue and one
ledger, which is what keeps the 4–5 hour spacing honest across both.

`meta.json` names the channel:

```json
"social": { "platform": "facebook", "account": "Vintage Motor House" }
```

`account` is the BrightBean account handle exactly as `/accounts` reports it — not the Facebook
page URL. Only `facebook | Vintage Motor House` is set up today; other channels use the same
endpoints but need their own project whose `account` names them.

### The credential

`BRIGHTBEAN_API_KEY` is read from the environment, then `image2videoEngine/.env`, then
`~/.env_brightbean`. It never goes in a project folder and is never printed — the tools report
its length at most. `BRIGHTBEAN_BASE` overrides the API host.

### The commands

Run them from the engine root. `status` is read-only; the rest write where the table says.

| Command | What it does | Writes |
| --- | --- | --- |
| `pick` | lists the next cars to film and the ones free again after 90 days | nothing |
| `queue` | adds a `ready` row pointing at the render, with title, description, hashtags and caption | `data.csv` |
| `schedule --dry-run` | resolves the channel, computes the slots, prints them | nothing |
| `schedule` | uploads each queued film from where it lies, creates the post, books the slot, moves the row, marks both workbooks | `uploaded.csv`, `data.csv`, both `.xlsx` |
| `sync` | reads each post back, records `published` and the post URL, marks the workbooks on publish | `uploaded.csv`, `data.csv`, both `.xlsx` |

A row leaves `data.csv` only after its slot is booked — and only the row moves. The film stays
exactly where it was rendered, `renders/<title>.mp4`, so the link in the queue never goes stale
and there is nothing to clean up afterwards.

### Never upload the same film twice

Three gates, in this order, because a repeated upload is the one mistake that cannot be undone:

1. **`queue` refuses the file.** Every row records `video_sha`. Queueing bytes that are already in
   `data.csv` or `uploaded.csv` — or pointing at a file some row already points at — stops with the
   row and status that already hold it.
2. **`schedule` refuses the fingerprint.** Before a row is uploaded, its `video_sha` is compared
   with every booked row; a match is skipped with a `SKIP` line naming the earlier film, and the
   row stays in `data.csv` with the reason in `error` so a human can look (the usual cause is the
   same cut queued twice under different titles).
3. **BrightBean refuses the caption.** If a post with this exact caption already exists on the
   channel, a retried run adopts that post and books its slot instead of creating a second one, so
   an interrupted `schedule` finishes rather than duplicating.

A genuinely new cut has a new fingerprint and is allowed; re-posting the same car later means a
new film, not the old file. Never re-run `queue` "to be sure", and never edit `video_sha` by hand.

### The caption

`queue` stores the title, description and hashtags as separate columns *and* as one `caption`, so
the text can be corrected before scheduling without re-parsing it. Facebook receives:

```
<title>

<description>

<hashtags>
```

which is the three-line format `MASTER PROMPT.md` requires. The same caption twice in one project
is refused as a mistake. `--caption-file` takes the same three blocks from a file,
`--video` queues something other than the project's finished render, and `--car` / `--angle` are
what let `schedule` find the workbook rows.

### Slots

The image page's cadence, kept: the first film goes **60–120 minutes** from now when the ledger is
empty, otherwise **4–5 hours** after the project's last booked slot. Following films are another
4–5 hours, never under 4. `--start-at` books an absolute first slot, `--start-delay N` a fixed
number of minutes from now, `--interval N` a fixed gap — use these when a time is asked for.
Without them the gaps are randomised on purpose: the same minute every day reads as a bot.

The last slot comes from that project's `uploaded.csv`; the API is asked only when the ledger is
empty, so one project's schedule never depends on another's.

### The workbooks

`schedule` and `sync` edit the project's two `.xlsx` files through `tools/excel.py` — no
`openpyxl`, and the existing styles and inline-string cells survive.

- **Tracker** — for the row whose `Car (Year Make Model)` equals the row's `car`: `Date` if it is
  empty, `Script done = Yes`, `Images done = Yes`, `Posted = Scheduled` when booked and
  `Posted = Yes` once `sync` sees it published. No match prints a note; it never invents a row.
- **Car List 300+** — that car's row: `Used? = Yes`, `Angle Used`, `Date Used`. The model matches
  exactly first (`Mustang Boss 429` must not land on the `Boss 302` a few rows above), and among
  repeats of one car the newest unused row wins, which is the row a repeat after 90 days should
  take.

`--no-excel` leaves both alone. The workbooks are the page's calendar: a missing row is added by
hand, never by the tool.

Both tools edit the `.xlsx` files **found in the film folder you name, or in the page folder
above it** — the page keeps one set, not one per film, and that set is the one they find. On a
silent run of `schedule` with no marks, the workbooks are missing from both folders; put them
back at the page level and re-run `sync`.

### Re-running, failures, API vs MCP

- `schedule` resumes. A row already `scheduled`/`published` is skipped; a film already uploaded
  resumes at its post; a post with the same caption on the same account is adopted instead of
  duplicated. Uploads are streamed in parts and retried once through an idempotency key.
- A failure marks that row `failed`, stores the reason in `error`, prints it, and the batch
  continues. `failed` rows are still pending, so the next `schedule` retries them — fix the cause
  first (the file, the account, the caption).
- Use the **REST API** for scheduled work: it runs unattended and reports each channel's `url`,
  `publishedAt` and `error`. The **MCP** server fronts the same backend and suits a one-off check
  in chat; never book the same film through both, since neither sees the other's slots.
- Uploads are video only (`mediaType: "video"`, `.mp4`) — no thumbnail, no caption on the asset;
  the caption belongs to the post.

---

## Changing things — what else must move

| If you change | Also change |
| --- | --- |
| A scene's duration or frame count | `frames` in that film's `scenes.py`, `FRAMES` in its `audio/build_final.py`, its `plan/TIMELINE.md`; `index.html` is regenerated |
| Script, voice take or `speed` | re-transcribe, then every `*_at` time in `scenes.py`, cut positions in `plan/TIMELINE.md` |
| A still | keep the filename, or change `still` in `scenes.py` |
| Scene slugs or their number | `scenes` in that project's `meta.json` (the render reads it), the layers in `index.html` |
| The output filename | `output` in `meta.json` — the 5–11 word title, the same words as the caption's first line |
| Sound levels | `START_*` / `BED_*` / `DUCK*` / `ROAR_*` in `audio/build_final.py`, the sound section of `plan/TIMELINE.md` |
| A caption, title or hashtag after `queue` | that row's `title`/`description`/`hashtags` **and** its `caption` in `data.csv`, before `schedule` books it |
| `social.account` or `platform` in `meta.json` | nothing else, but the account must exist and be connected in BrightBean; `uploaded.csv` keeps the old channel's history |
| A queued film's file | re-render it (a new file has a new fingerprint, so it is allowed) and point the row's `video` at it; never rename or move a render after queueing |
| Anything in the engine (`assets/`, `sound/`, `tools/`) | every project at once — check the reference film still renders before moving on |

## Known pitfalls of this engine

- **Silence detection is not sync.** Cut on transcribed word times only.
- **16:9 stills cropped to 9:16 cut the car in half.** Generate vertical natively at 1080×1920.
- **A rev under the line that carries the number swallows it.** Engine lives in the gaps.
- **A number printed flat reads as a caption; a number counted out reads as a fact.** Use
  `TX.roll` for every figure, and give the roll `0.75 s`+ or the digits just blink.
- **Engine recordings are much quieter than they look.** The `sound/engines/` files measure around
  `−47 dBFS`; a fixed `volume=0.3` makes an inaudible bed. Level-match each slice to a target RMS
  in the build script, then print the measured levels in the pauses and under speech.
- `assets/broll.js` deliberately re-decodes the plate and redraws on `hf-seek`. Removing either
  gives a blank first frame or a plate one frame late — leave them alone.
- `magick` is not installed. Use `ffmpeg` for scaling, tiling and contact sheets.
- `tools/scan.py` takes **file paths**, one or more, from the engine root
  (`python3 tools/scan.py video-projects/<page>/<film>/renders/<out>.mp4`); `.mp4` is added if you
  leave it off. It no longer guesses a project.
- 1080×1920 PNGs are large; downscale before attaching them anywhere with a size limit.
- `renders/cut/` is disposable — it is regenerated on every render. `audio/final-audio.wav` is
  not: if it is missing, the mux step fails, so run the mix again.
- Rebuilding the scenes (`python3 tools/scene_builder.py video-projects/<page>/<film>`) rewrites
  that project's `compositions/*.html` and `index.html`. Hand edits made in those files are lost —
  put the film's own changes in its `scenes.py`, and anything that should hold for every film in
  `tools/scene_builder.py` or `assets/`.
- **The workbooks only update where they exist.** `schedule` and `sync` look for `*.xlsx` in the
  film folder and then in its page folder; missing from both means no error and no marks. They
  live at the page level — check the Tracker after the first `schedule` of a batch.
- `uploaded.csv` is the truth for what is booked. Never hand-edit its `status`, `post_id` or
  `post_url` — `sync` overwrites those from the API. Correct a caption in `data.csv` *before*
  `schedule`, never after.
- **There are no copies of renders.** `data.csv` holds the path of the film in its own `renders/`
  and `schedule` uploads from there, so a queued row is a pointer, not a duplicate. Renaming or
  moving that file after queueing breaks the row; re-render instead.
- **Scenes are opened from the engine root**, so their `assets/…` refs hit the shared library
  and their stills are addressed as `video-projects/<page>/<film>/stills/<file>.png`. The film's own
  `index.html`, by contrast, uses project-relative refs (`compositions/…`, `audio/…`) — that is
  what the linter and the render pre-flight resolve against the project folder.
- **The spreadsheets are the source of truth, not your memory of them.** Never mark `Used? = Yes`
  for a car whose film is not finished, and never reuse a car inside 90 days at all — a different
  angle does not make it a new post.
- The Tracker's `Notes` is what stops a Part 2 repeating the original hook and fact. Write it.
- **Every Tracker row is a real post.** Never seed it with sample rows to show how it works; the
  only rows allowed are films that were actually published, with their real score and date.

---

## What to post next — the two spreadsheets

Two workbooks hold the page's production calendar, at the page level
(`video-projects/vintage-motor-house/`). They, not memory, decide what gets made. Read both
before a batch, write both after every film.

### `Vintage-Motor-House-Car-List-300.xlsx` — the 312 cars

Sheet `Car List 300+`, one row per car, 312 rows from 1940 to 1990:

`No. | Year | Brand | Model | Used? | Angle Used | Date Used | Views | Star?`

- Every row starts at `Used? = No`. **Pick from `No` only** — `python3 tools/publish.py pick
  video-projects/<page>` prints the next 10 and counts the runway.
- When a film is finished, set `Used? = Yes` and fill `Angle Used` and `Date Used`. Fill `Views`
  and `Star?` once it is posted and numbers exist.
- **A car used a second time after 90 days gets a new row at the bottom** — never overwrite the
  old row, it is the record of that angle. (The list repeats `Year | Brand | Model` by design.)
- The file's own `How To Use` sheet says the same thing in four lines; keep it true instead of
  inventing a parallel convention.

### `Vintage-Motor-House-Tracker.xlsx` — the posts

Sheet `Tracker`, one row per post:

`Date | Post No. | Car (Year Make Model) | Angle Used | Viral Score % | Script Done? | Images Done? | Posted? | Views (48h) | Views (7 days) | Star? (50K+) | Notes`

- **One row = one car + one angle, and that pair never repeats.**
- `Script Done?` / `Images Done?` move as the film moves; `Posted?` when it is live; views at
  48 h and 7 days; `Notes` records the hook and the fact used, so a Part 2 does not reuse them.
- `Star?` becomes Yes at 50,000+ views. That car earns a Part 2 after 90 days.
- State at the time of writing: one real row — 2026-11-14, Post No. 1, 1969 Ford Mustang Boss
  429 (Price / Rarity, 82, posted 02:40). The 2026-11-13 sample rows were invented and were
  deleted; the Tracker only ever records films that were actually published.

### The maths that says "don't panic"

312 cars × 3 angles = 936 posts. Two a day is about 15 months, one a day about 2.5 years, before
one angle repeats. There is therefore never a reason to pad the list with a car you cannot
verify, and never a reason to rush a batch.

### The six angles, rotated

`Size / Looks` · `Price / Rarity` · `Engine / Speed` · `Secret Story` · `Why It Failed` ·
`Why It Became Legend`

- Rotate them across a batch. Ten luxury cars in a row is the failure mode, ten reels are not.
- The angle chooses the hook, the script and what the cards say. It does **not** change the six
  stills or their order; it changes which of them carry the big cards and the footnote.
- One car can carry three to five of these, one per post, never two inside 90 days.

### Ten films, ten folders

`## The working procedure` is the sequence; a batch runs it ten times. The batch changes exactly
one thing: the choosing happens once, up front, for all ten (steps 1–2 across the whole list, then
steps 3–8 per film). Nothing about a single film changes because nine others are being made.

Batching in practice: the engine is **one folder** and the page is **one folder**; each film is a
folder inside its page, made with the skeleton in step 2. Never clone the engine (`node_modules`
alone is 700 MB) and never copy the page — the workbooks and the queue would fork. Ten films means
ten small film folders.

A film folder is roughly 30–45 MB and holds nothing but that film. Nothing in `video-projects/` is
an input to another film; the only shared things are `assets/`, `sound/engines/`, `tools/` and
`node_modules/`.

A film that will post itself needs only its `social` block in `meta.json` — or none at all, since
the page's `data.csv` and `uploaded.csv` are created on first use in the page folder above it. Workbooks are found in the film folder or the page folder, whichever has them;
keep them at the page level.

Making one film a day on demand is the anti-pattern. A batch of ten is one session of work and
ten days of posts, and it is what keeps the list honest.

### Reading the workbooks without Excel

`openpyxl` is not installed, and should not be added just for this. An `.xlsx` is a zip:

```bash
python3 - <<'PY'
import zipfile, xml.etree.ElementTree as ET
N = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
z = zipfile.ZipFile('Vintage-Motor-House-Car-List-300.xlsx')
for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter(N + 'row'):
    vals = []
    for c in row.iter(N + 'c'):
        isel, v = c.find(N + 'is'), c.find(N + 'v')
        vals.append(''.join(t.text or '' for t in isel.iter(N + 't')) if isel is not None
                    else (v.text if v is not None else ''))
    print(vals)
PY
```

Text in these two files is stored inline; if a column comes back empty, the same loop needs
`xl/sharedStrings.xml` for shared strings.

**Do not round-trip the workbook through a library** — `openpyxl` and friends rewrite the styles
and can drop the person's formatting. If they ask you to write a cell (they did, for post 1),
copy the file into `backup/` first, then edit only the target cells inside
`xl/worksheets/sheetN.xml` as text, keeping the existing `s=` style number and `t="inlineStr"`
shape, and keep `dimension`, `autoFilter` and `cols` consistent with the new last row. Entering a
film they have finished is fine; inventing a post, a score or a view count is not.

---

## Inside one film

`## The working procedure` steps 2–8 are the whole of it; nothing here overrides them. Three things
only matter once you are inside a single film.

The last step before showing a film is naming it: rename the render to its 5–11 word title (the
caption's first line, year + make + model + a power word), and put that same string in
`meta.json` `output` so the next render keeps it. A film is never sent under a working name.

Projects are independent: two can be in progress at once without touching each other, and
re-rendering the old film never disturbs the new one. Delete `renders/cut/` after a delivery —
it is rebuilt on the next render. Projects nobody has asked about stay archived; unsent drafts
are deleted, not left half-built.

## File map

| Path | What it is |
| --- | --- |
**The engine — shared by every film, edited with care:**

| Path | What it is |
| --- | --- |
| `AGENTS.md` | this file — operating manual for any AI model |
| `README.md` | plain-words guide for the person |
| `assets/stage.js`, `broll.js`, `text.js`, `seams.js`, `kit-config.js`, `gsap.min.js` | the drawing engine |
| `assets/fonts/`, `fonts.css` | local fonts, no network |
| `sound/engines/`, `sound/README.md` | engine recordings and their licence |
| `tools/render-all.sh` | one film: mix → render → join → mux → scan |
| `tools/scan.py` | blank/black/pop scan of any render |
| `tools/publish.py` | queue / schedule / status / sync a film to BrightBean, through its page |
| `tools/brightbean.py` | the API calls: account, multipart video upload, post, schedule, read back |
| `tools/excel.py` | dependency-free `.xlsx` cell read/write for the two workbooks |
| `tools/caption.py` | the caption contract as code: counts, bans, the naming rule, the 80 floor |
| `package.json`, `hyperframes.json`, `node_modules/` | toolchain, shared by all projects |
| `video-projects/<page>/` | one folder per Facebook page — its rules, workbooks and queue |
| `video-projects/<page>/<film>/` | one folder per film, inside its page |

**One page — `video-projects/vintage-motor-house/`:**

| Path | What it is |
| --- | --- |
| `MASTER PROMPT.md` | binding posting rules for every film on the page (score, facts, images, caption) |
| `META PROMPT.md` | the same rules as one prompt for Meta AI; only its INPUT block changes per batch |
| `tools/meta.py` | ask Meta AI through Browser MCP and get the answer back as text |
| `Vintage-Motor-House-Car-List-300.xlsx` | the 312 cars to draw from, with `Used?` and what was done |
| `Vintage-Motor-House-Tracker.xlsx` | one row per post: car, angle, score, views, Star |
| `backup/` | the workbooks as they were before each edit |
| `data.csv` | the queue: one row per finished film — caption, `video`, fingerprint, status |
| `uploaded.csv` | the ledger: every booked film, its slot, post id and post URL |
| `<film>/` | a film folder, below |

**One film — `video-projects/<page>/<film>/` (shown here for `1954-mercedes-300sl-gullwing`):**

| Path | What it is |
| --- | --- |
| `meta.json` | the project's build contract — name, output file, fps, scene order, duration — plus the `social` channel block |
| `index.html` | master timeline: the scenes and the mix as one film, for preview and lint |
| `scenes.py` | **data only** — the film's scene table: frames, stills, camera, cards, word times |
| `compositions/s01…s12.html` | the scenes, generated by `tools/scene_builder.py` |
| `stills/` | the six plates (+ their `.images.json` provenance) |
| `audio/paragraph/` | the voice take and its word timings — the clock |
| `audio/build_final.py` | the mix: start, bed loop, word-timed duck, closing roar, loudness |
| `audio/sfx/` | pieces the mix bakes; `audio/final-audio.wav` is the master |
| `plan/` | the paper trail: score, facts, prompts, script, beats, timeline |
| `qa/` | contact sheets and stills checked before sending |
| `renders/` | the finished MP4, named after the film's title, plus the disposable `cut/` |

The two workbooks are the **page's** calendar, not one film's: keep a single copy, in the
project you are working in, and carry it to the next project rather than forking it.
