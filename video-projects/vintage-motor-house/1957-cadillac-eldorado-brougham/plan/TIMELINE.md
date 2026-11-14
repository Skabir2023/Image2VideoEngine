# Eldorado Brougham — timeline

1200 frames at 60 fps = 20.000 s. Voice starts at 2.40; every word time in the table is
the transcript stamp + 2.40. Cuts land on the pause just before the next phrase. The last
2.65 s carry the end card and one spoken question over the engine.

| Scene | In | Out | Frames | Spoken over it |
|---|---|---|---|---|
| s01-hero | 0.000 | 5.900 | 354 | engine start (silent), then "Seven hundred and four. That's how many Cadillac built," 2.49–5.82 |
| s02-side | 5.900 | 7.483 | 95 | "and every one was finished by hand" 5.97–7.45 |
| s03-rear | 7.483 | 9.050 | 94 | "a brushed stainless roof" 7.52–9.04 |
| s04-engine | 9.050 | 9.600 | 33 | — (a 0.55 s insert: the bay alone, no type) |
| s05-interior | 9.600 | 12.433 | 170 | "a vanity set with six magnetic cups in the glovebox" 9.13–12.12 |
| s06-wheel | 12.433 | 17.350 | 295 | "and then they asked thirteen thousand, seventy four dollars. More than a Rolls-Royce." 12.44–17.20 |
| s07-close | 17.350 | 20.000 | 159 | "Roof, or glove box, which would you keep?" 17.77–19.74, over the revs |

Cuts: 5.900 · 7.483 · 9.050 · 9.600 · 12.433 · 17.350

## Type timing inside the scenes (film time)

| Scene | Element | In |
|---|---|---|
| s01 | kicker 1957 · CADILLAC | 0.55 |
| s01 | 704 (counts up from 0) | 2.25, number lands at 3.40 |
| s01 | EVER BUILT | 4.30 |
| s01 | rule + ELDORADO BROUGHAM | 5.10 / 5.16 |
| s02 | EVERY ONE | 6.00 |
| s02 | BY HAND | 6.65 |
| s03 | STAINLESS | 7.60 |
| s03 | STEEL | 8.00 |
| s03 | rule + BRUSHED, NOT PAINTED | 8.40 / 8.46 |
| s04 | *nothing — 0.55 s of the bay, no type* | |
| s05 | VANITY SET | 9.74 |
| s05 | SIX CUPS | 10.06 |
| s05 | rule + MAGNETIC, SO THEY STAY PUT | 10.62 / 10.70 |
| s06 | $13,074 | 13.28 |
| s06 | MORE THAN A ROLLS-ROYCE | 15.83 |
| s06 | rule + 1957 LIST PRICE | 16.18 / 16.24 |
| s07 | kicker VINTAGE MOTOR HOUSE | 17.40 |
| s07 | ELDORADO | 17.49 |
| s07 | BROUGHAM | 17.63 |
| s07 | THE ROOF, OR THE GLOVEBOX? | 17.74 |
| s07 | TELL US IN THE COMMENTS | 18.55 |
| s07 | fade to black | 19.40 – 20.00 |

The question comes up with the first spoken word, the action line with "which", and the
fade lands on the last word — the engine plays out under the black.

## Furniture that never stops

Every scene carries the same thin layer, phase-locked to the film clock so it runs
across the cuts instead of restarting:

- a 3 px red progress rail along the bottom that fills over the full 20 s;
- a soft light pass crossing the frame every 2.6 s;
- sixteen dust motes per scene, seeded, drifting up 70–220 px.

The right edge carries nothing: no tick ladder, no scene counter.

On top of that every plate is moved by the BROLL camera (push, truck, orbit, pull), so
the frame is never a still.

## Audio

- Engine recording: `engine-start-idle-rev_nhumphrey_pixabay-33510.mp3`, played in full 0 – 8.60 s,
  then its idle section (3.10 – 8.60) looped with 0.50 s equal-power crossfades to 17.10 s.
- At 17.10 the idle hands over — 0.35 s equal-power crossfade — to the throttle run at the
  end of the same recording (source 34.20 – 37.90), so the close is the car revving.
- The ask (`cta/cta-01-v120.wav`, 2.30 s) comes in at 17.72 and runs to 19.74, +1.5 dB so
  it carries. The roar is **not** dipped for it: the close runs at full throttle
  17.35 – 19.80 and the question is mixed on top. Measured, that works — the recording
  lives in 60 – 400 Hz (its 400 – 900 band is 21 dB down) and in 1.5 – 4 kHz it sits
  about 30 dB under the voice, so the words have the band to themselves.
- The idle bed is sidechain-ducked by the voice (threshold 0.020, ratio 12, attack 18 ms,
  release 450 ms), engine gain 0.94, low-pass 2.6 kHz so it never fights the read. The
  first 2.25 s carry a further ×1.28 lift, released over 0.45 s, so the start is heard
  before anyone speaks. The closing roar runs full band (7.2 kHz) with +5 dB at 70 Hz and
  fades over its last 0.20 s.
- Master: −14.2 LUFS integrated, true peak −2.6 dBFS.
