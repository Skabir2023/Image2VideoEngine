# Timeline — 1969 Dodge Charger Daytona

Every number here is measured, not chosen: the voice is one Kokoro take of **am_adam**, the
transcript gives the word times, and the picture is cut to those.

## Voice

- Kokoro **`am_adam`**, `speed 1.03`, one call, 86 words → **26.160 s**
- Speed 1.03 rather than the page's 1.2 because am_adam reads about 18 % faster than am_michael
  at the same setting; 1.03 is what puts an 86-word script on 30 s of picture. It is set in the
  TTS request, never `atempo` afterwards. Recorded in `audio/paragraph/voice.json`.
- Placed at **1.00 s**, so speech runs **1.00 – 27.16 s** (last word "below." ends 26.84 s)
- Word times: `audio/paragraph/transcript.json`

## Picture — 1800 frames = 30.000 s at 60 fps, 14 shots

A fresh image roughly every two seconds: the three tight details (wing strut, steering wheel,
fender badge) sit on the beats that ask for them, so the picture keeps moving without a card
being cut short.

| # | Scene | Starts | Frames | Seconds | Plate | Words spoken |
|---|-------|--------|--------|---------|-------|--------------|
| 1 | hero ¾ | 0.000 | 194 | 3.233 | `01_hero_front34.png` | Only 503 of these exist, |
| 2 | side | 3.233 | 183 | 3.050 | `02_side.png` | because NASCAR said build 500 or stay home. |
| 3 | rear ¾ | 6.283 | 169 | 2.817 | `03_rear34.png` | So Dodge built the minimum, then hung |
| 4 | wing | 9.100 | 77 | 1.283 | `04_wing.png` | a wing on the trunk. |
| 5 | strut | 10.383 | 108 | 1.800 | `14_wingstrut.png` | It sat 23 inches up, and no, |
| 6 | tail | 12.183 | 126 | 2.100 | `10_tail.png` | that was not so the trunk would open. |
| 7 | nose | 14.283 | 172 | 2.867 | `05_nose.png` | It was reaching for clean air. The nose came to a |
| 8 | window | 17.150 | 125 | 2.083 | `09_rearwindow.png` | point, the rear window went flat, |
| 9 | engine | 19.233 | 108 | 1.800 | `06_engine.png` | and that shape hit 200 miles per hour. |
| 10 | steering | 21.033 | 168 | 2.800 | `12_steering.png` | Then the cars sat unsold on dealer lots. |
| 11 | wheel | 23.833 | 123 | 2.050 | `08_wheel.png` | Would you drive a car built to beat a rule? |
| 12 | closing | 25.883 | 97 | 1.617 | `11_closing.png` | Tell me below. |
| 13 | badge | 27.500 | 66 | 1.100 | `13_badge.png` | — (the roar) |
| 14 | bookend | 28.600 | 84 | 1.400 | `01_hero_front34.png` | — (the roar) |

Cuts sit in the measured pauses, never on a word. The 10.383 cut is the one tight pause in the
script ("…trunk." ends 10.36, "It" starts 10.41) and it is what hands the wing to the strut
close-up so the 23 can roll on the detail. The last two cuts (27.500, 28.600) land in silence,
under the roar.

Camera: every shot moves and most of them push, so the details read as zooms into the car —
the wing cranes up, the strut pushes 0.17 in, the steering wheel pulls back, the badge pushes
0.15 in under the dying roar.

## Numbers — counted, never printed

Every figure spins through random digits and locks left to right (`TX.roll`), starting on its word:

| Figure | Scene | Roll | Locked at |
|--------|-------|------|-----------|
| 503 | 1 | `1.38 s`, 0.85 s | 2.23 s |
| 500 | 2 | `4.71 s`, 0.80 s | 5.51 s |
| 23 | 5 | `10.74 s`, 0.78 s | 11.52 s |
| 200 | 9 | `19.30 s`, 0.85 s | 20.15 s |

Labels (`BUILT`, `CARS NASCAR WANTED`, `INCHES UP`, `MILES PER HOUR`) arrive after the lock, so
the number is read first and the meaning second. `ON THE TRUNK` (scene 4) and
`1969 · CHARGER DAYTONA` (scene 13) slide in as footnotes, and the kicker
`REAR WINDOW WENT FLAT` arrives word by word.

## Sound

Three parts, all from `engine-start-idle-rev_nhumphrey_pixabay-33510.mp3`. The car is on the
whole film, it is loud enough to be the bed, and it gets out of the way of every word.

| Part | Where | Slice | Treatment | Level |
|------|-------|-------|-----------|-------|
| Start | 0.10 – 2.60 s | `0.10–2.60` | level-matched, 20 ms in, held to 0.90 s, then a raised-cosine settle to silence over 1.45 s | `−18 dBFS` RMS (first second measures `−20.5 LUFS` on its own) |
| Bed | 1.00 – 29.90 s | `14.00–16.00` looped, 0.30 s crossfade | highpass 42 Hz, lowpass 2.2 kHz, compressed, 0.70 s fade in | `−19 dBFS` RMS target → **−26.0 dB in the pauses** |
| Roar | 26.90 – 28.91 s | `27.72–29.45` at rate `0.86` | 20 ms in, 300 ms out, level-matched then +12 % | **−15.5 dBFS** RMS, `−11.7 LUFS` over its window |

Ducking is built from the transcript, not from a compressor: bed ×0.100 (−20 dB) across every one
of the 86 word spans, ×1.0 in the gaps, smoothed 20 ms attack / 220 ms release. Measured:
**−26.0 dB in the pauses, −41.6 dB under speech** — the car is felt under the voice and never
heard over one, and it comes straight back up in every gap.

Mix: **−14.2 LUFS**, peak **−2.4 dBFS**, 30.000 s. The speech section on its own (1.00–27.16 s)
measures **−14.2 LUFS**, and the roar window measures −11.7 LUFS — 2.5 dB louder than the voice,
so the car gets the last word.

## Render — measured

`renders/The Most Imposing 1969 Dodge Charger Daytona Ever Built.mp4` — **1800 frames,
1080×1920, 60 fps, 30.000 s, 35 MB**, 14 scenes joined without re-encoding, mix muxed on.

Gates, all run on that file:

| Gate | Result |
| --- | --- |
| `npm run lint` | 0 errors, 0 warnings (15 files) |
| `frame0_blank` | false (std 49.0 — the thumbnail reads) |
| `black_frames` / `one_frame_pops` | `[]` / `[]` |
| hard jumps | 194, 377, 546, 623, 731, 857, 1029, 1154, 1262, 1430, 1553, 1650, 1716 — the thirteen seams, nothing else |
| loudness / peak | −14.2 LUFS, −2.4 dBFS; speech section alone −14.2 LUFS |
| frames looked at | `qa/plates-sheet.jpg`, `qa/plates-sheet-2.jpg`, `qa/new-plates-sheet.jpg` (all 14 plates), `qa/final-sheet.jpg` (16 frames across the cut), `qa/s10-check.jpg` |

Cut list printed by the mix: 3.233, 6.283, 9.100, 10.383, 12.183, 14.283, 17.150, 19.233,
21.033, 23.833, 25.883, 27.500, 28.600.

## Booked

Post `b2464520-9792-4a52-80e8-54e57d54c2f6` on Vintage Motor House, slot
**2026-11-15 07:32 UTC** (13:32 local, +06). Car List row 126 marked `Used? = Yes`,
`Angle Used = Secret Story`, `Date Used = 2026-11-15`.
