# Script — 1977 Oldsmobile Cutlass Supreme

**1977 Oldsmobile Cutlass Supreme - The Best-Seller That Hid A Chevrolet** · Secret Story · 53 words

## The read, as one paragraph

In 1977, America's best-seller hid a Chevrolet — they paid for a Rocket 350, and the mechanics found a Chevy; the fan belt didn't fit. General Motors painted every engine blue, so nobody could tell. Four years later, fourteen thousand owners got paid, five hundred fifty dollars each — would you have looked at yours?

One chain, not a fact list. The first clause is a claim that sounds impossible, the second says what
was promised, and the semicolon after "a Chevy" is the hinge of the whole film: the discovery and
the proof you can hold — a belt that would not fit — are one thought, not two. That forces the
question of how nobody noticed, which is the blue paint, and "so nobody could tell" answers it in
the same breath. Then the consequence, and the question turns on the viewer: you own one, would you
have known? Delete any clause and the next loses its reason.

**Punctuation is the performance.** Kokoro takes all of its pacing from punctuation and nothing
else (see the `kokoro-natural` skill), so a full stop is a 0.4–0.6 s hole with a full intonation
reset — nine of them in a row is what made the first take read, stop, read, stop. This read keeps
**two** stops: one after "didn't fit" and one after "could tell". Every other boundary is a comma,
a semicolon or a dash, which Kokoro reads as a breath that keeps the sentence alive. The numbers
are written the way they are said — "fourteen thousand", "five hundred fifty dollars" — instead
of digits and a `$` the model has to guess at.

The take is still one unbroken call of the whole paragraph, and it goes through
`tools/voice_trim.py` before the mix: every internal pause is capped at 0.22 s, so what is left is
breath, not dead air. On this read the tool capped ten pauses of 0.30–0.65 s and the take went from
20.661 s to 18.601 s, its longest pause 0.210 s. The cuts land in those breaths, ~65 ms before the
next word; that is why the clause boundaries are written in.

Word count: **53**. Every number is sourced in `FACTCHECK.md`: 1977, the Rocket 350, 550 dollars,
14,000 owners, four years. Nothing invented.

## Beats

- **HOOK** — "In 1977, America's best-seller hid a Chevrolet — they paid for a Rocket 350" · the shock is the object: the most ordinary car in the country, not a supercar.
- **SETUP** — "…and the mechanics found a Chevy" · what was actually sold, and what was actually there, in one clause.
- **TURN** — "; the fan belt didn't fit." · the discovery, told as a physical detail instead of an accusation.
- **REVELATION** — "General Motors painted every engine blue, so nobody could tell." · the cover-up and the reason it worked, in one breath.
- **ENDING** — "Four years later, fourteen thousand owners got paid, five hundred fifty dollars each — would you have looked at yours?" · the verdict, then the question that puts the viewer under the hood.

## Cards

Scene 1 carries the title over the engine start: kicker `1977 · OLDSMOBILE CUTLASS`, then
**AMERICA'S / BEST-SELLER** as the hook lands. The two numbers that carry the proof are counted,
never flat: `14,000` rolls from 14.50 and locks 15.40, `$550` rolls from 16.45 and locks 17.15 on
"each". The 350 stays in the voice — its scene ends 0.8 s after the word — and the card carries
`A ROCKET` instead of digits, so no figure is ever printed flat.

The red second line carries the meaning, scene by scene: `BEST-SELLER`, `CHEVY`, `A ROCKET`,
`CHEVY`, `DIDN'T FIT`, `ENGINE BLUE`, `COULD TELL`, `OWNERS`, `EACH`, and the film closes on
`WOULD YOU / HAVE LOOKED?` under the roar.

## Caption

**1977 Oldsmobile Cutlass Supreme - The Best-Seller That Hid A Chevrolet**

Oldsmobile sold 632,742 Cutlasses in 1977, the best-selling car in America, and some of them left the factory with a Chevrolet V8 instead of the Rocket V8 on the order sheet. A Chicago mechanic found one in March 1977, when the Oldsmobile fan belt would not fit. GM had painted every division's engine the same blue that year. Four years later, a federal jury ordered $550 for each of 14,000 owners. Would you have checked yours?

 #Oldsmobile #ClassicCars #CutlassSupreme #1977 #VintageMotorHouse

Caption score **91**/100 (gate 80): hook shock 22/25, relatability 19/20, curiosity gap 19/20,
shareability 14/15, visual wow 17/20.

Title = 10 words: year + make + model + the claim, in the tease shape. Grounding test: "the
best-seller that hid a Chevrolet" cannot sit on any other car's post — 632,742 and the engine swap
are this car's alone.

Description = 5 sentences, 76 words, second person, gives the three details the voice leaves out
(632,742; the March 1977 discovery; the blue paint) and closes on the question the film opens.

Hashtags = 5: brand, classic-car, model, year, page.

## Voice

Kokoro `am_michael`, speed 1.2 in the request, one take, no `atempo`, then `tools/voice_trim.py`.
The word times are measured on the refined take and re-anchored to its speech blocks — whisper alone
drifted up to 0.35 s here — then copied into `scenes.py` and used by `audio/build_final.py` for the
duck. Raw whisper output is kept as `transcript-whisper.json`; the old nine-stop take is kept as
`line-01-raw-stops.wav`.
