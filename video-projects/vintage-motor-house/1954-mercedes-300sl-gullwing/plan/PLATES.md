# Plates — 1954 Mercedes-Benz 300SL Gullwing

Twelve stills, generated free through **Meta AI in the signed-in Chrome** (Browser MCP,
0 credits). Every prompt repeats the identity block verbatim so the twelve read as one car
in one studio. The first pass of this film used grey gradient placeholders — they sit in
`qa/placeholder-stills/` and were never a real plate.

## Car identity block
1954 Mercedes-Benz 300SL Gullwing coupe, silver paint, chrome grille with three-pointed
star, round headlights, chrome bumpers, red leather interior, chrome hubcap wheels

## The twelve plates
Every prompt opens with `Create one photorealistic photograph, vertical portrait 9:16: `
+ the identity block, and closes with `empty concrete studio, golden hour light, 35mm,
no people, no animals, no text, no watermark`.

| # | File | Framing clause | Used in |
| --- | --- | --- | --- |
| 1 | `01_hero_front34.png` | Front three-quarter, gullwing doors closed | s01 |
| 2 | `02_side.png` | Side profile, one gullwing door open straight up, full car in frame | s02 |
| 3 | `03_rear.png` | Rear three-quarter, rounded tail, chrome bumper, twin exhaust pipes | s09 |
| 4 | `04_engine.png` | Bonnet lifted, engine bay filling the frame: overhead-cam inline six, intake manifold, chrome cam cover | s06 |
| 5 | `05_interior.png` | Interior through the open door: red leather buckets, body-colour dash, thin-rimmed wheel, chrome trim | s11 |
| 6 | `06_wheel.png` | Tight front wheel close-up: steel disc, chrome hubcap, black tyre | s04 |
| 7 | `07_headlight.png` | Extreme close-up of one round headlight: chrome bezel, glass lens, silver fender curve | s03 |
| 8 | `08_star.png` | Extreme close-up of the three-pointed star on the grille, polished bars | s05 |
| 9 | `09_engine_detail.png` | Tight engine detail: polished intake manifold and injector lines, chrome cam cover | s07 |
| 10 | `10_exhaust.png` | Rear lower body close-up: chrome bumper, twin exhaust tips, tail light lens | s08 |
| 11 | `11_gauges.png` | Dashboard gauge cluster: round dials, cream numerals, chrome rings, red leather | s10 |
| 12 | `12_steering.png` | Thin-rimmed ivory steering wheel and horn ring, red dash behind | s12 |

Each `.images.json` next to the plate records engine, full prompt, size and time.

## How they were pulled
Meta AI returns 1152×2048 WebP (exactly 9:16). Each was downloaded from the page with
Browser MCP's `download`, then scaled once to 1080×1920 with lanczos — no crop, and no
re-encode beyond the single scale.

One chat for the whole film, one prompt at a time, as the rule now requires. This shoot was
first done with a fresh chat per shot, because Meta AI's message list only keeps recent
messages in the DOM and "the newest image on the page" kept resolving to the hero plate.
That is no longer the method: the new picture is identified against the image URLs already
on the page (the `seen` set in `tools/shoot_plates.py`), so the shared chat is unambiguous
and the session stays open for every plate. Consistency comes from the identity block,
not from chat context.

## Checks
- No people, no animals, no text overlay, no watermark in any of the twelve.
- Same silver paint, same chrome hubcap wheels, same red leather, same studio and light
  across all twelve; nothing was cropped out of a 16:9 frame.
- Engine bay and interior are the correct 300SL M198 layout.
- Camera framing runs wide → macro → wide across the film, so consecutive shots never
  repeat the same distance.
