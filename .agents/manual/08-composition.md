# Writing a scene — the contract, the scene table, the seams, the numbers

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

## Composition contract (HyperFrames)

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
| `TX.fly(tl, el, at, gap)` | the two lines fly in from alternate sides and settle — the entrance for a title that should feel drawn onto the plate, not slammed (`fly=True` in the scene table) |
| `TX.roll(tl, el, at, dur, seed)` | a number spins through random digits and locks onto its real value — use it for **every** number, price, year or figure |
| `TX.words(tl, el, at, gap)` | kicker/label arriving word by word |
| `TX.typeOn(tl, el, at, per)` | character-by-character, use sparingly |

## The scene table — the fields `scenes.py` may use

`scenes.py` is data only: `tools/scene_builder.py` reads it and writes `compositions/*.html` and
`index.html`. Its docstring lists the keys every scene must carry; these are the optional ones the
films use, and a plate that needs one of them never gets a hand edit in the generated HTML.

| Field | What it does |
| --- | --- |
| `scrim` / `scrim_gain` | `"top"` or `"bottom"`; `scrim_gain` `1.18–1.30` deepens that scrim — only on a bright macro plate (grille, gauges, valve cover) where the type would otherwise sit on glare, never on the hero |
| `blur_in` / `blur_out` | the seam at this scene's head and tail; frame 0 and the last frame pass `False` |
| `shots` | camera moves on one plate, `dict(t, dur, move, by, ease)`. Two may run at once — a `push` with a `truckR` is the engine's depth cue. `dur="full"` runs to the shot's end; a move that starts later uses `dur="rest"`, which still ends where the shot does. `by` is a zoom fraction for `push`/`pull` (`0.07–0.15`) and pixels for the trucks and cranes (`14–50`) |
| `b2_size` | the second line's size: `""` (208 px), `"mid"` (148 px), `"small"` (96 px, a long phrase). *Style* states the rule; this is how a scene asks for it |
| `fly` | `True` swaps `TX.slam` for `TX.fly` on both lines — the title lockup |
| `roll` | `dict(dur, seed)` on a scene whose first line is a number (*Numbers law*) |
| `kick_red` | paints the kicker in the accent instead of bone |
| `extra_shakes` | `[dict(at, power, decay)]`, absolute film time — one on the roar and the closing card, never a steady wobble |
| `glow` | `dict(bg, at, rise, peak, hold, settle)` paints a light onto the plate itself (a taillight coming up), appended inside BROLL's layer with `screen` blend so the camera move and the shake carry it and it stays on the lamp |
| `leak` | a light sweep across the hero, drawn by the builder |

Two rules the fields do not state: a card's `*_at` is absolute film time on the word, and a scene
carries two camera moves at most — a third reads as a wobble.

## Seams

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
one `SEAM.blur` call, and the behaviour is the engine's, so changing the cut changes every film at
once. **Frame 0 of the film and the last frame stay sharp.**

No white flash overlay, no skew whip, no transition sound. The picture changes in a blur; the mix
has no whoosh on the cut (see [Sound law](09-sound-law.md)), so the engine bed carries the change.
This replaced the old `0.20 s` flash-out / `0.16 s` flash-in after the flash read as a strobe on
repeated viewing.

Scenes are joined without re-encoding, so a one-frame error in any scene's duration shifts the
audio against every cut after it.

## Numbers law

**A number never appears as flat text.** Any year, production count, horsepower figure, price or
0–60 time is counted out: the digits spin through random values and lock onto the real one, left
to right, before the reader can finish reading the label. It is the difference between a caption
and a claim.

- `TX.roll(tl, $('b1'), at, dur, seed)` — `dur` `0.75–0.95 s`, its own `seed`.
- The roll starts **on** the word and overlaps the `TX.slam` entrance, never before it.
- Keep the digit count: `547` never flashes `47`, `4.7` never loses its decimal.
- Seeded, so every render spins the same digits. Never `Math.random()` at draw time.
- The label under it (`BUILT`, `HORSEPOWER`, `SECONDS`) arrives word by word *after* the lock, so
  the eye reads the number first and the meaning second.
