# Timeline — 1987 Buick GNX

Every number here is measured, not chosen: the voice is one Kokoro take, the transcript
gives the word times, and the picture is cut to those.

## Voice

- Kokoro `am_michael`, `speed 1.2`, one call, 42 words → **19.094 s**
- Placed at **0.30 s**, so speech runs **0.36 – 19.26 s** (last word "comments." ends 18.96 s)
- Word times: `audio/paragraph/transcript.json`

## Picture — 1282 frames = 21.367 s at 60 fps

| # | Scene | Starts | Frames | Seconds | Plate | Words spoken |
|---|-------|--------|--------|---------|-------|--------------|
| 1 | hero ¾ | 0.000 | 176 | 2.933 | `01_hero_front34-01.png` | This Buick beat Corvettes without a V8. |
| 2 | side | 2.933 | 269 | 4.483 | `02_side-01.png` | Only 547 GNX were built in 1987. |
| 3 | engine bay | 7.417 | 292 | 4.867 | `04_engine-01.png` | Its turbo 3.8 V6 made 276 horsepower. |
| 4 | rear | 12.283 | 162 | 2.700 | `03_rear-01.png` | It hit 60 in 4.7 seconds. |
| 5 | interior | 14.983 | 173 | 2.883 | `05_interior-01.png` | Would you take this turbo V6 over a V8 today? |
| 6 | wheel | 17.867 | 210 | 3.500 | `06_wheel-01.png` | Tell me in the comments. |

Cuts sit ~60 ms before the first word of the next line, so the picture changes on the pause and
the text lands with the word. Scene 6 is 0.77 s longer than the read needs: that is the picture
under the closing roar.

## Numbers — counted, never printed

Every figure spins through random digits and locks left to right (`TX.roll`), starting on its word:

| Figure | Scene | Roll | Locked at |
|--------|-------|------|-----------|
| 547 | 2 | `0.43 s`, 0.90 s | 1.33 s |
| 276 | 3 | `0.95 s`, 0.95 s | 1.90 s |
| 4.7 | 4 | `0.34 s`, 0.80 s | 1.14 s |

Seeded (`547`, `276`, `47`), so the same digits spin on every render. Labels (`BUILT`,
`HORSEPOWER`, `SECONDS`) arrive after the lock, so the number is read first.

## Sound

Three parts, all from `engine-start-idle-rev_nhumphrey_pixabay-33510.mp3`:

| Part | Where | Slice | Treatment | Level |
|------|-------|-------|-----------|-------|
| Start | 0.10 – 1.60 s | `0.10–1.60` | level-matched, 20 ms in / 150 ms out | `−22 dBFS` RMS, ×0.55 under the first words |
| Bed | 1.15 – 21.0 s | `14.00–16.00` looped, 0.30 s crossfade | highpass 42 Hz, lowpass 2.2 kHz, compressed | `−29 dBFS` RMS before ducking |
| Roar | 19.30 – 21.31 s | `27.72–29.45` at rate `0.86` | 20 ms in, 300 ms out | 2.01 s at full level |

Ducking is computed from the transcript, not from a compressor: bed ×0.17 (−15 dB) across every
one of the 42 word spans, ×1.0 in the gaps, smoothed 20 ms attack / 220 ms release.
Measured: **−35.6 dB in the pauses, −48.5 dB under speech** — 20 dB+ below the voice.

Mix: **−14.2 LUFS**, peak **−2.2 dBFS**, 21.367 s.

## Render

`renders/The Buick That Beat Corvettes.mp4` — 1282 frames, 1080×1920, 60 fps, 29 MB.
Scan: frame 0 not blank (std 34.58), no black frames, no one-frame pops; the jumps at frames
173–179, 443–449, 734–741, 896–904 and 1068–1076 are the five white-flash cuts.
