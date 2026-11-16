# The two free brains — Meta AI and Google Flow

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

Both routes — **Meta AI** over browser-mcp and **Google Flow** over flow-mcp — are **installed
and working**, and neither uses an API key. They run in **different Chrome profiles**, so one
window can be open while the other is closed. **A closed window is a state, not a broken route.**
`python3 tools/brain.py` checks all three routes and tells you what to open; this page is the
route law, and [the working procedure](03-working-procedure.md) is where it fires.

| Job | Route | Chrome window | Driver |
| --- | --- | --- | --- |
| Score, script, caption, plate prompts | **Meta AI** | the **default** Chrome profile, signed in at `meta.ai` | Browser MCP extension → `tools/meta.py` |
| Plates (stills) | **Google Flow** | flow-mcp's own profile (`~/.flow-mcp/chrome-profile`, CDP 9333) | flow-mcp `flow_agent_images` / `flow_generate` → `tools/shoot_plates_flow.py` (**0 credits**) |
| Short video clips (a performance beat) | **Google Flow** | the same Flow window and project | flow-mcp `flow_generate` `type:"video"` — **spends credits**, needs a yes |
| Voice | **Kokoro** | none — `localhost:8880` | `tools/voice.py`, then `tools/voice_trim.py` — read the `kokoro-natural` skill first |

- **Never say “Meta AI is not connected” or “Flow is not connected” as a finding.** If
  `tools/meta.py --check` says “No browser is connected”, the **default Chrome window is closed**.
  Start it and retry:
  `/opt/google/chrome/chrome --no-first-run --no-default-browser-check https://meta.ai/`. The
  extension is installed; this is not an install problem, not a sign-out, and not a reason to
  reach for an API key.
- Flow reporting `signedIn: true, inProject: false` means exactly that — connected, no project
  open. Open or create one in Flow's Chrome window; a plate batch queued with no project lands
  nowhere. It is **not** a connection failure.
- **`brain.py` exits 0 only when all three routes answer.** The one not-ready state that still
  passes is **Flow signed in with no project open** — it prints `OK` with the fix, because that
  is a normal state. A closed Meta window, a Flow window that is not signed in, a flow-mcp
  server that does not reply, or Kokoro down each print `--` and exit 1. Read the three lines,
  not just the code: `0` still does not mean the batch is ready to shoot.
- Use **one route per film** for its plates. Meta's tab thread or Flow's project is what keeps the
  car consistent; never diagnose one profile with the other.
- Meta fallback stays narrow: only when Meta is open, signed in, and still will not answer (or
  returns broken JSON) does the agent do the work itself in the same shape and say so in
  `plan/META.md`.

## Inside Flow — one project window, two cadences, and what costs credits

Flow is the other free brain, and it is the only place in this engine where **motion** can be
bought. Its images are free, its videos are not, and its pacing is not Meta's. This page carries
the whole surface; these are the laws.

- **`flow_status` first, always.** It answers `signedIn`, `inProject`, the plan and the credits
  left, and returns a `hint` when something must be done by hand. `inProject: false` means Flow is
  connected and no project is open — open or create one in Flow's window and stop there; a batch
  queued with no project lands nowhere. **One project window per film**, opened once and kept
  open: the project is the car's consistency, exactly as the Meta chat tab is.
- **Images, two ways, both 0 credits and both in that one project.** `flow_agent_images` hands up
  to 50 image scenes to Flow's own Agent mode, which renders them in parallel and enriches each
  prompt itself — this is what `tools/shoot_plates_flow.py` calls, and the route for a whole
  film's plates. `flow_generate` with `type:"image"` renders **one scene at a time**, your prompt
  verbatim, and is the route when a plate must be exact (the hero, a badge). Both draw on Nano
  Banana (2.1 today) and neither spends a credit.
- **Never re-send, in either cadence.** For Meta that means the 22 s / every 10 s page check. For
  Flow it means `flow_wait`: a call comes back inside ~40 s even while Flow is still working, so
  call `flow_wait` again until `finished: true`, and if a reply is `still_working` hand its
  `task_id` to `flow_wait` instead of repeating the call. A scene that failed comes back named in
  the job note and is re-made with `flow_retry` **by job id**, under its own scene number — never
  by queueing the same prompt again by hand. Scenes run one at a time with 25–70 s human-like
  pauses.
- **Video is the paid door.** `flow_generate` with `type:"video"` makes a clip in the open
  project: 9:16 (or 16:9) only, `duration` 4/6/8/10 s on Omni, fixed 8 s on Veo. **Omni 1.1 Flash
  is 7 credits at 4 s and 12 at 8 s; Veo 3.1 is 10 (Lite), 20 (Fast), 100 (Quality) per clip**,
  and `variants` multiplies that. `max_credits` (default 25) makes Flow skip a scene whose quote
  is dearer instead of spending it. So: read the quote, say the total out loud, and **get a yes
  before queueing** — the same rule as every other paid route in this engine.
- **Consistency is free — use it instead of paying for a re-roll.** `flow_character` draws and
  saves a reusable product portrait (a car counts) at no cost, `first_frame` / `last_frame`
  animate between two stills that were free to make, `reference_images` (max 3) holds one car
  across scenes, `flow_continue` starts the next clip on the last frame of the one before, and
  `flow_edit` relights or re-dresses a clip already in the project. Flow's composer takes
  references **or** frames on a video scene, never both; with frames set the references are
  skipped and the job says so.
- **Free plumbing exists; use it before regenerating.** `flow_download` pulls media already in the
  project — including the 1080p/2K upscale — for 0 credits; `flow_transcribe`, `flow_captions`,
  `flow_assemble` and `flow_narrate` are local and free. The small tools are free too:
  `flow_assets` lists the project's media, `flow_cancel` stops a job that has not started,
  `flow_techniques` returns ready-made camera and product-shot phrases, `flow_voices` lists the
  TTS voices, `flow_characters` / `flow_character_edit` manage the saved portraits, and
  `flow_trash` deletes one asset recoverably. The page's voice still comes from
  **Kokoro** (one voice across the channel, and its trimmed word times are the clock);
  `flow_narrate` is not a substitute for it.

```bash
python3 tools/flow_call.py flow_status                       # signed in? project? credits?
python3 tools/flow_call.py flow_wait '{"timeout_seconds":40}'  # again until finished: true
python3 tools/flow_call.py flow_generate '{"project":"<slug>-beats","scenes":[{"type":"video",
  "prompt":"…","aspect_ratio":"9:16","duration":4,"model":"Omni 1.1 Flash","max_credits":12}]}'
```

## Meta AI does the thinking — the agent drives it

**Meta AI is the default brain for the batch**, through Browser MCP in the person's own signed-in
**default Chrome** (where the extension is installed) — no API key, nothing to pay for. The agent
drives it and edits nothing it says. It does four jobs, always these four: **pick and score the
topic, write the script, write every plate prompt, and write the caption** — a viral title, a long
engaging description that talks to the viewer and ends on a call to action, and four or five
hashtags.

**One chat, one film — binding, no exceptions.** Every image of one film is generated in **the
same browser session**: for Meta AI that is the *same chat tab*, opened once and kept open for the
whole film; for Flow it is the *same project window*. Never open a new chat, tab or window per
image, and never close the old one between images — the thread is the context, and shots made in
one conversation read as one car. A second tab is allowed only when a *different* site is
genuinely needed (Flow instead of Meta AI), never one tab per image. Close the session only once
that film's last plate is downloaded.

**One prompt at a time, and never a re-send.** The cadence inside that one chat is strict: send a
prompt **once**, then check the page at **22 s** and every **10 s** after that until *that* image
is finished, download it, and only then send the next prompt. Meta normally draws inside 20 s, so
the first check usually finds it. A prompt is **never** sent again because the image has not
appeared yet — waiting is the fix, and re-sending the same prompt is exploiting the free route. If
an image never arrives, stop and report it; do not fire the prompt again. The new picture is
recognised against the images already on the page (the tool's `seen` set), **never** by opening a
clean chat so that "the newest image" is unambiguous.

```bash
python3 tools/meta.py --check                     # tab list + is the composer there
python3 tools/meta.py ask --prompt-file "video-projects/<page>/META PROMPT.md" \
  --out video-projects/<page>/plan/META-batch-<date>.md --timeout 540
```

- The prompt lives at `video-projects/<page>/META PROMPT.md`. Everything above its
  `<!-- SEND BELOW -->` line is for us; only the text under it is sent. Change nothing but the
  **INPUT** block per batch: candidates, page numbers, posts wanted, angles used so far.
- Meta answers inside `<<<PLAN>>>` … `<<<END>>>`, as one JSON object: the five-line `brief` block
  when a brief was given; every candidate scored (with `GO` / `REJECT` and a reason); and for each
  `GO` a full post — title, description, hashtags, script with word count, `voice` / `speed`, beat
  timings, sourced facts, an identity block, one image prompt per 3 s of film, and three
  `future_angles` for the same car.
- Browser MCP cuts replies at 10 000 characters, so the JSON must stay compact; the driver reads
  the answer back in slices and refuses to press Enter unless the composer holds the text.
- **Fallback**: only if Meta is open, signed in, and still will not answer — or the JSON comes
  back broken — the agent does the same work itself in exactly the same shape and says so in
  `plan/META.md`. A closed Chrome window is not that case; open it. The film never waits on the
  tool.
- Meta's facts are **proposals**. Every number is checked against a source before it reaches a
  script, and the check is written into `plan/FACTCHECK.md` (`0 invented facts` still holds).
- Meta AI is a chat window, not the page. **Nothing there can post.** Publishing stays `schedule`,
  behind an explicit yes. Never paste credentials, app passwords or page tokens into it.

These four bits of text are then split into the film folder — `VIRAL.md` (scores and the why),
`SCRIPT.md` (read, beats, caption), `FACTCHECK.md` (sourced numbers), `PLATES.md` (identity block
and six prompts) — so the film carries its own evidence.
