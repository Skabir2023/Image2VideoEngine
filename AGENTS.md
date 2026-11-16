# AGENTS.md — image2videoEngine

This folder is the **reel engine** for the Facebook page *Vintage Motor House*: vertical
(1080×1920, 60 fps) narrated vintage-car reels made from one AI still every three seconds,
HyperFrames motion graphics cut to the spoken words, and a real engine recording for sound.

The engine is shared and never copied: one `node_modules`, one set of fonts, one stage, one sound
library. Under `video-projects/` the first level is the **page**, the second is the **film**: one
folder per Facebook page, one folder per film inside it. The page folder holds what belongs to the
channel — the posting rules, the workbooks, the schedule, the queue — and each film folder holds
only that film's pictures, voice, scenes, plan and render.

```
image2videoEngine/                    ← the engine. Run every command from here.
  AGENTS.md / README.md               the map, and the plain-words guide
  .agents/manual/                     the manual itself: one file per section
  assets/                             stage.js, broll.js, text.js, seams.js, kit-config.js, fonts.css, gsap, fonts/
  sound/kit.json                      the four sound slots: recording, slice, level, alternates
  sound/engines/                      shared engine recordings (Pixabay)
  sound/SFX Sound Effects/            one-shots for the closing hit (mixed provenance)
  tools/                              brain.py, meta.py, flow_call.py, shoot_plates*.py, voice.py, voice_trim.py, sound.py, scene_builder.py, new_film.py, render-all.sh, scan.py, score.py, scheduler.py, publish.py + brightbean.py + excel.py + caption.py
  video-projects/
    vintage-motor-house/              ← the page (the Facebook channel)
      MASTER PROMPT.md                the posting rules, binding for every film on the page
      Vintage-Motor-House-*.xlsx      the page's calendar: 312 cars + the Tracker
      schedule.json                   the page's posting hours: 07:00, 13:00, 19:00, 01:00
      data.csv / uploaded.csv         the page's queue and ledger
      1969-ford-mustang-boss-429/     ← a film: the reference build (18.6 s, 1080×1920)
      1957-cadillac-eldorado-brougham/  ← a film (20.0 s, 1920×1080)
        meta.json scenes.py index.html compositions/ stills/
        audio/ plan/ qa/ renders/
```

`video-projects/vintage-motor-house/1969-ford-mustang-boss-429/` is the **reference build**: one
finished film, its sources, its measurements and its plan. Every other car is a new folder at the
same depth, made the same way — but that film predates `tools/scene_builder.py`, so its scenes
come from a film-local `build_scenes.py` and it has no `scenes.py`. Copy the shape, not that file.
A second page (another channel) is a new sibling of `vintage-motor-house/` with its own rules,
workbooks and queue — films never mix across pages.

You are the operator. You pick the car, check the facts, build the scenes, make the voice, mix the
sound, render, verify, and write the caption. Then, once they approve that film, you queue it and
book it on the page. The person you work with is a creator: they name a car and get a video plus a
caption. Never ask them to edit code, run commands or choose between libraries — decide, build,
show. Work in the order of [the working procedure](.agents/manual/03-working-procedure.md), in
batches of ten, and do not skip a step because a film looks easy.

---

## Read in this order before touching anything

0. This file, top to bottom — the layout, the index, and the one section file your job needs. [The
   working procedure](.agents/manual/03-working-procedure.md) is the order every batch runs in;
   nothing later in the manual replaces it.
1. `README.md` — the commands and the folder map, in plain words. [The two
   brains](.agents/manual/04-the-two-brains.md) is the route guide: Meta AI over browser-mcp
   (default Chrome) and Google Flow over flow-mcp (its own Chrome), both free, and how to tell a
   closed window from a broken integration.
2. `video-projects/vintage-motor-house/MASTER PROMPT.md` — the posting rules. **Binding for every
   reel.** Viral-score rubric, fact-check box, the plate cadence and its six fixed angles, the
   no-living-beings rule, and the exact three-line caption format. The `.text` file next to it is
   the same document. Its machine-readable twin is `META PROMPT.md` in the same folder: the prompt
   we actually send to Meta AI, which asks for those rules in one JSON object. If a rule ever
   differs between them, `MASTER PROMPT.md` wins and `META PROMPT.md` is corrected to match.
3. `video-projects/vintage-motor-house/1969-ford-mustang-boss-429/plan/TIMELINE.md` — every
   measured number of the reference build: cuts, word times, frame counts, sound levels.
4. `…/1969-ford-mustang-boss-429/plan/` — VIRAL, FACTCHECK, PROMPTS, SCRIPT, BEATS: how the
   reference build was scored, checked, drawn and written.
5. `video-projects/vintage-motor-house/Vintage-Motor-House-Car-List-300.xlsx` and `…-Tracker.xlsx`
   — the production calendar: which cars are left, what has been posted, which angle is due next.
   Both are read before a batch and written after every film; see [the two
   spreadsheets](.agents/manual/18-workbooks.md), and [Publishing a finished
   film](.agents/manual/15-publishing.md) for the cells `schedule` and `sync` fill in themselves.

If these files disagree about a **rule**, this manual and `MASTER PROMPT.md` win. If they disagree
about a **number**, that film's `plan/TIMELINE.md` is the measurement and wins.

---

## The manual — one file per section

The manual used to be this one file. It is now one file per section under `.agents/manual/`, so a
job reads only its own section instead of the whole manual — **open the file for the task in front
of you, not all twenty.** Every file starts with a line pointing back here.

**Plan the batch**

- [Choosing the next car](.agents/manual/14-choosing-the-next-car.md) — the Car List rule:
  `Used?`, 90 days, a different angle, a new row, a batch of ten.
- [The two spreadsheets](.agents/manual/18-workbooks.md) — the Car List and the Tracker in detail,
  the six angles, the batch maths, reading `.xlsx` without `openpyxl`.
- [Content rules](.agents/manual/11-content-rules.md) — score before script, no invented facts,
  the story completes, the plate rule, the caption's exact shape. **Binding, from
  `MASTER PROMPT.md`.**
- [Money and other people's media](.agents/manual/12-money-and-other-peoples-media.md) — free
  routes only for images and voice; name the total and **ask before anything paid**; never edit
  their footage.

**Build the film**

- [The working procedure](.agents/manual/03-working-procedure.md) — the one sequence: steps 1–8 of
  a batch, and what never happens at any step. Read it whole, in order.
- [The two free brains](.agents/manual/04-the-two-brains.md) — Meta AI in the default Chrome, Flow
  in its own: one session per film, send once and never re-send, no credit spent without a yes.
- [Commands](.agents/manual/02-commands.md) — every command from the engine root, and
  `tools/scheduler.py` as the **one** scheduling door.
- [The pipeline](.agents/manual/06-pipeline.md) — the ten steps at film detail, and the delivery
  name (5–11 words, the same words as the caption's first line).
- [Timing law](.agents/manual/07-timing-law.md) — the voice is the clock: `LEAD` is the start's
  length, cuts 65 ms before a word, exact frame counts, nothing parsed at build time.
- [Writing a scene](.agents/manual/08-composition.md) — the composition contract, the `scenes.py`
  fields, the blur-cut seam, the numbers law.
- [Sound law](.agents/manual/09-sound-law.md) — four slots, the duck built from the transcript,
  `TAIL = 0.030`, −14.2 LUFS on the delivered MP4.
- [Style of this engine](.agents/manual/10-style.md) — the ground, type, card sizes, kicker, scrim
  every reel shares.
- [The caption pass](.agents/manual/05-the-caption-pass.md) — write, score to 80, the grounding
  test, then let `queue` gate it.

**Finish and post**

- [Verification gates](.agents/manual/13-verification-gates.md) — score, lint 0/0, the frame scan,
  the contact sheet, the reveal sheet, the audio, the name. Never show a film before these pass.
- [Publishing a finished film](.agents/manual/15-publishing.md) — the page-level queue and ledger,
  the three anti-duplicate gates, the slots grid, the workbooks. **Ask for a yes before
  `schedule`.**

**Keep it honest**

- [Changing things](.agents/manual/16-changing-things.md) — what else must move when a duration, a
  voice take, a still, a sound or a caption changes.
- [Known pitfalls](.agents/manual/17-pitfalls.md) — the traps with no other home, and the pointer
  to where the rest are written down.
- [Requirements](.agents/manual/01-requirements.md) — Node 22+, ffmpeg, python3, Chrome; what the
  repo carries and what it deliberately does not.
- [Inside one film](.agents/manual/19-inside-one-film.md) — naming, independence, what to delete
  after a delivery.
- [File map](.agents/manual/20-file-map.md) — every path in the engine, the page and one film.

A rule in a section file binds exactly as it did inside this one — the index is only a map. When a
task touches a rule two files share, the file that owns the rule wins and the other links to it.
