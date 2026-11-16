# The working procedure — one batch, start to finish

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

This is the single sequence the project runs on. Every section after it explains one step, and
none of them reorders it. Work in **batches of ten**: one session of building, ten films, ten
posts. A film made on its own, out of order, or "just this once" is the anti-pattern — the Car
List and the Tracker only stay honest when the batch is the unit of work.

## 1. Choose the batch — ten cars, ten angles, ten scores

```bash
python3 tools/publish.py pick video-projects/vintage-motor-house --count 10
```

Ten cars with `Used? = No`, spread across brands and decades — not the ten Cadillacs at the top.
`pick` lists the next ten in row order, so choose across the whole list, not just its first page.

**When the person names or describes something, that is the brief and it outranks the list.** A
car, a fact, a memory, a scene, a feeling — "a barn-find Charger that turned out to be a Daytona",
"something about giant fins and terrible parking" — replaces `pick` for that film: the car they
named is the subject, the detail they gave is a beat of the script, and the feeling they asked for
decides the tone. The brief goes into `META PROMPT.md`'s INPUT block as `Brief: …`, and Meta
returns the five-line `BRIEF` block (heard / car / angle / fact / feeling) before any score. The
fact-check and the 80 gate still apply: a named car that scores under 80 is reported with the
angle that could rescue it, never swapped for a "better" car behind their back. Only an empty
brief falls back to `pick`.

The candidates then go to **Meta AI**, which scores them, names the angle for each, and writes the
script, caption and image prompts (one per 3 s) for the ones that pass — see [Meta AI does the
thinking](04-the-two-brains.md#meta-ai-does-the-thinking--the-agent-drives-it). Before any build,
every candidate clears the selection rules: no Tracker row for that `Car + Angle` pair, the car
outside **90 days**, and the six angles rotated so no two neighbours in the batch share one
([Choosing the next car](14-choosing-the-next-car.md)). The 90-day wait is for the operator
choosing; a car the person **names** is built anyway, because their request is the brief.

Then, in this order: `plan/FACTCHECK.md` (year, model and trim, engine, production, price/speed —
no invented facts) → `plan/VIRAL.md` (the score). **Under 80 the car is not built**: try another
angle, then another car, and leave its row `Used? = No` until a film of it exists.

Step 1 is done when there are ten cars, ten angles, ten scores ≥ 80, and no repeated pair.

The two routes themselves — Meta AI in the default Chrome, Flow in its own — are [The two free
brains](04-the-two-brains.md).

## 2. Make the folder and the plan

```bash
PAGE=video-projects/vintage-motor-house
PROJ=$PAGE/1959-cadillac-fins            # slug = year + car, never title words
python3 tools/new_film.py "$PROJ" --title "1959 Cadillac: The Biggest Fins Ever Built"
python3 tools/new_film.py --list          # the templates available
```

The skeleton comes from `templates/film/` — the folder tree, a `meta.json` carrying this film's
names, a guarded `scenes.py` skeleton, and `audio/build_final.py` copied from the reference build
so it already carries the current sound law (`templates/README.md`). It carries **no numbers**: a
scene table with another car's measurements is a film that is out of sync on every cut. Then fill
`meta.json` (page, slug, film, title, duration and `scenes` — and clear `status` / `published_at`
if the copy came from a published film), the `SCENES` table, and the numbers at the top of
`audio/build_final.py` (structure stays). Write the plan as you go: `FACTCHECK.md`, `VIRAL.md`,
`SCRIPT.md` (word budget, and the three-line caption at the end), `PLATES.md`, `PROMPTS.md`,
`BEATS.md`. `TIMELINE.md` is written from measurements at the end, not up front. One engine, one
page folder, one folder per film (30–45 MB); never clone the engine and never copy the page — the
workbooks and the queue would fork.

## 3. Voice first, timing from the voice

One Kokoro take of the whole paragraph with `python3 tools/voice.py <film>`, then transcribe
**that file** and copy the word times into that film's `scenes.py` and its `audio/build_final.py`.
The page has two voices: **`am_michael`** (default, speed 1.20, warm and steady — wonder,
nostalgia, luxury, price and legend) and **`am_adam`** (lower and harder — failure, secret,
rule-breaker, engine and racing; 1.20, or 1.30 only after a 30 s read measures long). Choose the
one the script asks for, keep the speed in the TTS request, and record the choice in
`audio/paragraph/voice.json`. Cuts land on the measured words, never on estimates; a late cut is a
re-take, not a stretched clip.

**Then refine the silence — this pass is mandatory, on every take.** Kokoro's pacing comes from
punctuation alone, so a paragraph written with ordinary full stops buys ten 0.3–0.6 s holes and
the voice reads *stop, read, stop*. Two things are done together: write the read for the ear (at
most two full stops, the rest commas, semicolons and dashes, numbers spelled as they are said —
see the `kokoro-natural` skill), and run the take through

```bash
python3 tools/voice_trim.py video-projects/<page>/<film>
```

It caps each internal pause at `0.22 s` (a breath, not a hole), re-transcribes the refined file,
and re-anchors those word times to the speech blocks it measured — whisper's own timings drift on
a short read (0.35 s on the Cutlass film, enough to place a word inside a pause), so the aligned
table, not whisper's, is the clock. A take is not finished until its longest internal pause
measures `≤ 0.22 s` and `transcript.json` is the re-anchored one.

## 4. Plates — one still per 3 seconds

**A new plate every 3 seconds, and every plate a different frame.**
`plates = ceil(film_seconds / 3)`: an 18 s film is six plates, a 24 s film is eight, a 27 s film
is nine, a 30 s film is ten. The six fixed angles come first and in this order — front ¾ · side ·
rear · engine bay · interior · wheel — and every plate after them is a close-up (headlight, badge,
wheel, exhaust, gauges, engine detail, steering wheel) placed where a beat needs a fresh image.
**No file may be used twice**: a closing return to the hero is its own tighter crop, never the
same still again, and `tools/score.py` counts the distinct stills against `ceil(seconds / 3)`. No
still may run longer than ~3 s; that cadence is the pace of the page. Each prompt is recorded in
`<shot>.images.json`.

**Archival, period and motion plates are legal.** A period advertisement, a manufacturer press
photograph, an archival race shot, or licensed footage of the era is a real plate when it is
genuinely this car or this story, and a driving or performance shot is the right plate for a
performance beat. The rules do not move: no living beings, no visible watermark, correct year and
model, source recorded. Stock or archival material earns its place only when it shows this film's
car or an indistinguishable analogue — same colour, same wheels, same era. A modern wheel, a wrong
colour or any person in frame is a reject.

**A real moving clip is Flow's paid door, not a plate you can slip in.** The clip prices and the
"say the total, then get a yes" rule are [The two free brains](04-the-two-brains.md) and
[Money](12-money-and-other-peoples-media.md). What stops it here is the engine: `BROLL.make` draws
a PNG, no film has a `<video>` layer, and `tools/score.py` counts the `still=` entries in
`scenes.py`. So a clip today is either **motion reference** for a plate you then shoot as a still,
or an **engine change** (a video layer in `scene_builder.py` and the scene contract) that is done
once for every film. It is never a silent substitution for a plate, and when it does become a
layer it animates the plate that is already counted (`first_frame` = that still), is cut to the
scene's own window, and does not buy its way past the 3 s cadence.

Generate them through **one route, chosen once for the film**, in **one open session** for every
plate of that film — the tab, the project window, the 22 s / 10 s check, Flow's `flow_wait` and
the never-re-send rule are [The two free brains](04-the-two-brains.md), and
`python3 tools/brain.py` says which window is open. Repeat the identity block word for word. The
prompts come from the post object in `PLATES.md`; the agent may add the camera and one **outdoor**
setting — road, park, beach, forecourt, boulevard, forest, overlook, coastal road — (Meta's own
prompts run to 45 words) and must never add people, text, watermarks or invented trim. The car is
always a **showroom car**: glossy paint, deep reflections, spotless chrome, clean tyres, never
dust, patina or a studio wall. Look at every plate before anything is built on top of it; if one
drifts, re-shoot just that one.

## 5. Build, render, pass the gates

```bash
npm run render -- $PROJ          # mix → every scene → join → mux → frame scan
npm run lint  -- $PROJ           # 0 errors, 0 warnings
npm run check -- "$PROJ/renders/<title>.mp4"
```

Then the gates in full: lint 0/0, `frame0_blank: false`, `black_frames: []`, `one_frame_pops: []`,
jumps only where the film intends them, −14.2 ±0.3 LUFS with peak ≤ −1.3 dBFS, the frames looked
at yourself — contact sheet, both ends, every seam — and the reveal sheet showing every card
arriving on its word. A film that fails a gate is fixed, not explained, and never shown.

Name it before anyone sees it — the **5–11 word** title in `meta.json` `output` and on the render,
never a working name and never a mood line: [Delivery name](06-pipeline.md#delivery-name).

The caption is written, scored and gated in [The caption pass](05-the-caption-pass.md) — before
step 6, never after.

## 6. Queue it in `data.csv`

```bash
python3 tools/publish.py queue $PROJ --title "…" --description "…" \
  --hashtags " #… #…" --car "1959 Cadillac …" --angle "Size / Looks" \
  --caption-score 88
```

`--caption-score` is the number the second pass produced. The row is the queue entry — a pointer
at the render where it lies, its fingerprint and the caption in three parts ([What a page
holds](15-publishing.md#what-a-page-holds)). `queue` refuses a caption that fails the check, and a
film whose bytes or caption are already in either CSV.

## 7. Publish — only after an explicit yes

```bash
python3 tools/scheduler.py $PAGE --dry-run     # the slots, nothing sent
python3 tools/scheduler.py $PAGE               # upload, book, move the row
python3 tools/scheduler.py $PROJ               # one film: same page queue, narrower
```

**One command, and it is always `tools/scheduler.py`.** "Schedule the next one" means
`python3 tools/scheduler.py video-projects/<page>` with no flags at all: run `--dry-run`, read the
slots, then run it for real. It books the page's whole queue by default, so a batch of ten is one
command and not ten; the flags, the grid and the cadence are [Commands](02-commands.md) and
[Slots](15-publishing.md#slots).

`schedule` uploads from `renders/`, books the next free slot, **moves only the row** into
`uploaded.csv`, and marks both workbooks — the exact cells are [The
workbooks](15-publishing.md#the-workbooks). It will not invent a Tracker row it cannot find.
Uploading is a public, external action: never run the real `schedule` for a film the person has
not said yes to.

## 8. Sync, measure, deliver

```bash
python3 tools/publish.py sync $PROJ     # status, post URL, published_at, workbooks
```

Then `Views (48h)`, `Views (7 days)`, `Star? = Yes` at 50,000+, and `Notes` with the hook and the
fact used, so a Part 2 never repeats them. Deliver the path plus one line on what changed, delete
`renders/cut/` once the film is delivered, and delete unsent drafts outright.

## What never happens, at any step

- **The same film posted twice.** Three gates — `queue`, then `schedule`, then BrightBean: [Never
  upload the same film twice](15-publishing.md#never-upload-the-same-film-twice).
- **A new scheduling script.** `tools/scheduler.py` is the one door; a batch gets flags, not a
  script. Writing `schedule-batch.py`, `book_these.py` or a one-off loop is the anti-pattern, and
  so is editing `scheduled_at` into a CSV to "fix" a slot.
- **A moved or copied film.** The row points at the render; `videos/` and `uploaded/` no longer
  exist and are not to be recreated.
- **An overwritten Car List row.** A repeat after 90 days is a **new row at the bottom**.
- **A second post for one car + angle.** A different angle, or nothing.
- **A build under 80, or a fact that cannot be sourced.** No film is worth an invented number.
- **Anything posted from a Meta AI chat.** It cannot publish; `schedule` is the only door, and
  only after a yes. No credentials, page tokens or app passwords ever go into a prompt, and no
  prompt is sent to a composer that was not checked first.
- **A paid plate, or a published post, without a yes.** Ask first, every time.
- **Their footage edited.** Work on a copy, or render our own layer on top.

---
