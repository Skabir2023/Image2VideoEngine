# Beats — 9 shots, cut to the voice

Film: 1128 frames = 18.800 s at 60 fps. The first second is the engine start, alone; the last
word ("legend?") ends at 16.51 s; the roar answers at 16.60 s and the tail fades at 18.80 s.

Every cut lands inside a measured silence, 20–120 ms before the word that opens the next
shot, so the picture changes in the pause and never on top of a word. Card times in
`scenes.py` are absolute film times, converted per scene by the builder.

| # | Scene | Start | Frames | Spoken in this shot | On screen |
| --- | --- | --- | --- | --- | --- |
| 1 | `s01-hero` | 0.000 | 150 | "Mercedes built a race car," | Front ¾, doors shut. **Engine start, alone, 0.00–1.00 s.** Push + truck right, light leak. Kicker `1954 · MERCEDES 300SL`, then **RACE CAR** |
| 2 | `s02-side` | 2.500 | 132 | "whose frame was too high to climb over," | Side profile. Truck right + push. **FRAME** / **TOO HIGH** (red) |
| 3 | `s03-rear` | 4.700 | 86 | "so the doors went up." | Rear ¾. Pull + truck left. **DOORS** / **WENT UP** (red) |
| 4 | `s04-star` | 6.133 | 180 | "They built only 1,400 of them." | Star badge macro. Push, then crane down. **1,400** counts up, then `COUPES BUILT` |
| 5 | `s05-engine` | 9.133 | 89 | "That body still hit" | Engine bay. Push. Kicker `THAT BODY` |
| 6 | `s06-wheel` | 10.617 | 128 | "161 miles per hour," | Wheel close. Orbit right. **161** counts up, then `MILES PER HOUR` |
| 7 | `s07-injection` | 12.750 | 144 | "because fuel went straight into the cylinder." | Engine detail. Push, then truck left. Kicker `BECAUSE`, **FUEL** / **STRAIGHT IN** (red, 148 px) |
| 8 | `s08-gauges` | 15.150 | 85 | "Would you dare drive a legend?" | Gauge cluster, deep scrim. Push. **WOULD YOU** / **DARE?** (red) |
| 9 | `s09-closing` | 16.567 | 134 | — (roar) | Steering wheel. Pull + crane up. **COMMENT** / **BELOW** (red), rule, `1954 MERCEDES 300SL`. Holds alone 1.45 s |

## The chain on screen

The cards are the chain, in order, one idea per shot: race car → frame too high → doors went
up → only 1,400 → 161 → because fuel went straight in → would you dare. No shot restates the
one before it, and no shot introduces a fact the sentence before it did not set up.

## Numbers law

Two figures are counted out with `TX.roll`, never printed flat: **1,400** (shot 4, 0.85 s)
and **161** (shot 6, 0.80 s), each starting on its own word with its own seed. The labels
under them — `COUPES BUILT` and `MILES PER HOUR` — arrive after the lock, so the eye reads
the number first.

Shot 4 carries no kicker: grey mono over the gold chrome of the badge does not read, and
the number plus its label already say "1,400 coupes built". The other three kickers
(`THAT BODY`, `BECAUSE`, and shot 1's line) sit on dark parts of their plates.

## Motion

- Every shot carries its own camera move (push, truck, orbit, crane, pull) plus hand-held
  drift; no shot is a static frame.
- Seams are the engine's **blur cut**, one `SEAM.blur(tl, DUR)` call (`assets/seams.js`):
  the outgoing plate defocuses to 18 px over 0.20 s and the incoming one focuses back over
  0.18 s, so the change happens inside the camera move. No white flash, no whip, and the
  type stays sharp through it, like a focus pull.
- Shot 1 has no focus-in and shot 9 no focus-out: frame 0 is the post thumbnail and the
  closing card holds, both sharp.
- The first and last shots add a drifting warm light leak.
- Shakes on the cut into shot 9 and again under its rule.

## Sound

1. **0.00–1.00 s** — engine catching, alone, −20 dBFS RMS, nothing over it. The voice starts
   at exactly 1.00 s.
2. **1.05 → end** — idle bed, −29 dBFS, fading in over 0.8 s; ducked to ×0.10 (−20 dB)
   across every spoken word, smoothed 20 ms / 220 ms. Measured: **−35.6 dB in the pauses,
   −52.4 dB under speech.**
3. **16.60–18.61 s** — one clean rev at rate 0.86, 2.01 s, no voice over it, camera shake on
   the hit; tail faded by 18.80 s.
4. **16.80 s** — one low hit (−33 dB) under the closing card, landing with `COMMENT` and on
   top of the roar. That is the only hit in the film.

Nothing else. No whoosh on any seam, no hit under a number, no music: the voice, the engine
start, the bed, the roar, and one hit at the close.
