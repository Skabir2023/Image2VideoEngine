# Timeline — measured, not estimated

Captured from `renders/Doors That Opened To Sky.mp4` and `audio/final-audio.wav` on
2026-11-15, after the voiceover was rewritten as one chained story and the film re-cut to it.
Render 22.8 MB, sha256 `ef4c4dbf9551dea1…`.

## Picture
- 1128 frames at 60 fps = **18.800 s**, 1080 × 1920.
- Frame counts: 150 + 132 + 86 + 180 + 89 + 128 + 144 + 85 + 134 = 1128.
- Cuts (scene starts, seconds): 2.500, 4.700, 6.133, 9.133, 10.617, 12.750, 15.150, 16.567.
- Cuts (frames): 150, 282, 368, 548, 637, 765, 909, 994.
- Frame scan: `frame0_blank: false`, `black_frames: []`, `one_frame_pops: []`, and every
  hard jump sits on one of those eight frames — no jump anywhere else.
- Lint: 0 errors, 0 warnings, 11 files.

## Voice
- Kokoro `am_michael`, speed 1.2 in the request, one take, 45 words, 15.830 s of audio.
- Placed at `LEAD = 1.00 s`, so the read runs **1.00 – 16.51 s**; the last word
  ("legend?") ends 16.51 s.
- Nine shots, because the chain only offers eight pause-safe cuts. Every cut lands in a
  measured silence, 20–120 ms before the word that opens the next shot:

| cut | gap it lands in | before the word |
| --- | --- | --- |
| 2.500 | 2.39 – 2.55 | "whose" (50 ms) |
| 4.700 | 4.70 – 4.75 | "so" (50 ms) |
| 6.133 | 6.12 – 6.17 | "They" (37 ms) |
| 9.133 | 9.12 – 9.17 | "That" (37 ms) |
| 10.617 | 10.51 – 10.67 | "161" (53 ms) |
| 12.750 | 12.52 – 12.87 | "because" (120 ms) |
| 15.150 | 15.14 – 15.19 | "Would" (40 ms) |
| 16.567 | 16.51 – 16.60 | the roar (33 ms) |

## Cards
Absolute film times, converted per scene by `tools/scene_builder.py`; no card falls outside
its own shot and none is on screen for less than 0.30 s before the cut.

| card | at | shot |
| --- | --- | --- |
| `1954 · MERCEDES 300SL` | 1.05 | 1 |
| `RACE CAR` | 1.99 | 1 |
| `FRAME` / `TOO HIGH` | 2.82 / 3.32 | 2 |
| `DOORS` / `WENT UP` | 4.96 / 5.24 | 3 |
| `1,400` (roll 0.85 s, seed 1400) | 7.23 | 4 |
| `COUPES BUILT` | 8.10 | 4 |
| `THAT BODY` | 9.17 | 5 |
| `161` (roll 0.80 s, seed 161) | 10.67 | 6 |
| `MILES PER HOUR` | 11.52 | 6 |
| `BECAUSE` | 12.87 | 7 |
| `FUEL` / `STRAIGHT IN` | 13.13 / 13.59 | 7 |
| `WOULD YOU` / `DARE?` | 15.19 / 15.56 | 8 |
| `COMMENT` / `BELOW` | 16.80 / 17.05 | 9 |
| `1954 MERCEDES 300SL` | 17.35 | 9 |

Every reveal sits on the word it belongs to. Shot 4 carries no kicker (grey mono over the
gold badge does not read) and its label lands 0.02 s after the roll locks, so the number is
read first.

## Sound, measured on the muxed file
- Master: **−14.2 LUFS integrated, true peak −2.1 dBFS**, 18.800 s.
- Engine start: 0.00–1.00 s, −20 dBFS RMS before loudness normalisation, alone.
- Bed: −29 dBFS RMS looped from 14.00–16.00 s of the source, **−35.6 dB in the pauses**,
  **−52.4 dB under speech** (16.8 dB of duck at the 0.100 floor).
- Roar: 16.60 → 18.61 s (1.73 s of source at rate 0.86), no voice over it.
- One low hit at 16.80 s under the closing card (−33 dB). No whoosh on any seam, no hit
  under a number, no music.
- Seams are the engine's blur cut, `SEAM.blur(tl, DUR)` from `assets/seams.js`: the plate
  defocuses to 18 px over the last 0.20 s of each shot and focuses back over the first
  0.18 s of the next. Shot 1 passes `in: 0` and shot 9 `out: 0`, so frame 0 and the last
  frame are sharp.
- Section levels (mean_volume): 0–1 s −15.1 dB (engine start, alone), 2–6 s −17.9 dB
  (voice over the ducked bed), 9.2–16.7 s −17.1 dB (voice), 16.6–18.6 s −18.1 dB (the roar).
