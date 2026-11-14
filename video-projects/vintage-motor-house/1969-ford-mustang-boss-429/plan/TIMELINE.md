# Boss 429 — timeline (six clips, 18.600 s)

`renders/1969 Ford Mustang Boss 429 - Rarest.mp4` · 18.600 s · 1080×1920 · 60 fps · 1116 frames.

Published 14 Nov 2026, 02:40 UTC (Post No. 1). The name below is the published file.

Everything below is measured, not guessed. The voice is one Kokoro call at
`speed: 1.2` and `audio/paragraph/transcript.json` holds the word-level
timestamps; the cuts and every text beat are placed off those times.

## Picture — 1116 frames, six clips, flash cuts

| # | clip | in | out | frames | camera | still |
|---|---|---|---|---|---|---|
| 01 | `renders/cut/s01-hero.mp4` | 0.000 | 4.267 | 256 | push 1.04→1.14 + truck right 34 | `stills-v2/01_hero_front34` |
| 02 | `renders/cut/s02-engine.mp4` | 4.267 | 9.450 | 311 | push 1.00→1.14 + crane down 24 | `stills-v2/04_engine_bay` |
| 03 | `renders/cut/s03-side.mp4` | 9.450 | 13.083 | 218 | truck right 60 + push 6% | `stills-v2/02_side_profile` |
| 04 | `renders/cut/s04-interior.mp4` | 13.083 | 14.667 | 95 | orbit left 44 | `stills-v2/05_interior_dash` |
| 05 | `renders/cut/s05-wheel.mp4` | 14.667 | 16.300 | 98 | orbit right 48 | `stills-v2/06_wheel_close` |
| 06 | `renders/cut/s06-rear.mp4` | 16.300 | 18.600 | 138 | push 1.02→1.09 | `stills-v2/03_rear34` |

Seams: 0.20 s flash-out on the outgoing clip, 0.16 s flash-in on the incoming
clip. No flash on frame 0, no flash on the final frame.

**Each cut lands ~65 ms before the first word of the next line**, so the picture
changes in the pause before the word, never on top of it.

## Voice

Kokoro `am_michael`, one call, one paragraph, `speed: 1.2` → 17.138 s
(`audio/paragraph/line-01-v120.wav`). The speed lives in the request, so the
pauses shrink with the read — no `atempo`, no pause squeezing, nothing to make
it sound machine-read.

Placed at 0.30 s, so speech runs 0.35 – 17.18 s and the closing card holds the
last 1.42 s alone, with the final rev answering the question.

| spoken line | in | out |
|---|---|---|
| 1969, Ford needs a NASCAR V8 on the street | 0.35 | 4.33 |
| so they drop in a 429 | 4.33 | 5.21 |
| Seven liters of hand-built big block | 6.99 | 9.52 |
| only 1,359 were ever made | 9.52 | 13.03 |
| Detuned so you could buy one | 13.15 | 14.74 |
| one year only, then gone | 14.74 | 16.38 |
| would you drive it? | 16.38 | 17.18 |

## Text — every reveal sits on the word

| # | text | lands on | at |
|---|---|---|---|
| 01 | `1969 · FORD MUSTANG` | "1969" | 0.35 |
| 01 | BOSS / 429 | the year clearing | 0.52 / 0.68 |
| 01 | NASCAR HOMOLOGATION | "NASCAR" | 2.63 |
| 02 | 429 | the number | 5.19 |
| 02 | 7.0 LITRE · HAND-BUILT V8 | "Seven liters" | 6.97 |
| 03 | 1,359 | "1,359" | 9.95 |
| 03 | 1969 ONLY | "made" | 11.87 |
| 04 | DETUNED TO SELL | "Detuned" | 13.44 |
| 04 | STREET LEGAL | "buy" | 14.22 |
| 05 | ONE YEAR ONLY | "one year" | 15.03 |
| 05 | 1969 · THEN GONE | "then" | 15.59 |
| 06 | WOULD YOU DRIVE IT? | "would" | 16.68 |

The old cut changed the "1,359" card at 12.24 s while the voice was still in the
middle of "made" — that was the sync fault. The number now owns the shot from
9.95 s to 13.08 s, which is exactly how long it takes to say it.

## Sound

- bed: the **big-block V8** (`big-block-v8-rev_henaway_pixabay-90919.mp3`) is the
  only engine in the film. Its sustained 0.45–1.55 s section is looped with a
  0.30 s equal-power crossfade so it runs 18.6 s without a seam, then lowpassed to
  1.2 kHz and compressed flat into a deep, distant idle instead of a revving roar
- **the bed is quiet and gets out of the way**: −27.8 dB in the pauses, −48.6 dB
  while he is speaking (32 dB under the voice), because the sidechain is set hard
  (threshold 0.018, ratio 16, 12 ms attack, 260 ms release). The engine is heard
  between lines and is effectively absent behind a word
- **no revs under speech.** The old cut put a rev under "429" and another under
  "1,359" — the exact lines the reel exists to land — and it swallowed them. Both
  are gone
- one real rev, at 17.10 s, after the last word: the car answers "Would you drive
  it?" and rings through the closing hold at level 0.92
- 0.30 s engine fade-up under the opening line, 0.10 s fade-out at the tail
- no low hits, no whooshes — removed on request
- master −14.2 LUFS, true peak −2.4 dBFS; the speech section alone measures
  −14.2 LUFS, so the voice is Shorts-loud on its own

Both engine files live in `sound/engines/` with their licence and source in
`sound/README.md`, so this project carries its own audio.

## Build order

`npm run render` runs all five steps below in one go.
1. `python3 audio/build_final.py` (place voice, looped big-block bed ducked by the voice, the closing rev, master, loudness correction)
2. `python3 tools/build_scenes.py` (writes all six compositions from one table)
3. render each: `npx hyperframes render -c compositions/<s>.html -o renders/cut/<s>.mp4 --fps 60 --quality high --video-frame-format png`
4. `ffmpeg -f concat -safe 0 -i renders/cut/concat.txt -c copy renders/cut/picture.mp4`
5. `ffmpeg -i renders/cut/picture.mp4 -i audio/final-audio.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "renders/1969 Ford Mustang Boss 429 - Rarest.mp4"`

Frame counts are exact per clip (256+311+218+95+98+138 = 1116), so the concat
stays frame-accurate at 60 fps.
