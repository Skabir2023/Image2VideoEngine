# Timeline — The 1978 BMW M1 That Missed Its Own Race

Measured from the rendered film `renders/The 1978 BMW M1 That Missed Its Own Race.mp4`
(1080×1920, 60 fps, 1800 frames = 30.000 s) and the mixed master `audio/final-audio.wav`.

## Voice (clock)
- Engine: Kokoro `am_adam`, speed **1.30** (1.20 read 0.34 s/word on this syllable-heavy text and would swallow the roar; 1.30 → 25.39 s speech).
- Source: `audio/paragraph/line-01-v120.wav` (25.663 s, 80 words). Word times: `audio/paragraph/transcript.json`.
- Placement: `LEAD = 1.00 s` (engine catch alone before the first word). All scene/word times below are absolute film time (transcript + LEAD).
- Last word **"was."** ends **26.24 s** (25.24 s in WAV). Roar starts **26.48 s**, 0.10 s clear of speech.

## Cuts and scenes (blur-seam, on measured pauses — never on a word)
Cuts placed from audio silencedetect (−32 dB / 0.12 s). 16 shots, ~1.9 s cadence.

| # | Scene | Start | End | Dur | Frames | Cumulative frame | Plate |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | s01-hero | 0.000 | 2.967 | 2.967 | 178 | 0–177 | 01_hero_front34 |
| 2 | s02-side | 2.967 | 5.133 | 2.167 | 130 | 178–307 | 02_side |
| 3 | s03-rear | 5.133 | 7.333 | 2.200 | 132 | 308–439 | 03_rear34 |
| 4 | s04-engine | 7.333 | 8.883 | 1.550 | 93 | 440–532 | 04_engine |
| 5 | s05-interior | 8.883 | 10.433 | 1.550 | 93 | 533–625 | 05_interior |
| 6 | s06-wheel | 10.433 | 11.733 | 1.300 | 78 | 626–703 | 06_wheel |
| 7 | s07-roundel-front | 11.733 | 13.217 | 1.483 | 89 | 704–792 | 07_roundel_front |
| 8 | s08-roundel-rear | 13.217 | 14.217 | 1.000 | 60 | 793–852 | 08_roundel_rear |
| 9 | s09-headlight | 14.217 | 15.200 | 0.983 | 59 | 853–911 | 09_headlight |
| 10 | s10-steering | 15.200 | 16.233 | 1.033 | 62 | 912–973 | 10_steering |
| 11 | s11-exhaust | 16.233 | 18.700 | 2.467 | 148 | 974–1121 | 11_exhaust |
| 12 | s12-louvres | 18.700 | 20.750 | 2.050 | 123 | 1122–1244 | 12_louvres |
| 13 | s13-mirror | 20.750 | 24.133 | 3.383 | 203 | 1245–1447 | 13_mirror |
| 14 | s14-intake | 24.133 | 25.417 | 1.283 | 77 | 1448–1524 | 14_intake |
| 15 | s15-night | 25.417 | 28.400 | 2.983 | 179 | 1525–1703 | 16_night_hero |
| 16 | s16-tail | 28.400 | 30.000 | 1.600 | 96 | 1704–1799 | 15_taillight |

**Total:** 178+130+132+93+93+78+89+60+59+62+148+123+203+77+179+96 = **1800 frames = 30.000 s**.
Hard jumps (scan) only at seam frames 178, 308, 440, 533, 626, 704, 793, 853, 912, 974, 1122, 1245, 1448, 1525, 1704.

Notes: s13 carries "They built 453. Then made a series…" so **453** rolls (21.24, 0.85 s) and locks with its "BUILT" label on screen (label 21.80, rule 23.30). s15 is the closing card and holds under the roar (shake at 26.48). s16 is the tail lamp as the roar decays; frame 0 and the last frame stay sharp (no blur-in on s01, no blur-out on s16).

## Rolled figures (TX.roll, on the word)
- 400 at 5.62 s (0.85 s) — "ROAD CARS TO QUALIFY"
- 7 at 10.65 s (0.78 s) — "SEVEN PROTOTYPES"
- 277 at 17.50 s (0.85 s) — "HORSEPOWER"
- 160 at 18.89 s (0.85 s) — "MILES PER HOUR"
- 453 at 21.24 s (0.85 s) — "BUILT"

## Audio mix (measured, `audio/build_final.py`)
- Start (engine catch, `START_SLICE` 0.10–2.60, `START_RMS_DB` −18, hold 0.90 s, settle 1.45 s): loud and alone 0.00–1.00, settles under narrator.
- Bed (idle `BED_SLICE` 14.00–16.00, loop xfade 0.30 s, `BED_RMS_DB` −19, fade in 1.00–1.70, out tail 0.40 s): present 1.00–30.00, ducked from transcript word spans (80 spans, floor 0.100 / −20 dB, attack 20 ms, release 220 ms). Measured: **−25.3 dB in pauses, −42.3 dB under speech** (17.1 dB of duck) on the bed track.
- Roar (`ROAR_SLICE` 27.72–29.45, rate 0.86 → 2.01 s, `ROAR_RMS_DB` −15.5, gain ×1.12): **26.48–28.49 s**, after "was." ends 26.38, with s15 camera shake at 26.48.
- Master: **−14.2 LUFS integrated, −2.0 dBFS true peak**, 30.000 s (speech-loudness check and ebur128 peak).

## QA
- `npm run lint` → 0 errors, 0 warnings.
- `npm run check` → `frame0_blank: false` (std 39.82), `black_frames: []`, `one_frame_pops: []`, hard jumps only at the 15 seams above.
- Contact sheet: `qa/final-sheet.jpg`. Seam frames: `qa/seams-check.jpg`.
