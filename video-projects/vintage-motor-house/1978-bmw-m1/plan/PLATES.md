# Plates — 1978 BMW M1

**Sixteen plates for a 30 s film**, so a new image lands about every 1.9 s. The six fixed angles
come first, in order — front ¾, side, rear, engine bay, interior, wheel — then ten close-ups that
cover every part of the car by name: the roundel on the nose, the roundel on the tail panel,
headlight, steering wheel, exhaust, engine-cover louvres, wing mirror, front air intake, tail
lamp, and a lit night hero for the last card.

Every one is shot as a **sharp, high-detail photograph**: the detail plates are macro, focus
locked on the part, shallow depth of field only where it helps the part read. No soft focus on a
part the beat is about.

## Car identity block

1978 BMW M1 coupe (E26) by Giugiaro, bright solid guards-red paint, low wedge body with a wide
flat nose, black slatted grille between twin rectangular headlights under clear covers, a single
blue-and-white BMW roundel on the nose and another on the tail panel, black louvred engine cover
behind the cabin, silver Campagnolo five-spoke alloy wheels with wide low-profile tyres, grey
cloth and black cockpit with a three-spoke wheel and twin round gauges, no racing livery, no
stripes on the body.

Every prompt opens with `Create one photorealistic photograph, vertical portrait 9:16: ` + the
identity block verbatim, and closes with `empty concrete studio, golden hour light, 35mm,
no people, no animals, no text, no watermark`. The badge plates say so explicitly in their own
framing clause: the roundel is the car's own emblem, sharp, and nothing else is written anywhere.

## The plates

| # | File | Framing clause | Scene |
| --- | --- | --- | --- |
| 1 | `01_hero_front34.png` | Front three-quarter from low, the whole car in frame, nose and roundel catching the light | s01, s16 |
| 2 | `02_side.png` | Side profile from low, the full wedge and the flat engine cover visible | s02 |
| 3 | `03_rear34.png` | Rear three-quarter, tail panel and roundel in view, whole car in frame | s03 |
| 4 | `04_engine.png` | Rear deck open, engine bay filling the frame: silver M88 straight-six, six throttle bodies, cam cover with the BMW M stripes, every hose and clamp sharp | s04 |
| 5 | `05_interior.png` | Interior through the open door: three-spoke wheel, twin round gauges, grey cloth seats | s05 |
| 6 | `06_wheel.png` | Macro of the front wheel: silver Campagnolo five-spoke alloy, tyre sidewall and tread sharp, brake disc behind | s06 |
| 7 | `07_roundel_front.png` | Macro of the nose roundel filling the upper frame, blue and white quadrants sharp and correct, chrome ring, red paint around it, the black grille slats behind | s07 |
| 8 | `08_roundel_rear.png` | Macro of the rear panel roundel, blue and white quadrants sharp, red tail panel around it, the edge of the tail lamp at the bottom of the frame | s08 |
| 9 | `09_headlight.png` | Macro of one rectangular headlight under its clear cover, the indicator beside it, the shut line and red paint sharp | s09 |
| 10 | `10_steering.png` | From the driver's seat: three-spoke steering wheel filling the frame, hub and spokes sharp, twin gauges behind it | s10 |
| 11 | `11_exhaust.png` | Macro of the twin exhaust tips in the black rear valance, polished steel mouths sharp, slight heat colour on the metal | s11 |
| 12 | `12_louvres.png` | Macro of the black louvred engine cover: rows of slats, edges sharp, red paint either side, light falling through the gaps | s12 |
| 13 | `13_mirror.png` | Macro of the wing mirror and the leading edge of the side glass, mirror shell sharp, red door below | s13 |
| 14 | `14_intake.png` | Macro of the front air intake in the nose and the indicator beside it, black mesh deep and sharp, red paint above | s14 |
| 15 | `15_taillight.png` | Macro of the rear lamp cluster: red lens, orange section, chrome trim, the panel edge sharp | s15 |
| 16 | `16_night_hero.png` | Low front three-quarter at dusk, headlights and tail lamps lit, nose and roundel filling the frame, dark garage behind | s16 |

Each `.images.json` next to the plate records engine, full prompt, size and time.

## Shoot status — done

**Route: Google Flow** (`flow-mcp`, Agent mode, Nano Banana 2.1, **0 credits**, project
`397a7e81-b316-445e-b3b4-fa434ec7cee6`). Meta AI still out of image credits and not retried.

- 16 plates generated in 3 batches (initial 16-tile run + reruns for 5 misses + 4 targeted re-shoots
  for the parts the batch missed: side, rear roundel, exhaust, tail lamp). All 16 downloaded
  **upscaled** (1536×2752 source) and scaled once to 1080×1920 into `stills/`, with per-plate
  `.images.json` provenance (prompt, source clip, size, engine).
- Visual check on the set: consistent guards-red BMW M1 (E26), silver Campagnolo five-spoke wheels,
  blue/white roundel on nose and tail, M88 straight-six visible in the engine bay, concrete
  studio/garage with warm light, no people, no animals, no invented lettering, no watermark. The
  close-up parts requested are covered: wheel, steering wheel, engine (bay + louvres + intake),
  roundel front and rear, front ¾, side, rear ¾, headlight, mirror, exhaust, tail lamp, plus a lit
  night hero.

Final scene mapping is the table above (`s01-hero` … `s16-tail`, one plate per scene). Measured
timing and cuts are in `plan/TIMELINE.md`.

## Rules for the shoot
- One tab, one batch, prompts appended in order — never a new chat per image.
- Identity block repeated word for word in every prompt.
- Native 1080×1920, scaled once, never cropped from 16:9.
- No living beings, no reflections of people, no text, no watermark.
- Look at every plate before the scene table is written.
