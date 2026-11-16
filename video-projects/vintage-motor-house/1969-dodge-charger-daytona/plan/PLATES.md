# Plates — 1969 Dodge Charger Daytona

Fourteen plates for a 30 s film, cut at a fresh image roughly every two seconds. The six fixed
angles come first, in order — front ¾, side, rear, engine bay, interior, wheel — then the
close-ups a beat needs: the nose, the rear window, the tail, the wing, and three tight details
(wing strut, steering wheel, fender badge) that carry the zoom beats.

Generated free: plates 01–02 on **Meta AI** (Browser MCP, one chat), 03–14 on **Google Flow**
(flow-mcp, 0 credits), all scaled once to 1080×1920.

## Car identity block
1969 Dodge Charger Daytona coupe, bright red paint, black vinyl roof, pointed sheet-metal nose
cone with exposed round headlights, black mesh grille, flush rear window, 23-inch rear wing on
tall black struts, black steel wheels with chrome hubcaps, black vinyl interior.

Every prompt opens with `Create one photorealistic photograph, vertical portrait 9:16: ` + the
identity block verbatim, and closes with `empty concrete studio, golden hour light, 35mm,
no people, no animals, no text, no watermark`.

## The plates

| # | File | Framing clause | Scene |
| --- | --- | --- | --- |
| 1 | `01_hero_front34.png` | Front three-quarter, whole car in frame, nose cone pointing left | s01, s14 |
| 2 | `02_side.png` | Side profile from low, the wing standing above the roofline | s02 |
| 3 | `03_rear34.png` | Rear three-quarter, wing and flush rear window, whole car in frame | s03 |
| 4 | `04_wing.png` | Tight rear close-up of the wing blade and its black struts | s04 |
| 5 | `05_nose.png` | Front close-up of the pointed nose cone, mesh grille and one exposed headlight | s07 |
| 6 | `06_engine.png` | Hood up, engine bay filling the frame: 440 Magnum V8, black air cleaner, orange block | s09 |
| 7 | `07_interior.png` | Interior through the open door: black vinyl buckets, three-spoke wheel, round gauges | — (kept for a Part 2) |
| 8 | `08_wheel.png` | Tight front wheel close-up: black steel wheel, chrome hubcap, whitewall tyre | s11 |
| 9 | `09_rearwindow.png` | Flush rear window and deck from behind and above, wing in the foreground | s08 |
| 10 | `10_tail.png` | Rear lower close-up: chrome bumper, twin exhaust tips, rectangular tail light | s06 |
| 11 | `11_closing.png` | Front low angle, headlights lit, nose cone filling the frame, car in shadow | s12 |
| 12 | `12_steering.png` | From the driver's seat: three-spoke steering wheel filling the frame, round gauges behind it, black vinyl and dust | s10 |
| 13 | `13_badge.png` | Extreme close-up of the chrome script nameplate on the front fender, only part of it in frame, lettering soft and out of focus | s13 |
| 14 | `14_wingstrut.png` | Low tight detail where the wing's black strut bolts through the rear deck, red quarter panel filling the lower frame | s05 |

Each `.images.json` next to the plate records engine, full prompt, size and time.

## Shoot status — 2026-11-15
**All fourteen plates are on disk.** Two routes, both free:

1. **Meta AI** (Browser MCP, one chat, prompts appended — never a new chat per shot) drew the
   hero ¾ and the side profile (1152×2048 WebP, downloaded, scaled once). It then answered:
   *"You reached your limit. Get Meta One Core for more media with AI, or wait until 9:08 AM."*
   That route is stopped, not retried.
2. **Google Flow** (`flow-mcp`, Agent mode, Nano Banana 2.1, **0 credits**) drew the other twelve
   in two parallel batches into `1969-dodge-charger-daytona-plates`, ~3 minutes each.

Checks on the set: same red paint and black vinyl roof in all fourteen, the wing on its black
struts, black steel wheels with chrome hubcaps, empty concrete studio, golden-hour light — and
no people, animals, readable text or watermark in any frame. Engine bay is the 440 Magnum.

```bash
python3 tools/shoot_plates_flow.py video-projects/vintage-motor-house/1969-dodge-charger-daytona   # queue + wait
python3 tools/shoot_plates_flow.py video-projects/vintage-motor-house/1969-dodge-charger-daytona --collect
```

## Rules for the shoot
- No people, no animals, no reflections of people, no readable text, no watermark, no invented race livery.
- Same red paint, same black wing, same wheels in every plate. The identity block is repeated
  word for word; that is what keeps the set reading as one car.
- Append the prompts to the one open chat (Meta) or send them as one batch (Flow); never a new
  chat per shot.
- Look at every plate before anything is built on it. A drifted plate is re-shot on its own.
