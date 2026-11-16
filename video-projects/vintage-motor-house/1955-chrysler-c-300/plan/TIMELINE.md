# Timeline — 1955 Chrysler C-300: The Luxury Coupe That Won NASCAR

Measured on the finished film, 20.400 s at 60 fps, 1080×1920.

Voice: Kokoro `am_michael`, speed 1.2, **one take of the whole paragraph**, 17.634 s, 43 words
(2.44 words/s). `LEAD = 1.00 s`; every spoken time below is absolute film time.

The first second belongs to the car: the engine catching at full level with no voice over it. The
last two seconds belong to it again: the Hemi roar answers the closing question after the final
word has ended.

## Scenes and cuts

| # | Scene | Still | Start | Duration | Frames | Cut before |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `s01-hero` | `01_hero_front34.png` | 0.000 | 3.200 | 192 | — |
| 2 | `s02-side` | `02_side.png` | 3.200 | 2.683 | 161 | 3.200 |
| 3 | `s03-rear` | `03_rear.png` | 5.883 | 2.967 | 178 | 5.883 |
| 4 | `s04-engine` | `04_engine.png` | 8.850 | 1.817 | 109 | 8.850 |
| 5 | `s05-interior` | `05_interior.png` | 10.667 | 3.133 | 188 | 10.667 |
| 6 | `s06-wheel` | `06_wheel.png` | 13.800 | 1.967 | 118 | 13.800 |
| 7 | `s07-grille` | `07_grille.png` | 15.767 | 1.733 | 104 | 15.767 |
| 8 | `s08-tail` | `08_taillight.png` | 17.500 | 2.900 | 174 | 17.500 |

Frames: 192 + 161 + 178 + 109 + 188 + 118 + 104 + 174 = **1,224** = 20.400 s × 60.

Eight distinct plates for eight scenes: `ceil(20.4 / 3) = 7` is the floor, the longest still is
**3.20 s** (the hero, which carries the whole engine start before the first word), and no plate
appears twice.

Cuts land in the measured pauses:
`3.200 · 5.883 · 8.850 · 10.667 · 13.800 · 15.767 · 17.500`
(before was 3.88, 300 5.93, At 9.77, it 10.72, Then 13.84, horsepower 15.83, with 17.57).

The first cut is the one exception to the 50–65 ms rule: *in 1955* ends at 2.99 and *was* opens at
3.88, so the pause is 0.89 s long — three times any other in the take. The hero may not outlive
3.20 s, so the cut goes at 3.200, inside the pause and never on a word, and the side view gets
0.68 s of air before the line lands on it. That reads as pacing, not as a late cut.

**Why the 127 is in the interior scene.** The transcript has no gap at all between *hit* and
*127* (10.150 → 10.150), so no cut may go between them. The real pause is 0.77 s after *Daytona*,
before *it*, and cutting there gives the number 1.85 s locked on screen instead of the two frames
a cut before *and* would have left it.

## Words

| Word | Starts | Word | Starts | Word | Starts |
| --- | --- | --- | --- | --- | --- |
| America's | 1.05 | most | 1.60 | powerful | 1.87 |
| car | 2.42 | in | 2.61 | 1955 | 2.76 |
| was | 3.88 | a | 4.04 | Chrysler | 4.14 |
| luxury | 4.64 | coupe. | 5.08 | 300 | 5.93 |
| horsepower, | 6.25 | from | 7.35 | a | 7.51 |
| 331 | 7.59 | Hemi. | 8.81 | At | 9.77 |
| Daytona | 9.95 | it | 10.72 | hit | 10.89 |
| 127 | 11.15 | and | 12.04 | won | 12.35 |
| the | 12.45 | NASCAR | 12.71 | title. | 13.26 |
| Then | 13.84 | Chrysler | 14.11 | named | 14.48 |
| the | 14.76 | car | 14.85 | after | 15.02 |
| its | 15.39 | own | 15.54 | horsepower. | 15.83 |
| Would | 16.80 | you | 17.07 | take | 17.23 |
| one | 17.42 | with | 17.57 | two | 17.78 |
| gears? | 17.94 | | | | |

Last word ends **18.41 s**. The closing card holds alone for 1.99 s while the roar lands.

## Text on picture

Frame 0 is the thumbnail, so the title is complete before the first word: kicker
`1955 · CHRYSLER C-300` at 0.18, then **MOST** / **POWERFUL** flying in word by word from 0.42.

| Scene | Number rolled | Red line | Lock → label |
| --- | --- | --- | --- |
| `s01-hero` | — | POWERFUL | fly at 0.42 / 0.66 |
| `s02-side` | — | LUXURY COUPE | on *Chrysler* 4.14 / *coupe* 5.08 |
| `s03-rear` | 300 | HORSEPOWER | 5.93 + 0.88 = 6.81 → 6.90 |
| `s04-engine` | — | kicker only | `DAYTONA, 1955` on *Daytona* 9.95 |
| `s05-interior` | 127 | MILES AN HOUR | 11.15 + 0.80 = 11.95 → 12.00 |
| `s06-wheel` | 300 | IS THE NAME | 14.48 + 0.80 = 15.28 → 15.40 |
| `s07-grille` | — | TAKE ONE? | on *Would* 16.80 / 16.98 |
| `s08-tail` | — | GEARS? | on *two* 17.78 / *gears* 17.94; rule + label `1955 CHRYSLER C-300` at 18.55 |

Every roll is seeded, every label after its lock, and no number is ever flat text: `300` (hp),
`127` (Daytona) and `300` again as the car's name are the film's three counted facts. `331` and
`1955` stay in the voice and the kicker.

## The taillight

The closing lamp is painted, not photographed. `s08-tail` carries a `glow=` block in `scenes.py`
and `tools/scene_builder.py` turns it into a `.tailglow` div **inside BROLL's `.br-layer`**, so the
1.05 push, the 16 px truck and the 18.42 shake all carry it and the light stays on the bulb while
the camera moves. It is `mix-blend-mode: screen` — it adds light to the lens instead of covering
it — and it sits under `#fg`, so the card stays sharp.

- Lens centre measured on the still: **32.6% / 52.4%** of the plate. The gradient `at` values are
  plate coordinates, and because the layer *is* the plate they hold in every frame of the push.
- Comes up at **18.42 s**, on the roar with the low hit: 0.14 s rise to full, settling to 0.94.
  The lamp switches on with the answer, then holds warm for the last 1.9 s.
- Three gradients: a white-hot core (9% × 5%), an amber fill across the lens (23% × 13%), and a
  red halo (42% × 25%) that spills onto the chrome bezel and the rear quarter.
- Red on red does not read in daylight, so the core carries the light: the lens goes amber-warm
  from the middle out instead of simply getting redder.

## Sound

| Element | Time | Level / result |
| --- | --- | --- |
| Engine start | 0.00–1.60 | full level, alone before the voice; slice 0.10–1.60 s level-matched to −20 dBFS RMS |
| Big-block idle bed | 1.05–20.30 | −35.6 dB in pauses, −51.4 dB under speech |
| Duck | word-timed | floor 0.100 (−20 dB), 20 ms attack / 220 ms release |
| Closing roar | 18.40–20.40 | 2.00 s, no voice over it |
| Low hit | 18.42 | under the closing card only |
| Master | 0.00–20.40 | −14.2 LUFS integrated, sample peak −3.6 dBFS |

Muxed file: start alone −16.5 LUFS, speech section −14.1 LUFS, roar alone −15.0 LUFS, true peak
−3.5 dBTP.

## Gates (measured on the delivered file)

- `frame0_blank: false` (frame 0 std 56.83)
- `black_frames: []`
- `one_frame_pops: []`
- `hard_jumps`: 231 (74.6), 353 (34.5), 531 (46.8), 640 (49.2), 828 (39.2), 946 (37.5),
  1050 (46.7) — seven seams, none elsewhere.
- Audio: −14.2 LUFS integrated, true peak −3.5 dBTP; voice above the bed throughout.
- Lint: **0 errors, 0 warnings** (`hyperframes lint`, 9 files).
- File: `renders/1955 Chrysler C-300 - The Luxury Coupe That Won NASCAR.mp4`
  (1080×1920, 60 fps, H.264/AAC, 20.400 s, 36.2 MB). A second copy of the same cut is kept as
  `… (2).mp4`.

## Plates

Two plates were re-shot after the first render: the wheel and the grille had come back as an
interior and a front three-quarter, and the run that replaced them could hand back a stale
picture — `tools/shoot_plates.py` now requires a new image ≥ 900 px wide, lets the DOM settle,
and rejects bytes already in `stills/`.
