# TIMELINE — 1977 Oldsmobile Cutlass Supreme

The measured numbers of this build. Voice: one Kokoro `am_michael` take at speed 1.2, 53 words,
**18.601 s** after `tools/voice_trim.py` capped every internal pause at 0.22 s (longest surviving
pause 0.210 s). `LEAD = 1.00 s`, ten scenes, **1292 frames = 21.533 s at 60 fps**, closing roar
19.44 → 21.44.

The read was rewritten for this take: two full stops instead of nine, the rest commas, a semicolon
and dashes, and the numbers spelled as they are said. The old take read, stopped, read, stopped —
ten pauses of 0.32–0.60 s. The refined take reads as one chain, and the cuts now sit in 0.21 s
breaths instead of holes.

## Cuts

| Scene | Starts | Frames | Seconds | Still | Card |
| --- | --- | --- | --- | --- | --- |
| s01-hero | 0.000 | 144 | 2.400 | `01_hero_front34.png` | AMERICA'S / BEST-SELLER |
| s02-side | 2.400 | 128 | 2.133 | `02_side.png` | HID A / CHEVY |
| s03-rear | 4.533 | 143 | 2.383 | `03_rear.png` | PAID FOR / A ROCKET |
| s04-engine | 6.917 | 93 | 1.550 | `04_engine.png` | FOUND A / CHEVY |
| s05-belt | 8.467 | 80 | 1.333 | `06_wheel.png` | FAN BELT / DIDN'T FIT |
| s06-valvecover | 9.800 | 146 | 2.433 | `07_blue_valvecover.png` | EVERY / ENGINE BLUE |
| s07-interior | 12.233 | 74 | 1.233 | `05_interior.png` | NOBODY / COULD TELL |
| s08-gauge | 13.467 | 175 | 2.917 | `08_gauges.png` | 14,000 / OWNERS |
| s09-grille | 16.383 | 172 | 2.867 | `09_grille.png` | $550 / EACH |
| s10-tail | 19.250 | 137 | 2.283 | `10_taillight.png` | WOULD YOU / HAVE LOOKED? then the roar |

Frame boundaries: 144 · 272 · 415 · 508 · 588 · 734 · 808 · 983 · 1155 · 1292 — every
`hard_jumps` frame reported by `tools/scan.py` (144, 272, 415, 508, 588, 734, 808, 983, 1155) is one
of these nine seams, and none is anywhere else.

## Word times

Measured on the refined take and re-anchored to its speech blocks; voice time is picture time
**− 1.00 s**. The rolls are seeded and lock on the spoken word: `14,000` starts 14.50 and locks
15.40, just before "owners"; `$550` starts 16.45 and locks 17.15, on "each".

| Word | Voice | Picture | | Word | Voice | Picture |
| --- | --- | --- | --- | --- | --- | --- |
| In | 0.000 | 1.000 | | General | 8.870 | 9.870 |
| 1977 | 0.118 | 1.118 | | Motors | 9.243 | 10.243 |
| America's | 1.470 | 2.470 | | painted | 9.597 | 10.597 |
| best-seller | 1.901 | 2.901 | | every | 10.175 | 11.175 |
| hid | 2.489 | 3.489 | | engine | 10.315 | 11.315 |
| a | 2.691 | 3.691 | | blue | 10.688 | 11.688 |
| Chevrolet | 2.755 | 3.755 | | so | 11.290 | 12.290 |
| They | 3.590 | 4.590 | | nobody | 11.353 | 12.353 |
| paid | 3.916 | 4.916 | | could | 11.665 | 12.665 |
| for | 4.253 | 5.253 | | tell | 11.934 | 12.934 |
| a | 4.518 | 5.518 | | Four | 12.520 | 13.520 |
| Rocket | 4.720 | 5.720 | | years | 12.680 | 13.680 |
| 350 | 5.103 | 6.103 | | later | 12.934 | 13.934 |
| and | 5.980 | 6.980 | | 14,000 | 13.500 | 14.500 |
| the | 6.098 | 7.098 | | owners | 14.413 | 15.413 |
| mechanics | 6.199 | 7.199 | | got | 14.682 | 15.682 |
| found | 6.563 | 7.563 | | paid | 14.839 | 15.839 |
| a | 6.818 | 7.818 | | $550 | 15.450 | 16.450 |
| Chevy | 6.982 | 7.982 | | each | 16.138 | 17.138 |
| The | 7.530 | 8.530 | | would | 16.580 | 17.580 |
| fan | 7.669 | 8.669 | | you | 17.170 | 18.170 |
| belt | 7.873 | 8.873 | | have | 17.360 | 18.360 |
| didn't | 8.240 | 9.240 | | looked | 17.622 | 18.622 |
| fit | 8.560 | 9.560 | | at | 18.011 | 19.011 |
| | | | | yours | 18.320 | 19.320 |

Every cut lands inside a measured pause, 57–70 ms before the next word:

| Cut | Pause | Next word |
| --- | --- | --- |
| 2.400 | 2.250 – 2.470 | America's 2.470 |
| 4.533 | 4.370 – 4.590 | They 4.590 |
| 6.917 | 6.760 – 6.980 | and 6.980 |
| 8.467 | 8.310 – 8.530 | The 8.530 |
| 9.800 | 9.650 – 9.870 | General 9.870 |
| 12.233 | 12.080 – 12.290 | so 12.290 |
| 13.467 | 13.300 – 13.520 | Four 13.520 |
| 16.383 | 16.230 – 16.450 | $550 16.450 |
| 19.250 | 19.120 – 19.320 | yours 19.320 |

The pauses at 14.28 (after "later,") and 17.95 (after "would") are deliberately not cut: the first
would leave a 1 s scene, the second would put the money and the question in one shot.

## Sound

Built by `audio/build_final.py`, measured on the master:

| Part | Setting | Measured |
| --- | --- | --- |
| Start | 0.10–1.60 of `engine-start-idle-rev`, levelled to −20 dBFS RMS | alone for the first 1.00 s |
| Bed | `0.45–1.55 s` of `big-block-v8-rev`, looped, 0.30 s crossfade, HP 42 Hz / LP 2.2 kHz | −36.4 dB in pauses, −50.5 dB under speech |
| Duck | 0.100 on every spoken word, 20 ms attack / 220 ms release | 14 dB+ below the voice |
| Roar | 0.55–2.55 at rate 1.00 → 2.00 s | 19.44 → 21.44, no voice over it |
| Thump | one low hit at 19.46, under the closing card | only hit in the film |
| Master | — | **−14.3 LUFS**, true peak **−3.7 dBTP** |

The bed is written 0.03 s longer than the picture (`TAIL`): `render-all.sh` muxes with `-shortest`,
and an audio bed of exactly 1292 frames silently drops the closing frame.

## Gates

`npm run lint` 0 errors / 0 warnings · `tools/scan.py` `frame0_blank: false`, `black_frames: []`,
`one_frame_pops: []`, nine hard jumps all on seams · `tools/score.py` 93/100, 53 words, 10 distinct
stills for 21.5 s (needs 8), longest still 2.92 s, caption 91/100 · render
`1977 Oldsmobile Cutlass Supreme - The Best-Seller That Hid A Chevrolet.mp4`, 1292 frames.
