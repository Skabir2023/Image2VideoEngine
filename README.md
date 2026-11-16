# image2videoEngine — vintage car reels

An engine for making short vertical car films for **Vintage Motor House**: six AI stills of one
car, motion graphics cut exactly to the spoken words, real engine sound, one MP4 ready for
Facebook.

The engine (drawing library, fonts, sound, render scripts) is here at the root and is shared.
Inside `video-projects/` the first folder is the **page** (the Facebook channel), and inside that
each **film** has its own folder, holding that film's pictures, voice, scenes, plan and renders —
nothing of the engine.

```
image2videoEngine/                   ← the engine: run every command from here
  assets/  sound/  tools/  node_modules/
  video-projects/
    vintage-motor-house/             ← the page: rules, workbooks, queue
      1969-ford-mustang-boss-429/    ← the reference film: 18.6 s, 1080×1920
      1957-cadillac-eldorado-brougham/  ← a film: 20.0 s, 1920×1080
```

**If an AI model is working here, it starts with `AGENTS.md`.** This file is the short human
version.

## Watch it

- `video-projects/vintage-motor-house/1969-ford-mustang-boss-429/renders/1969 Ford Mustang Boss 429 - Rarest.mp4`
  — the finished film (published 14 Nov 2026)
- `…/1969-ford-mustang-boss-429/qa/final-sheet.jpg` — the six shots on one sheet

## Rebuild it

You need **Node 22 or newer**, **ffmpeg**, **python3** (with numpy), and **Chrome** on the
machine. Everything else is inside the folder.

```bash
npm install                                  # only if node_modules/ is missing
FILM=video-projects/vintage-motor-house/1969-ford-mustang-boss-429
npm run render -- $FILM                      # mix → scenes → join → mux → check
```

A full run takes a couple of minutes and rewrites that film's render, named by its `output` in
`meta.json`.

```bash
python3 $FILM/audio/build_final.py           # only the sound, ~20 s
python3 tools/scene_builder.py $FILM         # rewrite scenes + index from the film's scenes.py
npm run lint -- $FILM                        # HyperFrames check, needs 0 errors
npm run check -- "$FILM/renders/1969 Ford Mustang Boss 429 - Rarest.mp4"
```

`npm run render` reads the film's `meta.json`, so it works for any film folder without edits.

## Starting on another computer

The repo carries everything that is not generated: the engine, the sound library, the fonts, the
templates, the page's rules and workbooks, the queue and ledger, and every film's sources — its
scenes, script, plan, plate prompts and measured word times.

Three things are deliberately absent, and each has its own way back:

| Not in the repo | Why | Back |
| --- | --- | --- |
| `node_modules/` | 700 MB of dependencies | `npm install` |
| `.env` with `BRIGHTBEAN_API_KEY` | a secret | recreate it (see *Publishing*) |
| `stills/`, `renders/`, voice WAVs | generated media | re-shoot the plates from each shot's `stills/<shot>.images.json`, then re-take the voice with `tools/voice.py` |

So a fresh clone can write, shoot, voice, render and schedule the next film. What it cannot do is
re-render a past film untouched — the stills and the voice take are not in history.

## What to post next

Two workbooks decide it (they live in `video-projects/vintage-motor-house/`):

- `Vintage-Motor-House-Car-List-300.xlsx` — 312 cars from 1940–1990. Pick from `Used? = No`,
  and set it to `Yes` with the angle and date once the film is finished.
- `Vintage-Motor-House-Tracker.xlsx` — one row per post: car, angle, score, views, Star.

`python3 tools/publish.py pick video-projects/vintage-motor-house` prints the next ten and says how
many are still unused, so you never have to count rows by hand.

Work in batches of ten. Rotate the six angles — Size / Looks, Price / Rarity, Engine / Speed,
Secret Story, Why It Failed, Why It Became Legend — so ten luxury cars never run in a row. A car
can come back after 90 days, but only with a different angle, and it gets a **new row at the bottom
of the list** — the old row stays as the record of what that angle did. A post past 50,000 views
gets `Star? = Yes` and earns a Part 2 after 90 days.

That is 936 posts before one angle repeats: about 15 months at two a day.

## Make the next reel

The order is fixed; `.agents/manual/03-working-procedure.md` is the same eight steps with every
command and gate spelled out.

1. **Choose ten, then let Meta score them.** `pick` lists the next cars with `Used? = No`;
   cross-check each car and angle against the Tracker. Name a car, or describe the story you want
   ("a barn-find Daytona", "something about giant fins"), and that description becomes the brief
   instead: the car you named is the subject and the reel is built from your detail. The candidates go to **Meta AI** through
   Browser MCP (`python3 tools/meta.py ask --prompt-file "…/META PROMPT.md"`), which scores each
   one, picks the angle and writes the script, the caption and one image prompt per 3 seconds for
   the ones that pass. Under 80: another angle, then another car — nothing is built below 80. Every number Meta
   proposes is checked against a source and written into `plan/FACTCHECK.md`. If Meta is open,
   signed in, and still will not answer, the agent does the same work in the same shape and says
   so — a closed Chrome window is fixed, not worked around.
2. **Make the folder.** `python3 tools/new_film.py video-projects/vintage-motor-house/<car-slug>
   --title "…"` lays it down from `templates/film/`: the tree, a `meta.json` carrying the new car's
   names, a `scenes.py` skeleton that refuses to build until it has real measurements, and the
   reference `audio/build_final.py` (it carries the current seam and sound law). Then fill the
   numbers and start the plan files. Same car, new angle → a new folder; never a copy of the page.
3. **Voice first.** One Kokoro take at `speed: 1.2`, transcribed, and the word times copied into
   the scene table and the sound build by hand — the build does not read the transcript, so those
   numbers are the truth. Cuts land on the transcribed words.
4. **Draw the plates — one per 3 seconds.** Six fixed angles first (front ¾, side, rear, engine
   bay, interior, wheel), then close-ups to fill the cadence: 6 plates for 18 s, 8 for 24 s. All
   of them through **one route**: Meta AI in the one tab, or Google Flow through flow-mcp (free
   images on Nano Banana). Both are free and installed; `python3 tools/brain.py` says which window
   is open. **All of a film's plates come out of that one open session** — the same Meta chat tab
   or the same Flow project window, never a fresh chat per image — one prompt at a time, sent once
   and never re-sent: in the Meta tab check at 22 s then every 10 s until the plate is done; in
   Flow, call `flow_wait` until it says finished, and re-make only a failed scene by its job id.
   Prompts come from `plan/PLATES.md`, identity block kept word for word, no people, animals or
   text, each prompt saved beside the plate.

   Flow can also generate a **short video clip**, which costs credits (7–12 for a 4–8 s Omni clip,
   10–100 for Veo), so it needs a yes first — and no scene can play one yet: the films are built
   from stills with camera moves, and the gate counts stills. See
   `.agents/manual/03-working-procedure.md` → *4. Plates*.
5. **Build, render, check.** `npm run render -- video-projects/vintage-motor-house/<car-slug>`,
   then lint, the frame scan, the loudness and the frames themselves — and name the file after
   its title (5–11 words) before anyone sees it.
6. **Queue it.** Write the caption, score it out of 100 and rewrite anything under 80, then `queue`
   with its title, long description, hashtags, `--car`, `--angle` and `--caption-score`. The check
   runs first (`tools/caption.py`), so a thin caption is refused; a passing one puts one row in
   `data.csv`, pointing at the render where it lies.
7. **Publish it, after a yes.** `python3 tools/scheduler.py video-projects/vintage-motor-house
   --dry-run` shows the slots — the next free one of your four hours (7 am, 1 pm, 7 pm, 1 am); the
   same command without `--dry-run` uploads, books them, moves those rows to `uploaded.csv` and
   marks both workbooks. One scheduler, for you and for the AI.
8. **Sync and measure.** `sync` brings back the post URL and the date; fill views at 48 h and 7
   days, `Star?` at 50,000+. Then send the file with one line on what changed and tidy the drafts.

`.agents/manual/` has the exact timings (`07-timing-law.md`), the sound law (`09-sound-law.md`),
the change-coupling table (`16-changing-things.md`) and the known traps (`17-pitfalls.md`). One
folder holds one film; the engine is shared by all of them.

## The two free brains

Both routes are **installed and working**, with no API key and nothing to pay for **on the image
and voice routes** — Flow only spends credits if you ask it for video. They run in two different
Chrome profiles, so one window can be open while the other is closed — that is a state, not a
broken route.

| Job | Route | What to run |
| --- | --- | --- |
| Score, script, caption, plate prompts | Meta AI in the **default** Chrome (Browser MCP extension) | `python3 tools/meta.py ask …` |
| Still plates | Google Flow in flow-mcp's own Chrome (CDP 9333, 0 credits) | `python3 tools/shoot_plates_flow.py …` |
| Short video clips (credits — ask first) | the same Flow window and project | `python3 tools/flow_call.py flow_generate …` |
| Voice | Kokoro on `localhost:8880` | `python3 tools/voice.py …` |

One command tells you the truth about all three:

```bash
python3 tools/brain.py
```

If it says browser-mcp has no browser connected, the default Chrome window is closed. Start it
(no `--user-data-dir`, so the profile with the extension is used) and rerun:

```bash
/opt/google/chrome/chrome --no-first-run --no-default-browser-check https://meta.ai/
```

If Flow says `signedIn: true, inProject: false`, Flow is connected and simply has no project open
— open or create one in Flow's Chrome window. Neither case is an install problem, and neither is
a reason to use a paid API. The full explanation is in `.agents/manual/04-the-two-brains.md`.

## Publish it

Posting goes through **BrightBean** (Facebook today). The queue belongs to the page, so it sits
beside the films, not inside one of them:

```
video-projects/vintage-motor-house/
  data.csv      the queue: one row per finished film, with its caption
  uploaded.csv  everything booked, with its slot
  1969-ford-mustang-boss-429/   one film
  1957-cadillac-eldorado-brougham/
```

You still name the film on the command line; the row goes to the page. There is no copying and no
`videos/` folder: a row points straight at the finished film in its own `renders/`, so the queue
holds the title, the description, the hashtags and the file in one line.

The key lives in `image2videoEngine/.env` (or `~/.env_brightbean`) as
`BRIGHTBEAN_API_KEY=…`. It is never needed inside a project.

```bash
python3 tools/publish.py queue video-projects/vintage-motor-house/1969-ford-mustang-boss-429 \
  --title "1969 Ford Mustang Boss 429 - The Rarest One" \
  --description "They only built 1,359 of these. And it was a NASCAR engine with plates." \
  --hashtags "#Mustang #ClassicCars #Boss429 #1969" \
  --car "1969 Ford Mustang Boss 429" --angle "Price / Rarity"

python3 tools/publish.py status video-projects/<page>/<film>
python3 tools/scheduler.py video-projects/<page> --dry-run  # the slots, nothing sent
python3 tools/scheduler.py video-projects/<page>            # upload and book the page's queue
python3 tools/publish.py sync video-projects/<page>/<film>                 # get the post URL
```

**`tools/scheduler.py` is the scheduler, and the page has four hours a day: 7:00 am, 1:00 pm,
7:00 pm and 1:00 am.** They are in your local time and live in
`video-projects/vintage-motor-house/schedule.json`, so asking for a schedule needs no flags:

```bash
python3 tools/scheduler.py video-projects/vintage-motor-house --dry-run   # the next slots
python3 tools/scheduler.py video-projects/vintage-motor-house             # book them
```

It takes the **next free one** of those four, then the one after that for the next film, and it
never hands out a slot that `uploaded.csv` already holds — so four films go out 7 am, 1 pm, 7 pm
and 1 am across two days. Nothing is booked within 15 minutes of now, because the upload takes a
moment. For a one-off time: `--daily "09:30,21:30"`, `--tz`, `--lead 5`, `--start-at <ISO>`,
`--interval 60`, `--limit 3`. Ask the AI to schedule and it runs this same file — no new script
per batch, and one written for a batch should not be trusted.

`queue` writes the caption and the film's address as one row. `schedule` uploads it from where it
lies, books the next free hour of that grid, and moves the **row** from
`data.csv` to `uploaded.csv` — the film never moves — then marks both workbooks: `Used? = Yes`
with angle and date in the Car List, `Posted` in the Tracker. `sync` reads the post back and fills
in the URL once it is live.

**A film can never go out twice.** Each row carries a fingerprint of its file; `queue` refuses a
film that is already queued, `schedule` skips one that is already booked (even under a different
title), and a retried run adopts its own earlier post instead of making a second one.

The Car List and Tracker live at the page level, next to `data.csv`, and that is where the marks
land. One copy per page — never one per film, or the calendar splits in two.

Nothing is uploaded or scheduled without your yes for that film.

## What is where

The engine:

| Path | What it is |
| --- | --- |
| `AGENTS.md` | the manual's front door: the layout, the read order, the index of its sections |
| `.agents/manual/` | the manual itself, one file per section (`03-working-procedure.md` …) |
| `assets/*.js`, `assets/fonts/` | the drawing engine, GSAP and the local fonts |
| `sound/kit.json` | the four sounds a reel uses, and the alternatives each story angle can pick |
| `sound/engines/`, `sound/SFX Sound Effects/` | the library: engine recordings and one-shots for the closing hit |
| `tools/sound.py` | hear a recording's shape, cut a sound out at the right level, check the kit |
| `tools/brain.py` | one preflight for Meta AI, Flow and Kokoro |
| `tools/meta.py` | Meta AI through browser-mcp, in the default Chrome |
| `tools/flow_call.py`, `tools/shoot_plates_flow.py` | Flow through flow-mcp, in its own Chrome (free images; video clips cost credits) |
| `tools/shoot_plates.py` | plates through Meta AI (browser-mcp) |
| `tools/voice.py` | one Kokoro take and its transcript, with `am_michael` / `am_adam` |
| `tools/render-all.sh` | the whole pipeline for one film |
| `tools/scan.py` | blank / black / one-frame-pop scan of any render |
| `templates/` | the film skeleton a new folder starts from — one structure, because the look is fixed |
| `tools/new_film.py` | makes a film folder from `templates/<name>/`, so nothing is hand-copied |
| `tools/scene_builder.py` | writes every film's scenes and `index.html` from its `scenes.py` table |
| `tools/scheduler.py` | the one scheduler: books a page's queue, or one film, and nothing else |
| `tools/publish.py` | pick, queue, schedule, status and sync for one film, through its page |
| `tools/brightbean.py`, `tools/excel.py` | BrightBean API calls, and the workbook cell writes |
| `video-projects/<page>/` | one folder per page: rules, workbooks, queue, and its films |

A page — `video-projects/vintage-motor-house/`:

| Path | What it is |
| --- | --- |
| `MASTER PROMPT.md` | the posting rules every film on the page follows |
| `META PROMPT.md` | those rules as one prompt for Meta AI; only its INPUT block changes per batch |
| `plan/META-batch-<date>.md` | Meta's raw answer for a batch — scores, scripts, captions, prompts |
| `Vintage-Motor-House-Car-List-300.xlsx` | the 312 cars, with `Used?` and what was done |
| `Vintage-Motor-House-Tracker.xlsx` | one row per post: car, angle, score, views, Star |
| `backup/` | those workbooks as they were before each edit |
| `data.csv`, `uploaded.csv` | the queue and the ledger — rows only, no video copies |

A film — `video-projects/vintage-motor-house/1954-mercedes-300sl-gullwing/`:

| Path | What it is |
| --- | --- |
| `meta.json` | output name, frame rate, scene order — what the render reads |
| `index.html` | the twelve scenes and the mix as one 19.4 s film, for preview — written by the builder |
| `scenes.py` | **data only** — the scene table (frames, stills, camera, cards, word times); `tools/scene_builder.py` writes the scenes from it |
| `compositions/s01…s12.html` | the scenes |
| `stills/` | the six pictures (1080×1920) and how each was prompted |
| `audio/paragraph/line-01-v120.wav` | the narration, one take at 1.2× |
| `audio/paragraph/transcript.json` | the measured word timings every cut and reveal comes from |
| `audio/build_final.py` | builds the mix from the voice and the engine files |
| `audio/final-audio.wav` | the master mix that gets muxed onto the picture |
| `plan/` | the paper trail: viral score, facts, prompts, script, beats, timeline |
| `qa/` | contact sheets checked before sending |
| `renders/` | the finished film, named after its title |

## The sound

Four sounds, and the car never talks over a word:

1. **the start** — the engine catching before the narrator opens his mouth;
2. **the bed** — a running idle under the whole film, dropped 30 dB the moment a word begins;
3. **the roar** — two seconds after the last word, the car answering the final question;
4. **the hit** — one low thud under the closing card.

Which recording fills each slot is a menu, and the story angle chooses from it: a car that
fails can start with an engine that never catches, a luxury car gets a quieter idle. The
menu is `sound/kit.json`, the levels are written into each film's `audio/build_final.py`, and
`python3 tools/sound.py list` prints the lot. Measured the same way every time: −14.2 LUFS,
true peak under −1.3 dBFS.

## Licence

The engine recordings are from Pixabay (Pixabay Content License) and the closing hit from
Mixkit (Mixkit Free License): free for commercial use, no attribution, no royalties, but the
audio files themselves may not be redistributed on their own or claimed as your own recording.
Inside the video is fine. One pack of one-shots came with no licence file, so `sound/kit.json`
marks it `unknown` and no film defaults to it. Details in `sound/README.md`.
