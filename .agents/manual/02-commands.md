# Commands

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

Every command runs from the engine root and takes the **film** folder. The page is
`video-projects/<page>/` (the channel, e.g. `vintage-motor-house`) and the film is the folder
inside it (e.g. `1969-ford-mustang-boss-429`).

```bash
npm run render -- video-projects/<page>/<film>    # mix → every scene → join → mux → frame scan
npm run lint -- video-projects/<page>/<film>      # hyperframes lint — 0 errors, 0 warnings
npm run check -- video-projects/<page>/<film>/renders/<out>.mp4   # blank/black/pop scan
python3 tools/score.py video-projects/<page>/<film>   # the 80 gate, facts, beats, words, plates, reveals, sound
python3 tools/sound.py list                          # the four sound slots and what resolves
python3 tools/sound.py probe <name>                  # duration, levels, 0.25 s envelope
python3 tools/sound.py cut <slot> --out /tmp/x.wav   # that slot, levelled, to audition

python3 tools/scene_builder.py video-projects/<page>/<film>   # rewrite compositions/*.html + index.html
python3 tools/voice_trim.py video-projects/<page>/<film>      # cap every pause at 0.22 s, re-measure the words
python3 video-projects/<page>/<film>/audio/build_final.py # rebuild that film's audio/final-audio.wav

python3 tools/brain.py                                   # Meta AI + Flow + Kokoro: one preflight
python3 tools/voice.py video-projects/<page>/<film>      # Kokoro take + transcript (--voice am_adam)
python3 tools/shoot_plates.py video-projects/<page>/<film>       # plates via Meta AI (browser-mcp)
python3 tools/shoot_plates_flow.py video-projects/<page>/<film>  # plates via Flow (flow-mcp, 0 credits)
```

Publishing (needs `BRIGHTBEAN_API_KEY`) — steps 6–8 of [the working
procedure](03-working-procedure.md), with the detail under [Publishing a finished
film](15-publishing.md):

```bash
python3 tools/publish.py pick video-projects/<page>                        # the next 10 cars
python3 tools/publish.py queue video-projects/<page>/<film> --title "…" --description "…" \
  --hashtags "…" --car "1969 Ford Mustang Boss 429" --angle "Price / Rarity"
python3 tools/publish.py status video-projects/<page>/<film>     # queue, ledger, last slot
python3 tools/scheduler.py video-projects/<page> --dry-run      # the slots, nothing sent
python3 tools/scheduler.py video-projects/<page>                # upload, book the rows
python3 tools/publish.py sync video-projects/<page>/<film>                 # published? url? sheets
```

**Scheduling is `tools/scheduler.py`, always** — the person and the agent run the same one file.
It takes a **page** (books everything queued there, in `data.csv` order) or a **film** (the same
page queue), and forwards every flag to `publish.py schedule`: `--limit`, `--start-at`,
`--start-delay`, `--start-min` / `--start-max`, `--gap-min` / `--gap-max`, `--interval`,
`--dry-run`, `--no-excel`. It is a door, not a second scheduler: never write a scheduling script
for a batch, and never edit a slot into `data.csv` by hand.

`npm run render` reads the project's `meta.json` for the scene order, frame rate and output name,
so a film is rendered by its folder alone. One scene only (fast loop while designing):

```bash
npx hyperframes render -c video-projects/<page>/<film>/compositions/s02-engine.html \
  -o video-projects/<page>/<film>/renders/cut/s02-engine.mp4 \
  --fps 60 --quality high --video-frame-format png
```

Preview the whole film as one timeline: `npx hyperframes preview video-projects/<page>/<film>`
(plays that project's `index.html`). The studio serves the project folder, while the scenes load
the shared library as `assets/…` from the engine root — so a studio preview can look unstyled. The
render is the truth; check stills with single-scene renders instead.

---
