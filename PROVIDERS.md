# The two free brains — browser-mcp and flow-mcp

Both routes are **installed and working** on this machine. Neither one uses an API key, a page
token, an app password or a paid credit. They run in **two different Chrome profiles**, so one
window can be open while the other is closed.

**A closed window is a state, not a broken integration.** No agent may report “Meta AI is not
connected” or “Flow is not connected” as a conclusion. Name the window that is closed, open it,
and carry on.

| Job | Route | Chrome window | Driver | Cost |
| --- | --- | --- | --- | --- |
| Batch research, viral score, script, caption, plate prompts | **Meta AI** | the **default** Chrome profile, signed in at `meta.ai` | Browser MCP 2.x extension ↔ `npx -y @browsermcp/mcp@latest`, through `tools/meta.py` | free |
| Photoreal still plates | **Google Flow** | flow-mcp's **own** profile (`~/.flow-mcp/chrome-profile`, CDP port 9333) at `flow.google.com` | flow-mcp stdio server (`/home/openclaw/flow-mcp/dist/index.js`), `flow_agent_images` / `flow_generate type:"image"`, through `tools/flow_call.py` and `tools/shoot_plates_flow.py` | **0 credits** (Nano Banana, 2.1 today) |
| Short video clips | **Google Flow** | the same Flow window and project | `flow_generate type:"video"`, through `tools/flow_call.py` | **credits** — Omni 1.1 Flash 7 (4 s) / 12 (8 s), Veo 3.1 10 / 20 / 100 |
| Narration | **Kokoro** | none — local HTTP server on `localhost:8880` | `tools/voice.py`, then `tools/voice_trim.py` | free, local |

There is no third route. Do not substitute an image API, an LLM API or a paid generator because
one of these windows is closed; free routes only, and ask before anything paid.

## One preflight for everything

```bash
python3 tools/brain.py
```

It reports Meta AI (browser-mcp), Flow (flow-mcp) and Kokoro side by side and names the exact
next action for anything that is not ready. A missing Flow project is reported as a normal state
and still exits 0; the command exits non-zero only when a route is disconnected or its server is
down. `python3 tools/brain.py` is the first command of a batch and the first command after a
reboot.

The individual checks still exist and are useful on their own:

```bash
python3 tools/meta.py --check                    # browser-mcp: tab list + composer
python3 tools/flow_call.py flow_status           # flow-mcp: signed in? project open?
curl -s http://localhost:8880/health             # Kokoro
```

## Reading a failure correctly

### 1. Meta AI / browser-mcp says “No browser is connected”

The extension is installed in the **default Chrome profile**. That Chrome window is simply not
running, or it was closed. Browser MCP can only see a browser that is open with the extension
attached.

Fix — start the default Chrome (no `--user-data-dir`, so it uses the profile that holds the
extension), then re-run the check:

```bash
/opt/google/chrome/chrome --no-first-run --no-default-browser-check https://meta.ai/
python3 tools/meta.py --check
```

Healthy output looks like:

```
✓ tab list
  …  "Meta AI - Your AI Assistant for Images, Shopping and More" — https://meta.ai/ (active)
composer on the meta.ai tab: True
```

This is **not** an install problem, **not** a sign-out, and **not** a reason to use an API key.
If the tab opens but the composer is missing, then look at the page: sign in to Meta AI once in
that window. That is the only Meta failure that is about the account rather than the window.

### 2. Flow / flow-mcp says `signedIn: true, inProject: false`

Flow is connected. It just has no project open. That is the normal state of a fresh Flow window,
not a failure.

Fix — open or create a project in the Flow Chrome window (the one flow-mcp opened on port 9333),
then re-run:

```bash
python3 tools/flow_call.py flow_status
```

Do not queue a plate batch until `inProject` is `true`; a batch queued against no project lands
nowhere. Images are **0 credits** in Agent mode, so there is nothing to buy and no reason to fall
back to another generator.

### 3. Flow / flow-mcp gives no reply at all

That means the flow-mcp server or its Chrome profile is not up — not that Flow is uninstalled.
Check the server path and the profile, then retry:

```bash
test -f /home/openclaw/flow-mcp/dist/index.js && echo "flow-mcp present"
python3 tools/flow_call.py flow_status
```

Flow's Chrome is a separate profile. It does **not** carry the Browser MCP extension, and the
default Chrome does **not** carry Flow's signed-in session. Never use one window to diagnose the
other.

## Rules that follow from this

- **Never say a route is “not connected” without opening the right window first.** The correct
  sentence is “the default Chrome is closed” or “Flow has no project open”, followed by the fix.
- **One session per film — same chat, same window, all images.** Every plate of a film is made in
  the **one open session**: Meta AI in the **same chat tab** (Browser MCP is attached to it) or Flow
  in the **same project window**. Never open a new chat/tab/window per image, never close the open
  one between images, and never re-open a fresh session to make a download unambiguous — the tool
  recognises the new picture against the images already on the page. Inside that session the order
  is strict — **one prompt at a time, sent once, never re-sent** — but the two routes wait
  differently. In the **Meta** tab: send once, check the page at **22 s** and every **10 s** until
  that image is finished, download it, then send the next prompt. In **Flow**: `flow_agent_images`
  batches a film's stills or `flow_generate` paces them one at a time, and either way you call
  `flow_wait` until `finished: true` — it returns inside ~40 s, so call it again; a `still_working`
  reply's `task_id` goes to `flow_wait`, never a repeat of the call. A failed scene is re-made with
  `flow_retry` by job id, under its own number. A late image is waited for, never re-prompted:
  re-sending the same prompt exploits a free route and is forbidden. Close the session only when
  the film's last plate is on disk.
- **Meta's answer is text; Flow's images are files.** Do not ask Flow to write the script and do
  not ask Meta to download a plate through flow-mcp.
- **Meta fallback is narrow.** If Meta is open, signed in, and still will not answer — or returns
  broken JSON — the agent does the same work itself in the same shape and writes
  `plan/META.md` saying so. A closed Chrome window is not that case; open it.
- **Nothing in either chat can publish.** Publishing stays `schedule`, behind an explicit yes.
  Never paste credentials, page tokens or app passwords into Meta AI or Flow.
- **Kokoro is local.** If `localhost:8880` is down, start the local Kokoro server; there is no
  cloud voice fallback in this engine.

## What flow-mcp can do — the tool surface

`python3 tools/flow_call.py <tool> '<json>'` calls any of these from the engine; the same tools
are what `tools/shoot_plates_flow.py` uses. `flow_status` is always first.

| Tool | What it does | Cost |
| --- | --- | --- |
| `flow_status` | session, project, plan, credits left, queued jobs, and the playbook | free |
| `flow_agent_images` | up to 50 image scenes in Flow's own Agent mode, rendered in parallel, prompts enriched by the agent; `references` + `scene_references` hold a car across scenes, `download_quality` `original`/`upscaled` | **0 credits** |
| `flow_generate` | one clip or image per scene, paced; `type` `video`/`image`, `model`, `aspect_ratio` (video: 16:9 or 9:16 only), `duration` 4/6/8/10 s (Omni; Veo fixed 8 s), `resolution` 360p/720p, `first_frame`/`last_frame`, `reference_images` (max 3), `variants`, `max_credits` | images **0**, video **credits** |
| `flow_wait` | waits up to ~40 s for `job_ids` or a `still_working` `task_id`, returns status and file paths; call until `finished: true` | free |
| `flow_retry` | re-queues only the failed scenes, same settings, same file names, by job id | same as the original |
| `flow_cancel` | cancels a job that has not started | free |
| `flow_assets`, `flow_download` | list the project's media / download media that already exists, including the 1080p/2K upscale | **free, no regeneration** |
| `flow_edit` | video-to-video on a clip already in the project (relight, weather, background, remove objects) | credits |
| `flow_continue` | starts a new clip on the last frame of one already in the project, for one continuous take | credits |
| `flow_character`, `flow_character_edit`, `flow_characters` | a reusable product or character portrait so it looks the same in every scene | **free** |
| `flow_techniques` | ready-made prompt phrases (camera moves, product shots, first→last-frame transitions) | free |
| `flow_narrate`, `flow_voices` | TTS narration | free (`gemini` needs a key) |
| `flow_transcribe`, `flow_captions`, `flow_assemble` | local whisper.cpp transcription, burned captions, ffmpeg join | free, local |
| `flow_trash` | moves one asset to Flow's Trash, recoverable | free |

**The prices, as Flow quotes them:** Omni 1.1 Flash **7 credits** at 4 s and **12** at 8 s (720p);
Veo 3.1 **10** (Lite), **20** (Fast), **100** (Quality), all fixed 8 s. Images cost nothing on
Nano Banana. `max_credits` (default 25) makes Flow skip a scene whose quote is higher instead of
spending it, and `variants` multiplies the price. So a video clip is a paid action: say the total,
then ask. The engine's plates are images, so the free route is the normal route.

**What the film can do with a clip today: nothing yet.** No composition carries a `<video>` layer —
`BROLL.make` draws the plate PNG and `tools/score.py` counts the `still=` entries — so a clip is
motion reference, or an engine change made once for every film. It is never a silent substitution
for a plate. `AGENTS.md` → *4. Plates* carries the rule.

## Stock media — Pixabay and Pexels

These are the only other network routes, and they exist for **footage and sound the engine
does not own**: a tyre close-up, a road shot, a background track. They are not image
generators and they never replace Meta AI or Flow for plates. Both are free tier and both
need a key; the keys live in `image2videoEngine/.env` and are never printed, logged or
committed. Report a key's length at most.

| Provider | Endpoint | Auth | Covers |
| --- | --- | --- | --- |
| Pixabay images | `https://pixabay.com/api/` | `?key=` query | photos, illustrations |
| Pixabay video | `https://pixabay.com/api/videos/` | `?key=` query | MP4 clips, several sizes |
| Pexels photos | `https://api.pexels.com/v1/search` | `Authorization: <key>` header | photos |
| Pexels video | `https://api.pexels.com/videos/search` | `Authorization: <key>` header | MP4 clips + poster frames |

```bash
set -a; . ./.env; set +a
curl -s -G "https://pixabay.com/api/videos/" -d key="$PIXABAY_API_KEY" \
  -d q="engine start" -d per_page=10 -d video_type=film -d safesearch=true
curl -s -H "Authorization: $PEXELS_API_KEY" \
  "https://api.pexels.com/videos/search?query=engine%20start&per_page=10&orientation=portrait"
```

Three hard facts learned the slow way:

- **Pixabay has no audio endpoint.** The documented API is images and videos only; there is no
  `api/audio`. Engine and bed recordings come from the local `sound/engines/` library (Pixabay
  Content License, already measured) or from a manually downloaded, licensed file placed there.
  Do not build a search path for something that does not exist.
- **Pixabay rejects `per_page` below 3** with HTTP 400 — and its `q` filter is loose, so ask for
  ten and read them.
- **Neither API serves 1080×1920 plates.** Stock is for motion accents and sound, never the six
  angles: a cropped 16:9 still cuts the car in half, which is the engine's oldest pitfall.

### What may be used, and what may not

A stock clip earns its place only when it **shows this film's car or an indistinguishable
analogue**: same colour family, same wheel and tyre style, same era. A modern wheel, a red car
when the film's car is white, or any frame with a person, animal or reflection of one is a
reject — it breaks the no-living-beings rule and the continuity of the six plates. Say no and
keep the still; a missing insert is invisible, a wrong insert is the thing viewers notice.

Sound is the easier win: a starter crank, an idle loop, a rev. Take one clean take whole rather
than stitching, and level-match it to a target RMS in the build script (these files measure
around −40 dBFS; a guessed `volume=0.3` is inaudible). Engine sound lives in the gaps, never
under a spoken word.

### Provenance

Anything downloaded lands under that film's `stock/` with a sidecar naming the provider, the
asset id, the page URL, the author and the licence. A clip with no recorded source cannot be
published, and rejected candidates stay in `stock/qa/` as evidence of the decision rather than
disappearing.

## Where this is enforced

- `AGENTS.md` → *The two free brains — browser-mcp and flow-mcp*, *Money and other people's
  media*, and *Known pitfalls*.
- `README.md` → *The two free brains*.
- `tools/brain.py` → the three-way preflight.
- `tools/meta.py` → the check and driver; a closed Chrome is reported as a closed window.
- `tools/shoot_plates_flow.py` → refuses a missing project with the fix, not a “not connected”.
- `PROVIDERS.md` → this stock-media section; `.env` holds the two keys by name only.
