# Boss 429 — script (six full-bleed car clips, one continuous read)

Subject: 1969 Ford Mustang Boss 429. Vertical 9:16, **18.600 s**, 60 fps, 1116 frames.

The read sets the length. Faster delivery for a Short: `speed: 1.2` in the Kokoro
request itself (17.138 s), plus a 1.42 s hold on the closing card.

## Voiceover

One paragraph, one call: Kokoro `am_michael`, **speed 1.2**. 41 words.

> 1969, Ford needs a NASCAR V8 on the street, so they drop in a 429. Seven liters
> of hand-built big block. Only 1,359 were ever made. Detuned so you could buy
> one. One year only, then gone. Would you drive it?

## How the speed and the sync were handled

1. The whole paragraph is one Kokoro call (`audio/paragraph/line-01-v120.wav`).
   Speed is requested from the model, so the pauses tighten with the words —
   no `atempo`, no resampling, nothing that makes a read sound machined.
2. `npx hyperframes transcribe` gives word-level timings
   (`audio/paragraph/transcript.json`). Every cut and every text beat is placed
   off those times instead of being guessed from silence detection.
3. A cut lands ~65 ms **before** the first word of the next line, so the picture
   changes in the pause and the text arrives with the word.
4. The voice sits 0.30 s in; speech runs 0.35 – 17.18 s; the closing card holds
   the last 1.42 s with the final rev.

The old cut changed the "1,359" card at 12.24 s while the voice was still in
"made" — the number takes 1.5 s to say, and the card was leaving early. It now
owns the shot from 9.95 s to 13.08 s.

## Clips and on-screen text

| # | time | still | text | narration over it |
|---|---|---|---|---|
| 01 hero | 0.00–4.27 | 01 hero front 3/4 | 1969 · FORD MUSTANG / BOSS **429** / NASCAR HOMOLOGATION | "1969, Ford needs a NASCAR V8 on the street" |
| 02 engine | 4.27–9.45 | 04 engine bay | **429** CUBIC INCHES / 7.0 LITRE · HAND-BUILT V8 | "so they drop in a 429. Seven liters of hand-built big block." |
| 03 side | 9.45–13.08 | 02 side profile | **1,359** EVER BUILT / 1969 ONLY | "only 1,359 were ever made" |
| 04 interior | 13.08–14.67 | 05 interior dash | **DETUNED** TO SELL / STREET LEGAL | "Detuned so you could buy one" |
| 05 wheel | 14.67–16.30 | 06 wheel close | ONE YEAR **ONLY** / 1969 · THEN GONE | "one year only, then gone" |
| 06 rear | 16.30–18.60 | 03 rear 3/4 | WOULD YOU **DRIVE IT?** / BOSS 429 | "would you drive it?" |

All six stills are native 9:16 (1080×1920), used once, full-bleed, camera pushing
or trucking on every clip, stitched with a white flash cut.

The plates are a single car in one place on one grey winter day: front three
quarter, side profile, rear three quarter, engine bay, cabin from the passenger
seat, wheel. No open doors — an open door kept hinging the wrong way, so the
cabin is shot from inside instead.

## Sound

Narration over the big-block V8 itself, kept deliberately quiet: its sustained
section is looped into a steady, distant idle, heard in the pauses and ducked 32 dB
under the words so nothing ever roars over the line. Nothing plays under the
important sentences. The one real rev comes after the last word, where the car
answers "would you drive it?" and rings into the closing hold. No whooshes, no
synthetic hits. It is a generic V8, not a Boss 429 — see TIMELINE.md.

## Facebook caption

The Rarest 1969 Ford Mustang Boss 429 Ever Made
They only built 1,359 of these. And it carried a 429 cubic-inch V8 meant for the track.
#Ford #Mustang #ClassicCars #Boss429 #1969

Published 14 Nov 2026, 02:40 UTC, Post No. 1 — the caption above is what went out, unchanged.
The row sits in `uploaded.csv` as `published`; the film is
`renders/1969 Ford Mustang Boss 429 - Rarest.mp4`.

## Facts kept in check

1969 Boss 429 · 429 cu in (7.0 L) V8 · 1,359 built · NASCAR homologation special ·
one model year only. No horsepower figure is claimed anywhere.
